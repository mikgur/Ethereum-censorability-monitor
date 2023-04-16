import asyncio
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import current_process

import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from web3.auto import Web3
from web3.exceptions import TransactionNotFound

from .address_collector import AddressDataCollector
from .data_collector import DataCollector
from .gas_estimation import GasEstimator
from .utils import split_on_chunks

logger = logging.getLogger(__name__)


class BlockCollector(DataCollector):
    def __init__(self, mongo_url: str, db_name: str,
                 web3_type: str, web3_url: str,
                 interval: float = 3, verbose: bool = True):
        super().__init__(mongo_url, db_name, web3_type, web3_url,
                         interval, verbose, 'BlockCollector')
        self.max_workers = 256
        self.address_data_collectors = [
            AddressDataCollector(web3_type, web3_url)
            for _ in range(self.max_workers)
        ]
        self.gas_estimators = [
            GasEstimator(web3_type, web3_url)
            for _ in range(self.max_workers)
        ]

    async def collect(self):
        logger = logging.getLogger(self.name)
        mongo_client = self.get_mongo_client()
        w3 = self.get_web3_client()

        last_processed_block = w3.eth.blockNumber - 1
        while True:
            t1 = time.time()
            current_block = w3.eth.blockNumber
            if current_block > last_processed_block:
                for block_number in range(last_processed_block + 1,
                                          current_block + 1):
                    try:
                        await self.process_block_data(
                            block_number, w3, mongo_client)
                    except Exception as e:
                        logger.error(f'Block {block_number} - {type(e)} {e}')
                last_processed_block = current_block
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning((f'Slow collector: {current_process().name} - '
                                f'{t2 - t1:0.2f} of {self.interval} sec'))
            await asyncio.sleep(max(time_left, 0))

    async def process_block_data(self, block_number: int,
                                 w3: Web3, mongo_client: MongoClient):
        t1 = time.time()
        logger = logging.getLogger(self.name)
        logger.info(f'Start processing block {block_number}')
        db = mongo_client[self.db_name]
        first_seen_collection = db['tx_first_seen_ts']
        tx_details_collection = db['tx_details']
        block = w3.eth.getBlock(block_number)
        block_ts = block['timestamp']
        # Get transactions from mempool that are not in the blocks
        # and update their from accounts data
        transactions = first_seen_collection.find(
            {'timestamp': {'$lte': block_ts},
             'block_number': {'$exists': False}})
        # Get mempool accounts and remove old txs without details
        no_details = 0
        n_mempool_txs = 0
        remove_from_mempool = []
        mempool_accounts = set()
        low_fee_txs = 0
        old_txs_found = 0
        # Remove old txs without details
        # Try to find deails for txs without details
        # Get list of addresses with txs with enough gas price
        found_details = []
        for tx in transactions:
            n_mempool_txs += 1
            if 'from' not in tx:
                try:
                    tx_data = w3.eth.getTransaction(tx['hash'])
                    found_tx = {}
                    found_tx['from'] = tx_data['from']
                    found_tx['nonce'] = tx_data['nonce']
                    if 'maxFeePerGas' in tx_data:
                        found_tx['maxFeePerGas'] = tx_data['maxFeePerGas']
                    else:
                        found_tx['maxFeePerGas'] = tx_data['gasPrice']
                    first_seen_collection.update_one(
                        {'hash': tx['hash']},
                        {'$set': found_tx})
                    # Save all details
                    transaction_dict = dict(**tx_data)
                    if 'value' in transaction_dict:
                        transaction_dict['value'] = str(transaction_dict['value']) # noqa E501
                    transaction_dict['hash'] = transaction_dict['hash'].hex()
                    found_details.append(transaction_dict)
                    old_txs_found += 1
                except TransactionNotFound:
                    no_details += 1
                # Remove tx that doesn't have details after 60 seconds
                if block_ts - tx['timestamp'] > 60:
                    remove_from_mempool.append(tx['hash'])
                continue
            # check that tx maxGasPrice is higher than blocks BaseFeePerGas
            if ('maxFeePerGas' in tx
                    and tx['maxFeePerGas'] < block['baseFeePerGas']):
                low_fee_txs += 1
                continue
            mempool_accounts.add(tx['from'])
        logger.info(f'Found {old_txs_found} old transactions')

        # Put found details to db
        if found_details:
            try:
                tx_details_collection.insert_many(
                    found_details, ordered=False)
            except BulkWriteError as bwe:
                for err_details in bwe.details['writeErrors']:
                    if err_details['code'] != 11000:
                        raise bwe
        n_removed = len(remove_from_mempool)

        # Remove old enough txs without details
        first_seen_collection.delete_many(
            {'hash': {'$in': remove_from_mempool}})
        logger.info((f'Found {no_details}/{n_mempool_txs} txs without '
                     f'details, remove {n_removed} from mempool. '))
        logger.info(f'Interesting accs in mempool: {len(mempool_accounts)}')

        # Update accounts info:
        t2 = time.time()
        batch_size = 1000
        num_workers = min(len(mempool_accounts) // batch_size + 1,
                          self.max_workers)
        process_executor = ProcessPoolExecutor(max_workers=num_workers)
        event_loop = asyncio.get_event_loop()
        chunks = list(split_on_chunks(list(mempool_accounts), batch_size))
        address_data = {}
        for i in range(0, len(chunks), num_workers):
            current_chunks = chunks[i:i + num_workers]
            collection_tasks = [
                event_loop.run_in_executor(
                    process_executor,
                    collector.get_address_data,
                    chunk,
                    block_number - 1
                )
                for collector, chunk in zip(self.address_data_collectors,
                                            current_chunks)
            ]
            data = await asyncio.gather(*collection_tasks)
            for d in data:
                address_data.update(d)
        # Save accounts info to db
        accounts_collection = db['addresses_info']
        accounts_collection.create_index('address', unique=True)
        accounts_in_db = accounts_collection.find(
            {'address': {'$in': list(mempool_accounts)}})
        existing_accounts = {a['address']: a for a in accounts_in_db}
        new_accounts = [a for a in mempool_accounts
                        if a not in existing_accounts]
        insert_records = [{'address': a, str(block_number - 1): address_data[a]
                           } for a in new_accounts]
        if len(insert_records) > 0:
            accounts_collection.insert_many(insert_records)

        update_documents = [
            UpdateOne(
                {'address': {'$eq': a}},
                {'$set':
                    {f'{block_number - 1}.n_txs': address_data[a]['n_txs'],
                     f'{block_number - 1}.eth': address_data[a]['eth']}
                 }
            )
            for a in existing_accounts
        ]
        if len(update_documents) > 0:
            accounts_collection.bulk_write(update_documents)

        # Add block number to transactions included in the current block
        block_hashes = [h.hex() for h in block['transactions']]
        result = first_seen_collection.update_many(
            {'hash': {'$in': block_hashes}},
            {'$set': {'block_number': block_number}})
        logger.info((f'Updated {result.modified_count} transactions of '
                     f'{len(block["transactions"])} in block'))
        logger.info((f'Processing with {num_workers} workers addresses '
                     f'took {int(time.time() - t2)} s'))

        # Remove reverted transactions from future queries
        # We will set block_number -1 for them

        transactions = first_seen_collection.find(
            {'timestamp': {'$lte': block_ts},
             'block_number': {'$exists': False}})
        # Get list of interesting transactions
        tx_details = []
        for tx in transactions:
            if 'from' not in tx:
                continue
            tx_details.append(tx)
        records = []
        for tx in tx_details:
            records.append({'hash': tx['hash'],
                            'from': tx['from'],
                            'nonce': tx['nonce']})
        if len(records) > 0:
            tx_df = pd.DataFrame.from_records(records)
            tx_grouped = tx_df.groupby(
                ['from', 'hash']).agg({'nonce': 'first'})
            total_reverted = 0
            reverted_tx_hashes = set()
            for addr in tx_df['from'].unique():
                if addr not in address_data:
                    continue
                n_txs = address_data[addr]['n_txs']
                addr_txs = tx_grouped.loc[addr].sort_values(
                    'nonce', ascending=True
                    ).reset_index()
                addr_txs['reverted'] = addr_txs['nonce'] < n_txs
                reverted = addr_txs['reverted'].sum()
                reverted_tx_hashes.update(
                    addr_txs[addr_txs['reverted']]['hash'])
                total_reverted += reverted
            logger.info(f'Found {total_reverted} reverted txs')
            # Save result to db
            first_seen_collection.update_many(
                {'hash': {'$in': list(reverted_tx_hashes)}},
                {'$set': {'block_number': -1}}
            )

        # Drop transactions that are not in mempool currently
        t_drop = time.time()
        mempool = w3.geth.txpool.content()
        mempool_hashes = []
        for _, v in mempool['queued'].items():
            for _, w in v.items():
                mempool_hashes.append(w['hash'])
        for _, v in mempool['pending'].items():
            for _, w in v.items():
                mempool_hashes.append(w['hash'])
        # Transactions older than hour without block
        transactions = first_seen_collection.find(
            {'timestamp': {'$lte': time.time() - 3600},
             'block_number': {'$exists': False}
             })
        transactions_to_drop = []
        for tx in transactions:
            if tx['hash'] not in mempool_hashes:
                transactions_to_drop.append(tx['hash'])
        first_seen_collection.update_many(
            {'hash': {'$in': transactions_to_drop}},
            {'$set': {'block_number': -2, 'dropped': True}}
        )
        logger.info(f'Dropping txes took {time.time() - t_drop:0.2f} sec')

        # Add blocknumber to processed blocks
        processed_blocks_collection = db['processed_blocks']
        processed_blocks_collection.insert_one(
            {'block_info_saved': block_number})

        logger.info(f'Block processing took {int(time.time() - t1)} s')