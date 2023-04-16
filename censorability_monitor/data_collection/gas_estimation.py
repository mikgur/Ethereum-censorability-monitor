import asyncio
import json
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import current_process

import pandas as pd
from pymongo import MongoClient, UpdateOne
from web3.auto import Web3
from web3.exceptions import ContractLogicError

from .data_collector import DataCollector
from .utils import split_on_chunks

logger = logging.getLogger(__name__)


class GasEstimator:
    def __init__(self, web3_type: str, web3_url: str):
        self.logger = logging.getLogger('GasEstimator')
        self.web3_type = web3_type
        self.web3_url = web3_url

    def get_web3_client(self):
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            return w3
        elif self.web3_type == 'http':
            w3 = Web3(Web3.HTTPProvider(self.web3_url))
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            self.logger.error(msg)
            raise Exception(msg)

    def estimate_chunk_gas(self, chunk, block_number):
        w3 = self.get_web3_client()
        gas_estimates = {}
        for tx_details in chunk:
            tx_hash = tx_details['hash']
            result = self.estimate_tx_gas(tx_details, block_number, w3)
            gas_estimates[tx_hash] = {'block_number': block_number,
                                      'gas': result}
        return gas_estimates

    def estimate_tx_gas(self, tx_details, block_number, w3):
        try:
            tx_data = tx_details.copy()
            del tx_data['_id']
            del tx_data['hash']
            del tx_data['blockHash']
            del tx_data['blockNumber']
            del tx_data['r']
            del tx_data['s']
            if 'gasPrice' in tx_data and 'maxFeePerGas' in tx_data:
                del tx_data['gasPrice']
            json_tx = w3.toJSON(tx_data)
            json_tx = json.loads(json_tx)
            est_gas = w3.eth.estimate_gas(
                json_tx, block_number)
            return est_gas
        except ContractLogicError:
            return 'contract_logic_error'
        except ValueError as e:
            if e.args[0]['message'].startswith(
                    'err: max fee per gas less than block base fee'):
                return 'low maxFeePerGass'
            elif e.args[0]['message'] == 'insufficient funds for transfer':
                return 'not enough eth'
            elif e.args[0]['message'].startswith(
                    'invalid opcode'):
                return 'invalid opcode'
            elif e.args[0]['message'].startswith(
                    'gas required exceeds allowance'):
                return 'low gas limit'
            elif e.args[0]['message'].startswith(
                    'invalid jump destination'):
                return 'invalid jump'
            elif e.args[0]['message'].startswith(
                    'contract creation code storage out of gas'):
                return 'contract creation error'
            return 'unknown value error'


def get_transactions_for_gas_estimation(db, block_number, w3):
    first_seen_collection = db['tx_first_seen_ts']
    tx_details_collection = db['tx_details']
    block = w3.eth.getBlock(block_number)
    block_ts = block['timestamp']
    # Get transactions from mempool that are not in the blocks
    # and update their from accounts data
    # t1 = time.time()
    transactions = first_seen_collection.find(
        {'timestamp': {'$lte': block_ts},
         '$or': [{'block_number': {'$exists': False}},
                 {'block_number': {'$gte': block_number}}]
         })
    # Get mempool accounts and remove old txs without details
    n_mempool_txs = 0
    # Get list of interesting transactions
    txs_for_gas_estimate = set()
    for tx in transactions:
        n_mempool_txs += 1
        if 'from' not in tx:
            continue
        # check that tx maxGasPrice is higher than blocks BaseFeePerGas
        if ('maxFeePerGas' in tx
                and tx['maxFeePerGas'] < block['baseFeePerGas']):
            continue
        # Put into list for gas estimation
        txs_for_gas_estimate.add(tx['hash'])
    # t2 = time.time()
    # print(f'Interval 1: {t2 - t1:0.2f} - found {len(txs_for_gas_estimate)}')

    # Get details
    tx_details_collection = db['tx_details']
    tx_details_db = tx_details_collection.find(
        {'hash': {'$in': list(txs_for_gas_estimate)}})
    tx_details = {tx['hash']: tx for tx in tx_details_db}
    # t3 = time.time()
    # print(f'Interval 2: {t3 - t2:0.2f}')

    # Fetch address info
    addresses = set()
    for _, tx in tx_details.items():
        addresses.add(tx['from'])

    accounts_collection = db['addresses_info']
    accounts_details_db = accounts_collection.find(
        {'address': {'$in': list(addresses)}})

    block_accounts_info = {
        a['address']: {
                        'eth': a[str(block_number - 1)]['eth'],
                        'n_txs': a[str(block_number - 1)]['n_txs']
                       }
        for a in accounts_details_db
        if str(block_number - 1) in a}
    # print(f'Accounts: {len(block_accounts_info)}')
    # t4 = time.time()
    # print(f'Interval 3: {t4 - t3:0.2f}')

    # Make df for nonce analysis
    records = []
    for _, tx in tx_details.items():
        records.append({'hash': tx['hash'],
                        'from': tx['from'],
                        'nonce': tx['nonce']})

    tx_df = pd.DataFrame.from_records(records)
    if len(records) == 0:
        return []
    tx_grouped = tx_df.groupby(['from', 'hash']).agg({'nonce': 'first'})

    # t5 = time.time()
    # print(f'Interval 4: {t5 - t4:0.2f}')

    # Remove transactions that can't be included to block due to high nonce
    all_nonce_blocked = set()
    for addr in tx_df['from'].unique():
        if addr not in block_accounts_info:
            continue
        block_txs = False
        n_txs = block_accounts_info[addr]['n_txs']
        transactions_from_addr = tx_grouped.loc[addr].sort_values(
            'nonce', ascending=True
        ).reset_index()
        for i, row in transactions_from_addr.iterrows():
            if row['nonce'] > n_txs:
                block_txs = True
                break
            n_txs += 1
        if block_txs:
            nonce_blocked = transactions_from_addr['hash'].values[i:]
            all_nonce_blocked.update(nonce_blocked)

    non_blocked = tx_df[~tx_df['hash'].isin(all_nonce_blocked)]
    non_blocked_hashes = non_blocked['hash'].values

    # t6 = time.time()
    # print(f'Interval 5: {t6 - t5:0.2f}')

    # Remove transactions with not enough value to transfer
    eligible_transactions = []
    for tx_hash in non_blocked_hashes:
        if tx_hash not in tx_details:
            continue
        details = tx_details[tx_hash]
        addr = details['from']
        if addr not in block_accounts_info:
            eligible_transactions.append(tx_hash)
            continue
        if 'value' in details:
            value = int(details['value']) / 10 ** 18
            if value >= block_accounts_info[addr]['eth']:
                continue
        eligible_transactions.append(tx_hash)
    # t7 = time.time()
    # print(f'Interval 6: {t7 - t6:0.2f}')
    return eligible_transactions


class MemPoolGasEstimator(DataCollector):
    def __init__(self, mongo_url: str, db_name: str,
                 web3_type: str, web3_url: str,
                 interval: float = 3, verbose: bool = True):
        super().__init__(mongo_url, db_name, web3_type, web3_url,
                         interval, verbose, 'MemPoolGasEstimator')
        self.max_workers = 256
        self.gas_estimators = [
            GasEstimator(web3_type, web3_url)
            for _ in range(self.max_workers)
        ]

    async def collect(self):
        logger = logging.getLogger(self.name)
        mongo_client = self.get_mongo_client()
        w3 = self.get_web3_client()
        db = mongo_client[self.db_name]
        processed_blocks = db['processed_blocks']

        # Wait for the first block to be processed
        logger.info('Waiting for processed blocks')
        total_blocks_prepared = processed_blocks.count_documents(
                {'block_info_saved': {'$exists': True}})
        while total_blocks_prepared == 0:
            total_blocks_prepared = processed_blocks.count_documents(
                {'block_info_saved': {'$exists': True}})
            await asyncio.sleep(1)
        logger.info('Waiting for recent (not older 128) processed block')
        last_block_info_prepared_query = processed_blocks.find().sort(
                'block_info_saved', -1).limit(1)
        last_block_info_prepared = next(last_block_info_prepared_query)
        last_block_saved = last_block_info_prepared['block_info_saved']
        last_eth_block = w3.eth.blockNumber
        while last_eth_block - last_block_saved > 128:
            last_block_info_prepared_query = processed_blocks.find().sort(
                'block_info_saved', -1).limit(1)
            last_block_info_prepared = next(last_block_info_prepared_query)
            last_block_saved = last_block_info_prepared['block_info_saved']
            last_eth_block = w3.eth.blockNumber
            await asyncio.sleep(1)
        logger.info(f'Starting gas estimation from block {last_block_saved}')
        current_block = last_block_saved
        last_gas_est_block = current_block - 1
        while True:
            t1 = time.time()
            if current_block > last_gas_est_block:
                for block_number in range(last_gas_est_block + 1,
                                          current_block + 1):
                    completed = False
                    n_attempt = 0
                    while not completed and n_attempt < 5:
                        n_attempt += 1
                        try:
                            await asyncio.wait_for(self.estimate_gas_for_mempool(
                                block_number, w3, mongo_client),
                                timeout=40)
                            completed = True
                        except asyncio.TimeoutError:
                            logger.error((f"Unable to estimate gas for block {block_number}"
                                          f" attempt: {n_attempt}"))
                            w3 = self.get_web3_client()
                        except Exception as e:
                            logger.error(f"Error while estimating gas {block_number} - {n_attempt} {type(e)} {e}")
                            w3 = self.get_web3_client()
                    processed_blocks.insert_one(
                        {'block_gas_estimated': block_number})
                last_gas_est_block = current_block
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning((f'Slow collector: {current_process().name} - '
                                f'{t2 - t1:0.2f} of {self.interval} sec'))
            # logger.info(f'Will wait for {max(time_left, 0)}')
            await asyncio.sleep(max(time_left, 0))

            # Get last processed block
            last_block_info_prepared_query = processed_blocks.find().sort(
                'block_info_saved', -1).limit(1)
            last_block_info_prepared = next(last_block_info_prepared_query)
            current_block = last_block_info_prepared['block_info_saved']
            # logger.info(f'Got last saved block: {current_block}')

    async def estimate_gas_for_mempool(self, block_number: int,
                                       w3: Web3, mongo_client: MongoClient):
        t1 = time.time()
        logger = logging.getLogger(self.name)
        logger.info(f'Start gas estimation {block_number}')
        db = mongo_client[self.db_name]

        txs_for_gas_estimate = get_transactions_for_gas_estimation(
            db, block_number, w3
        )
        logger.info(f'Complete gathering list: {time.time() - t1:0.2f} sec')

        # Estimate gas for txs
        tx_details_collection = db['tx_details']
        transactions_details = tx_details_collection.find(
            {'hash': {'$in': list(txs_for_gas_estimate)}}
        )
        transactions_details = [d for d in transactions_details]
        batch_size = 1000
        num_workers = min(len(transactions_details) // batch_size + 1,
                          self.max_workers)
        process_executor = ProcessPoolExecutor(max_workers=num_workers)
        event_loop = asyncio.get_event_loop()
        chunks = list(split_on_chunks(list(transactions_details), batch_size))
        estimated_gas = {}
        t_2 = time.time()
        for i in range(0, len(chunks), num_workers):
            current_chunks = chunks[i:i + num_workers]
            n_attempt = 0
            completed = False
            while not completed and n_attempt < 5:
                n_attempt += 1
                collection_tasks = [
                    event_loop.run_in_executor(
                        process_executor,
                        estimator.estimate_chunk_gas,
                        chunk,
                        block_number - 1
                    )
                    for estimator, chunk in zip(self.gas_estimators,
                                                current_chunks)
                ]
                try: 
                    data = await asyncio.wait_for(
                        asyncio.gather(*collection_tasks),
                        timeout=30)
                    completed = True
                except asyncio.TimeoutError:
                    logger.error(f"Timeout for gas estimation: {n_attempt}")
                except Exception as e:
                    logger.error(f"Error {type(e)} {e} while gas estimation: {n_attempt} {type(e)} {e}")
            if not completed:
                logger.info(f"Unable to complete gas estimation!")
                return
            for d in data:
                estimated_gas.update(d)
        logger.info(f'Estimation: {time.time() - t_2:0.2f} sec')
        # Save gas estimation to Mongo DB
        tx_gas_collection = db['tx_estimated_gas']
        tx_gas_collection.create_index('hash')
        updates = []
        for tx_hash, gas in estimated_gas.items():
            updates.append(UpdateOne(
                {'hash': tx_hash},
                {'$set': {str(gas['block_number']): gas['gas']}},
                upsert=True
            ))
        if len(updates) > 0:
            tx_gas_collection.bulk_write(updates)
        logger.info((f'Gas estimation took {int(time.time() - t1)} '
                     f'seconds - got {len(estimated_gas)} of '
                     f'{len(txs_for_gas_estimate)}'))
