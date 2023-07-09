import asyncio
import json
import logging
import pickle
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database
from pymongo.errors import (AutoReconnect, NetworkTimeout,
                            ServerSelectionTimeoutError)
from web3.auto import Web3
from web3.beacon import Beacon
from web3.exceptions import TransactionNotFound

from censorability_monitor.analytics.fetch import (get_addresses_from_receipt,
                                                   load_mempool_state)
from censorability_monitor.analytics.validators import (get_validator_info,
                                                        get_validator_pubkey)
from censorability_monitor.data_collection.ofac import (
    get_banned_wallets, get_grouped_by_prefixes)


class CensorshipMonitor:
    ''' Monitor non included into block transactions'''
    def __init__(self, mongo_url: str, mongo_analytics_url: str,
                 collector_db_name: str,
                 analytics_db_name: str,
                 web3_type: str, web3_url: str,
                 beacon_url: str,
                 model_path: str,
                 interval: float, verbose: bool, start_block: int = 0,
                 name: str = 'CensorshipMonitor',
                 classifier_dataset_path: Optional[Path] = None):
        self.mongo_url = mongo_url
        self.mongo_analytics_url = mongo_analytics_url
        self.collector_db_name = collector_db_name
        self.analytics_db_name = analytics_db_name
        self.web3_type = web3_type
        self.web3_url = web3_url
        self.interval = interval
        self.verbose = verbose
        self.name = name
        self.start_block = start_block
        self.beacon_url = beacon_url
        self.ofac_cache = None
        self.classifier_dataset_path = classifier_dataset_path
        if self.classifier_dataset_path is not None:
            self.classifier_dataset_path.mkdir(parents=True, exist_ok=True)
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def get_mongo_client(self):
        return MongoClient(self.mongo_url)

    def get_mongo_analytics_client(self):
        return MongoClient(self.mongo_analytics_url)

    def get_web3_client(self):
        logger = logging.getLogger(self.name)
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            # logger.info(f'Connected to ETH node: {w3.isConnected()}')
            return w3
        if self.web3_type == 'http':
            w3 = Web3(Web3.HTTPProvider(self.web3_url))
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            logger.error(msg)
            raise Exception(msg)

    def get_beacon(self):
        beacon = Beacon(self.beacon_url)
        return beacon

    def get_last_processed_block_number(self, db: Database) -> int:
        ''' Get number of last processed block (if restarted)'''
        processed_blocks = db['processed_blocks']
        last_processed_block_query = processed_blocks.find().sort(
                'block_number', -1).limit(1)
        try:
            last_processed = next(last_processed_block_query)
            return last_processed['block_number']
        except StopIteration:
            return 0

    async def get_first_ready_block_number(self, db: Database) -> int:
        ''' Get number of the first block which is ready to analysis'''
        data_collected_blocks = db['processed_blocks']
        all_ready_blocks = data_collected_blocks.count_documents(
                {'block_gas_estimated': {'$exists': True}})
        # Wait for the first block to be ready for analysis
        while all_ready_blocks == 0:
            all_ready_blocks = data_collected_blocks.count_documents(
                {'block_gas_estimated': {'$exists': True}})
            await asyncio.sleep(1)
        first_ready_block_query = data_collected_blocks.find(
            {'block_gas_estimated': {'$exists': True}}
        ).sort('block_gas_estimated', 1).limit(1)
        return next(first_ready_block_query)['block_gas_estimated']

    async def get_last_ready_block_number(self, db: Database) -> int:
        ''' Get number of the last block which is ready to analysis'''
        data_collected_blocks = db['processed_blocks']
        all_ready_blocks = data_collected_blocks.count_documents(
                {'block_gas_estimated': {'$exists': True}})
        # Wait for the first block to be ready for analysis
        while all_ready_blocks == 0:
            all_ready_blocks = data_collected_blocks.count_documents(
                {'block_gas_estimated': {'$exists': True}})
            await asyncio.sleep(1)
        last_ready_block_query = data_collected_blocks.find(
            {'block_gas_estimated': {'$exists': True}}
        ).sort('block_gas_estimated', -1).limit(1)
        return next(last_ready_block_query)['block_gas_estimated']

    async def run(self):
        logger = logging.getLogger(self.name)
        mongo_client = self.get_mongo_client()
        mongo_analytics_client = self.get_mongo_analytics_client()
        db_collector = mongo_client[self.collector_db_name]
        db_analytics = mongo_analytics_client[self.analytics_db_name]

        logger.info('Select starting block')
        last_processed_block = self.get_last_processed_block_number(
            db_analytics)
        logger.info(f'Last processed block: {last_processed_block}')

        first_ready_block = await self.get_first_ready_block_number(
            db_collector)
        logger.info(f'First ready block: {first_ready_block}')

        if self.start_block > 1:
            first_ready_block = max(self.start_block - 1, first_ready_block)
        
        logger.info(f'First ready/start block: {first_ready_block}')

        last_ready_block = await self.get_last_ready_block_number(
            db_collector)
        logger.info(f'Last ready block: {last_ready_block}')

        if last_processed_block > last_ready_block:
            logger.error(('Last processed block is higher than first ready '
                          'block - something is wrong with DB'))
            raise Exception('Check database')

        # Set current block
        current_block = max(first_ready_block, last_processed_block) + 1
        logger.info(f'Starting from block: {current_block}')
        while True:
            while current_block > last_ready_block:
                await asyncio.sleep(1)
                last_ready_block = await self.get_last_ready_block_number(
                    db_collector)
                print(f'Last ready block in loop: {last_ready_block}')
            while current_block <= last_ready_block:
                block_processed = False
                while not block_processed:
                    try:
                        await self.process_block(current_block)
                        block_processed = True
                    except (NetworkTimeout, ServerSelectionTimeoutError):
                        logger.error(('Mongo network error will try process '
                                      f'block {current_block} one more time'))
                        await asyncio.sleep(30)
                current_block += 1

    async def process_block(self, block_number: int):
        ''' Process block (catch exceptions) and save block_number to db'''
        logger = logging.getLogger(self.name)
        w3 = self.get_web3_client()
        n_behind = w3.eth.blockNumber - block_number
        while n_behind < 10:
            logger.info(f"Waiting for block confirmations, now have {n_behind}")
            asyncio.sleep(12)
        logger.info(f'processing {block_number}, {n_behind} behind ETH')
        # Update validators and ofac list
        mongo_client = self.get_mongo_analytics_client()
        db = mongo_client[self.analytics_db_name]
        block = w3.eth.getBlock(block_number)
        block_ts = block['timestamp']
        try:
            self.update_ofac_list_and_validators(block_ts, db)
        except Exception as e:
            logger.error(f'Error during list updates: {type(e)} {e}')
        # Process block
        success = False
        n_attempt = 0
        while not success and n_attempt < 100:
            try:
                await self.process_one_block(block, block_number)
                success = True
            except (AutoReconnect, NetworkTimeout) as e:
                logger.error((f'Error mongo {block_number}: '
                              f'{type(e)} {e} {e.args[0]}'))
                await asyncio.sleep(10)
                n_attempt += 1
            except Exception as e:
                logger.error(f'Error with block {block_number}: {type(e)} {e}')
                raise e
        if n_attempt == 100:
            logger.error(f'More than 100 attempts {block_number}')
            raise Exception()
        # Save block_number to db
        mongo_analytics_client = self.get_mongo_analytics_client()
        db_analytics = mongo_analytics_client[self.analytics_db_name]
        processed_blocks = db_analytics['processed_blocks']
        attempt = 0
        processed_block_saved = False
        while not processed_block_saved:
            try:
                processed_blocks.insert_one(
                    {'block_number': block_number,
                     'success': success})
                processed_block_saved = True
            except (NetworkTimeout, ServerSelectionTimeoutError) as e:
                if attempt > 5:
                    raise e
                attempt += 1
                logger.error((f'Waiting for attempt {attempt + 1} '
                              'to save block status'))
                await asyncio.sleep(30)
                mongo_analytics_client = self.get_mongo_analytics_client()
                db_analytics = mongo_analytics_client[self.analytics_db_name]
                processed_blocks = db_analytics['processed_blocks']

    async def process_one_block(self, block: Dict, block_number: int):
        logger = logging.getLogger(self.name)
        ''' Process block'''
        w3 = self.get_web3_client()
        mongo_client = self.get_mongo_client()
        mongo_analytics_client = self.get_mongo_analytics_client()
        block_ts = block['timestamp']

        # Get validator pool and name
        validator_pool, validator_name = await self.get_validator_full_info(block_number, block_ts)
        # Transactions
        block_txs = [b.hex() for b in block['transactions']]
        db = mongo_client[self.collector_db_name]
        try:
            mempool_txs = load_mempool_state(db, block_number, w3)
        except Exception as e:
            logger.error(f'Mempool error {block_number} {type(e)} {e}')

        # block txs AND mempool txs
        all_transactions = set(block_txs).copy()
        all_transactions.update(mempool_txs)
        logger.info((f'Total txs to process: {len(all_transactions)}'
                     f' (memopool: {len(mempool_txs)})'))
        # txs in block which were not found in mempool
        not_found_in_db_txs = set(block_txs) - set(mempool_txs)
        logger.info(f"not found in mempool txs: {len(not_found_in_db_txs)}")

        block_txs_addresses = await self.get_txs_addresses(block_txs, w3)
        logger.info(f"Got addresses: {len(block_txs_addresses)}")
        # check
        if len(block_txs_addresses) != len(block['transactions']):
            logger.error((f'Block {block_number}: len of block_txs_addresses '
                          'is not equal to number of txs in block'))
        # Second try to find txs in db - we need only first seen ts
        # without mempool constrains
        found_in_db = self.find_txs_in_db(not_found_in_db_txs, db)
        not_found_in_db_txs = not_found_in_db_txs - set(found_in_db)
        logger.info(f"not found in db txs: {len(not_found_in_db_txs)}")

        # Еще осталась часть не найденных not_found_in_db_txs,
        # а также могли быть транзакции без деталей в BD
        all_txs_found_in_db = set(list(mempool_txs) + list(found_in_db))
        txs_details_from_db = self.get_txs_details_from_db(
            all_txs_found_in_db, db)
        txs_details_hashes = set(txs_details_from_db.keys())
        logger.info(f"Found txs in db and mempool: {len(txs_details_hashes)}")
        # Транзакции из БД, для которых нет деталей:
        db_txs_without_details = all_txs_found_in_db - txs_details_hashes
        # Достанем детали из блокчейна для "транзакций, напрямую попавших в
        # блок" и "транзакции, найденные в БД, но без деталей"
        txs_no_details = db_txs_without_details.union(not_found_in_db_txs)
        additional_details = self.get_txs_details_from_w3(txs_no_details, w3)
        logger.info(f"Additional details found {len(additional_details)}")
        # Соберем потребление газа для транзакций
        gas_consumption = self.gather_gas_estimation(
            txs_details=txs_details_from_db,
            additional_details=additional_details,
            block_number=block_number,
            db=db
        )
        if len(all_transactions) != len(gas_consumption):
            logger.info((f'Block {block_number} len gas consumption '
                         f'{len(gas_consumption)} not '
                         f'equal number of all txs {len(all_transactions)}'))

        # Собираем фичи в датафрейм
        logger.info("Creating df")
        df = self.create_txs_dataframe(
            block_ts=block_ts,
            transactions=all_transactions,
            txs_details=txs_details_from_db,
            additional_details=additional_details,
            gas_consumption=gas_consumption,
            db=db
        )
        logger.info("Adding features")
        df = self.add_features_for_classification(
            df=df,
            block_txs=block_txs,
            block=block,
            block_number=block_number,
            not_in_mempool=not_found_in_db_txs
        )
        # Make prediction
        feature_columns = ['availablePriorityFee', 'gas', 'already_waiting',
                           'baseFeePerGas', 'prev_block_gasUsed', 'priority_n',
                           'total_eligible_txs', 'priority_percent',
                           'cumulative_gas', 'first_gas_unit', 'last_gas_unit',
                           'change_baseFeePerGas', 'hour']
        logger.info(f'Txs passed through classifier: {len(df)}')
        classifier_features = df[feature_columns].copy()
        preds = self.model.predict(classifier_features)
        df['prediction'] = preds

        # Compliance status
        db_analytics = mongo_analytics_client[self.analytics_db_name]
        status = self.get_compliance_statuses(
            block_ts=block_ts,
            block_txs_addresses=block_txs_addresses,
            db=db_analytics
        )
        df['status'] = df['hash'].apply(lambda x: status.get(x, 0))

        # Save data for classifier training
        if self.classifier_dataset_path is not None:
            df.to_csv(self.classifier_dataset_path / f'{block_number}.csv',
                      index=False)

        # Calculate and save block metrics
        df_block_txs = df[df['included_into_next_block']].reset_index(
            drop=True).copy()
        df_not_included_txs = df[~df['included_into_next_block']].reset_index(
            drop=True).copy()
        if len(df_block_txs) != len(block['transactions']):
            logger.info((f'N block txes {len(df_block_txs)} is not equal to '
                         f'df block txes {len(block["transactions"])}'))

        dt = datetime.utcfromtimestamp(block_ts)
        block_date = dt.strftime('%d-%m-%y')
        validators_collection = db_analytics['validators_metrics']
        n_compliant_txs = len(df_block_txs[df_block_txs['status'] == 1])
        n_non_compliant_txs = len(df_block_txs) - n_compliant_txs
        logger.info((f'Txs in block: {len(block_txs)} '
                     f'compliant: {n_compliant_txs}'))

        validators_collection.update_one(
            {'name': {'$eq': validator_name},
             'pool': {'$eq': validator_pool}},
            {'$inc': {
                f'{block_date}.num_blocks': 1,
                f'{block_date}.num_txs': len(df_block_txs),
                f'{block_date}.num_ofac_compliant_txs': n_compliant_txs}
             },
            upsert=True)

        logger.info('Saved validators_collection data')

        # Suspicious txes
        should_be_included = df_not_included_txs["prediction"] == 1
        suspicious_txs = df_not_included_txs[should_be_included].copy()
        suspicious_txs.reset_index(drop=True, inplace=True)
        # Save them to tx_censored
        censored_collection = db_analytics['censored_txs']
        censored_collection.create_index('hash', unique=True)
        logger.info('Start saving suspicious_txs')
        for _, row in suspicious_txs.iterrows():
            censored_collection.update_one(
                {'hash': {'$eq': row['hash']}},
                {'$set': {'hash': row['hash'],
                          'first_seen': block_ts - row['already_waiting']},
                 '$push': {'censored': {'block_number': block_number,
                                        'validator': validator_name,
                                        'validator_pool': validator_pool}}},
                upsert=True
            )
        logger.info((f'Found {len(suspicious_txs)} suspicious txs, '
                     f'{n_non_compliant_txs} non compliant'))
        logger.info('Complete saving suspicious_txs')

        # if there are non compliant txes
        if n_non_compliant_txs > 0:
            validators_updates = []
            censored_txs_updates = []
            non_compliant_txs = df_block_txs[df_block_txs['status'] == -1].copy() # noqa E501
            validators_updates.append(UpdateOne(
                filter={'name': {'$eq': validator_name},
                        'pool': {'$eq': validator_pool}},
                update={'$addToSet': {
                    f'{block_date}.non_censored_blocks': block_number}
                 },
                upsert=True
            ))
            for _, row in non_compliant_txs.iterrows():
                tx_hash = row['hash']
                validators_updates.append(UpdateOne(
                    filter={'name': {'$eq': validator_name},
                            'pool': {'$eq': validator_pool}},
                    update={'$addToSet': {
                        f'{block_date}.non_ofac_compliant_txs': tx_hash}
                     },
                    upsert=True
                ))
                censored_txs_updates.append(UpdateOne(
                    filter={'hash': {'$eq': tx_hash}},
                    update={'$set': {'block_number': block_number,
                                     'block_ts': block_ts,
                                     'date': block_date,
                                     'validator': validator_name,
                                     'validator_pool': validator_pool,
                                     'non_ofac_compliant': True,
                                     'hash': tx_hash,
                                     'first_seen': block_ts - row['already_waiting']}, # noqa E501
                            },
                    upsert=True
                ))

                # Add censored blocks information to validators
                censored_tx = censored_collection.find_one(
                    {'hash': {'$eq': tx_hash}})
                if censored_tx is None:
                    continue
                if 'censored' not in censored_tx:
                    continue
                for censored_block in censored_tx['censored']:
                    name = censored_block['validator']
                    n = censored_block['block_number']
                    validators_collection.find_one_and_update(
                        {
                            'name': {'$eq': name}},
                        {'$addToSet': {
                            f'{block_date}.censored_block': n}
                         },
                        upsert=True)
            # Write to db
            if len(validators_updates) > 0:
                validators_collection.bulk_write(validators_updates)
            if len(censored_txs_updates) > 0:
                censored_collection.bulk_write(censored_txs_updates)

        # compliant txs
        if n_compliant_txs > 0:
            censored_txs_updates = []
            total_updates = 0
            compliant_txs = df_block_txs[df_block_txs['status'] == 1].copy() # noqa E501
            for _, row in compliant_txs.iterrows():
                tx_hash = row['hash']
                censored_txs_updates.append(UpdateOne(
                    filter={'hash': {'$eq': tx_hash}},
                    update={
                        '$set': {'block_number': block_number,
                                 'block_ts': block_ts,
                                 'date': block_date,
                                 'validator': validator_name,
                                 'validator_pool': validator_pool,
                                 'non_ofac_compliant': False,
                                 'hash': tx_hash,
                                 'first_seen': block_ts - row['already_waiting']}, # noqa E501
                                }
                ))
            if len(censored_txs_updates):
                update_result = censored_collection.bulk_write(
                    censored_txs_updates)
            total_updates = update_result.modified_count
            logger.info(f'Updated {total_updates} compliant suspicious txs')

    async def get_validator_full_info(self,
                                      block_number: int,
                                      block_ts: int) -> Tuple[str, str]:
        ''' Get block validator (try until success)'''
        logger = logging.getLogger(self.name)
        while True:
            try:
                w3 = self.get_web3_client()
                beacon = self.get_beacon()
                mongo_client = self.get_mongo_analytics_client()
                db_analytics = mongo_client[self.analytics_db_name]
                validator_pubkey = get_validator_pubkey(
                    block_number, block_ts, beacon, w3, db_analytics)
                # TODO Save blocknumber for not found validators
                if validator_pubkey == '':
                    logger.info('Validator not found!')
                    return 'Unknown', 'Unknown'
                return get_validator_info(
                    validator_pubkey, db_analytics)
            except Exception as e:
                logger.error(('Error while getting validator'
                              f'name: {type(e)} {e}'))
                await asyncio.sleep(1)

    async def get_txs_addresses(self,
                                transactions: List[str],
                                w3: Web3) -> Dict[str, List[str]]:
        ''' Get addressess touched by transactions from receipts'''
        logger = logging.getLogger(self.name)
        while True:
            try:
                block_txs_addresses = {}
                for tx in transactions:
                    receipt = w3.eth.get_transaction_receipt(tx)
                    addresses = get_addresses_from_receipt(receipt)
                    block_txs_addresses[tx] = addresses
                return block_txs_addresses
            except TransactionNotFound:
                logger.info(f"Transaction not found {tx} - {time.time():0.2f}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.info(f"Exception {e} - {tx} - {time.time():0.2f}")
                await asyncio.sleep(1)

    def find_txs_in_db(self, hashes_list: List[str], db: Database):
        first_seen_collection = db['tx_first_seen_ts']
        result = first_seen_collection.find(
            {'hash': {'$in': list(hashes_list)}})
        found_in_db = [r['hash'] for r in result]
        return found_in_db

    def get_txs_details_from_db(self, hashes_list: List[str], db: Database):
        details_collection = db['tx_details']
        tx_details_db = details_collection.find(
            {'hash': {'$in': list(hashes_list)}})
        return {r['hash']: r for r in tx_details_db}

    def get_txs_details_from_w3(self, hashes_list: Set[str],
                                w3: Web3) -> Dict[str, Any]:
        additional_details = {}
        for tx_hash in hashes_list:
            try:
                transaction = w3.eth.get_transaction(tx_hash)
                additional_details[tx_hash] = transaction
            except TransactionNotFound:
                pass
        return additional_details

    def gather_gas_estimation(self,
                              txs_details: Dict[str, Any],
                              additional_details: Dict[str, Any],
                              block_number: int,
                              db: Database) -> Dict[str, Any]:
        ''' Gather gas consumptions for all txes'''
        logger = logging.getLogger(self.name)
        gas_consumption = {}

        txs_details_hashes = set(txs_details.keys())
        # Собираем для тех, для которых были детали в ДБ
        estimated_gas_collection = db['tx_estimated_gas']
        estimations_from_db = estimated_gas_collection.find(
            {'hash': {'$in': list(txs_details_hashes)}})

        for estimation in estimations_from_db:
            prev_block = str(block_number - 1)
            if prev_block in estimation:
                gas_consumption[estimation['hash']] = estimation[prev_block]

        # Если estimation по газу не число - то заменяем на gas из details
        for tx_hash in gas_consumption:
            if not isinstance(gas_consumption[tx_hash], int):
                gas_consumption[tx_hash] = txs_details[tx_hash]['gas']

        # Теперь добавим gas из db details для тех, для которых у
        # нас в базе не было оценки
        for tx_hash in txs_details.keys():
            if tx_hash not in gas_consumption:
                gas_consumption[tx_hash] = txs_details[tx_hash]['gas']

        if len(gas_consumption) != len(txs_details):
            logger.error((f'Block {block_number}: len of gas_consumption '
                          'is not equal to number of txs_details_from_w3'))

        # Теперь для тех транзакций, которых не было в БД возьмем
        # потребление газа из блокчейна
        for k, v in additional_details.items():
            gas_consumption[k] = v['gas']
        return gas_consumption

    def create_txs_dataframe(self,
                             block_ts: int,
                             transactions: List[str],
                             txs_details: Dict[str, Any],
                             additional_details: Dict[str, Any],
                             gas_consumption: Dict[str, int],
                             db: Database) -> pd.DataFrame:
        # Возьмем first_seen
        logger = logging.getLogger(self.name)
        first_seen_collection = db['tx_first_seen_ts']
        result = first_seen_collection.find(
            {'hash': {'$in': list(transactions)}})
        first_seen_data = {r['hash']: r for r in result}
        records = []
        all_details = txs_details.copy()
        all_details.update(additional_details)
        for h, v in all_details.items():
            record = {'hash': h, 'from': v['from'], 'nonce': v['nonce']}
            if 'gasPrice' in v:
                record['maxFeePerGas'] = v['gasPrice']
                record['maxPriorityFeePerGas'] = v['gasPrice']
            if 'maxFeePerGas' in v:
                record['maxFeePerGas'] = v['maxFeePerGas']
                record['maxPriorityFeePerGas'] = v['maxFeePerGas']
            if 'maxPriorityFeePerGas' in v and v['maxPriorityFeePerGas'] > 0:
                record['maxPriorityFeePerGas'] = v['maxPriorityFeePerGas']
            record['gas'] = gas_consumption[h]
            if h in first_seen_data:
                waiting_time = block_ts - first_seen_data[h]['timestamp']
                record['already_waiting'] = waiting_time
            else:
                record['already_waiting'] = 0
            records.append(record)

        if len(records) != len(transactions):
            logger.error(('Number of records is not equal  '
                          'to number of all transactions'))
        return pd.DataFrame.from_records(records)

    def add_features_for_classification(self,
                                        df: pd.DataFrame,
                                        block_txs: List[str],
                                        block: Dict[str, Any],
                                        block_number: int,
                                        not_in_mempool: List[str],
                                        ) -> pd.DataFrame:
        w3 = self.get_web3_client()
        df['included_into_next_block'] = df['hash'].apply(
            lambda x: x in block_txs)
        df['baseFeePerGas'] = block['baseFeePerGas'] / 10 ** 9
        df['maxFeePerGas'] = df['maxFeePerGas'] / 10 ** 9
        df['maxPriorityFeePerGas'] = df['maxPriorityFeePerGas'] / 10 ** 9
        df['block_number'] = block_number
        df['availablePriorityFee'] = df['maxFeePerGas'] - df['baseFeePerGas']
        df['availablePriorityFee'] = df[['availablePriorityFee',
                                         'maxPriorityFeePerGas']].min(axis=1)
        df['mempool'] = True
        df.loc[df['hash'].isin(not_in_mempool), 'mempool'] = False

        prev_block = w3.eth.get_block(block_number - 1)
        df['prev_block_gasUsed'] = prev_block['gasUsed']
        df['prev_block_baseFeePerGas'] = prev_block['baseFeePerGas'] / 10 ** 9
        change = df['baseFeePerGas'] - df['prev_block_baseFeePerGas']
        df['change_baseFeePerGas'] = change
        df.sort_values('availablePriorityFee', ascending=False, inplace=True)

        df['total_eligible_txs'] = len(df)
        df['cumulative_gas'] = df['gas'].cumsum()
        df['first_gas_unit'] = df['cumulative_gas'].shift(1).fillna(0)
        df['first_gas_unit'] = df['first_gas_unit'] / 30_000_000
        df['last_gas_unit'] = df['cumulative_gas'] / 30_000_000

        df['priority_n'] = list(range(len(df)))
        df['priority_percent'] = df['priority_n'] / df['total_eligible_txs']
        df['timestamp'] = block['timestamp']
        df['hour'] = df['timestamp'].apply(
            lambda x: datetime.utcfromtimestamp(x).hour)
        return df

    def get_ofac_cache(self,
                       block_ts: int,
                       db: Database):
        ofac_addresses_collection = db['ofac_addresses']
        ofac_db = ofac_addresses_collection.find(
            {'timestamp': {'$lte': block_ts}}
        ).sort('timestamp', -1).limit(1)
        ofac_db = [a for a in ofac_db]
        if len(ofac_db) == 0:
            # Get latest
            ofac_db = ofac_addresses_collection.find({}).sort('timestamp', -1).limit(1) # noqa E501
        ofac_addresses = set([a['addresses'] for a in ofac_db][0])
        return ofac_addresses

    def get_compliance_statuses(self,
                                block_ts: int,
                                block_txs_addresses: Dict[str, List[str]],
                                db: Database
                                ) -> Dict[str, int]:
        if self.ofac_cache is None:
            self.ofac_cache = self.get_ofac_cache(block_ts, db)
        compliance_status = {}
        for tx, addresses in block_txs_addresses.items():
            n_ofac_addresses = len(set(addresses).intersection(self.ofac_cache)) # noqa E501
            if n_ofac_addresses == 0:
                compliance_status[tx] = 1
            else:
                compliance_status[tx] = -1
        return compliance_status

    def update_ofac_list_and_validators(self, block_ts: int, db: Database):
        logger = logging.getLogger(self.name)
        ofac_addresses_collection = db['ofac_addresses']
        ofac_db = ofac_addresses_collection.find()
        ofac_db = ofac_db.sort('timestamp', -1).limit(1)
        ofac_lists = [a for a in ofac_db]
        need_to_update = len(ofac_lists) == 0
        if len(ofac_lists) > 0:
            last_update_ts = ofac_lists[0]['timestamp']
            # update once in 12 hours
            if time.time() - last_update_ts > 12 * 60 * 60:
                need_to_update = True
            if not need_to_update:
                return

        # update ofac list
        logger.info('Fetching OFAC data')
        banned_wallets, is_successful = get_banned_wallets(
            'https://www.treasury.gov/ofac/downloads/sdnlist.txt')
        if is_successful:
            logger.info('Save ofac data')
            ofac_data = get_grouped_by_prefixes(banned_wallets)
            eth_addresses = ofac_data['wallets']['ETH'].copy()
            eth_addresses.extend([a for a in ofac_data['wallets']['USDT']
                                  if a[:2] == '0x'])
            unique_addresses = list(set(eth_addresses))
            ofac_addresses_collection.insert_one({
                'timestamp': ofac_data['dt'],
                'addresses': unique_addresses
            })
            self.ofac_cache = self.get_ofac_cache(block_ts, db)

        # update validators
        logger.info('Fetching lido validators')
        lido_NodeOperatorsRegistry = '0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5' # noqa E501
        with open('lido_contract_abi.json', 'r') as f:
            lido_abi = json.load(f)
        w3 = self.get_web3_client()
        contract = w3.eth.contract(
            address=lido_NodeOperatorsRegistry, abi=lido_abi)

        key_status = {}
        key_to_validator = {}
        key_to_validator_address = {}

        for i in range(contract.functions.getNodeOperatorsCount().call()):
            operator = contract.functions.getNodeOperator(i, True).call()
            logger.info(f'Operator: {operator[1]}')
            for j in range(contract.functions.getTotalSigningKeyCount(i).call()): # noqa E501
                key = contract.functions.getSigningKey(i, j).call()
                key_hex = '0x' + key[0].hex()
                key_to_validator[key_hex] = operator[1]
                key_to_validator_address[key_hex] = operator[2]
                key_status[key_hex] = key[2]

        validators_collection = db['validators']
        validators_db = validators_collection.find()
        validators = set([a['pubkey'] for a in validators_db])
        records = []
        current_time = int(time.time())
        for k, v in key_to_validator.items():
            if k in validators:
                continue
            record = {
                'pubkey': k,
                'pool_name': 'Lido',
                'name': v,
                'timestamp': current_time
            }
            records.append(record)
        logger.info(f'Add {len(records)} new validators to db')
        if len(records) > 0:
            validators_collection.insert_many(records)
