import asyncio
import logging
import time
from multiprocessing import current_process

from pymongo.errors import BulkWriteError
from web3.exceptions import TransactionNotFound

from .data_collector import DataCollector

logger = logging.getLogger(__name__)


class MempoolCollector(DataCollector):
    '''Collects transactions from the mempool
       and stores the first seen timestamp in MongoDB'''
    def __init__(self, mongo_url: str, db_name: str,
                 web3_type: str, web3_url: str,
                 interval: float = 0.5, verbose: bool = True):
        super().__init__(mongo_url, db_name, web3_type, web3_url,
                         interval, verbose, 'MempoolCollector')

    async def collect(self):
        # Connect to the ETH node and MongoDB
        logger = logging.getLogger(self.name)
        mongo_client = self.get_mongo_client()
        w3 = self.get_web3_client()
        logger.info('Start collecting mempool data')

        # Get the collections
        db = mongo_client[self.db_name]
        first_seen_collection = db['tx_first_seen_ts']
        tx_details_collection = db['tx_details']
        first_seen_collection.create_index('hash', unique=True)
        first_seen_collection.create_index('block_number', unique=False)
        tx_details_collection.create_index('hash', unique=True)
        tx_filter = w3.eth.filter('pending')
        i = 0
        while True:
            t1 = time.time()
            new_transactions = [tx.hex() for tx in tx_filter.get_new_entries()]
            t_eth_get_filter_update = time.time() - t1
            t_current = time.time()
            n = len(new_transactions)
            # Find new transactions            
            found_in_db = first_seen_collection.find(
                {"hash": {"$in": new_transactions}})
            existing_hashes = [d['hash'] for d in found_in_db]
            t = time.time()
            t_mongo_get_existing_from_mongo = t - t_current
            t_current = t

            # Return dropped txes
            first_seen_collection.update_many(
                {'hash': {'$in': existing_hashes}},
                {'$set': {'dropped': False},
                 '$unset': {'block_number': ''}}
            )
            t_mongo_return_dropped = time.time() - t_current

            new_hashes = set([h for h in new_transactions
                              if h not in existing_hashes])
            # Prepare data for insertion
            new_transactions_first_seen = [{'hash': h, 'timestamp': int(t1)}
                                           for h in new_hashes]
            # Add details to new transactions
            details_not_found = 0
            new_transactions_details = []
            t_current = time.time()
            for tx in new_transactions_first_seen:
                try:
                    tx_data = w3.eth.getTransaction(tx['hash'])
                    tx['from'] = tx_data['from']
                    tx['nonce'] = tx_data['nonce'] % 10 ** 9
                    if 'maxFeePerGas' in tx_data:
                        tx['maxFeePerGas'] = tx_data['maxFeePerGas']
                    else:
                        tx['maxFeePerGas'] = tx_data['gasPrice']
                    # Collect all details in the tx_details collection
                    transaction_dict = dict(**tx_data)
                    if 'value' in transaction_dict:
                        transaction_dict['value'] = str(transaction_dict['value']) # noqa E501
                    transaction_dict['hash'] = transaction_dict['hash'].hex()
                    new_transactions_details.append(transaction_dict)
                except TransactionNotFound:
                    details_not_found += 1
                    continue
            n_new_txs = len(new_transactions_first_seen)
            details_found = n_new_txs - details_not_found
            t_eth_get_new_details = time.time() - t_current

            # Insert new transactions
            t_eth_insert_new_txs = 0
            if new_transactions_first_seen:
                t_current = time.time()
                first_seen_collection.insert_many(new_transactions_first_seen)
                t_eth_insert_new_txs = time.time() - t_current
            n_inserted = len(new_transactions_first_seen)
            if self.verbose:
                logger.info((f'Inserted {n_inserted} new txs, '
                             f'found {details_found}/{n_new_txs}'
                             f'txs from {n} total'))
            # Insert details
            t_eth_insert_new_txs_details = 0
            if new_transactions_details:
                try:
                    t_current = time.time()
                    tx_details_collection.insert_many(
                        new_transactions_details, ordered=False)
                except BulkWriteError as bwe:
                    for err_details in bwe.details['writeErrors']:
                        if err_details['code'] != 11000:
                            raise bwe
                finally:
                    t_eth_insert_new_txs_details = time.time() - t_current
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning((f'Slow collector: {current_process().name} - '
                                f'{t2 - t1:0.2f} of {self.interval} sec'))
                logger.warning(f't_eth_get_filter_update: {t_eth_get_filter_update:0.2f}')
                logger.warning(f't_mongo_get_existing_from_mongo: {t_mongo_get_existing_from_mongo:0.2f}')
                logger.warning(f't_mongo_return_dropped: {t_mongo_return_dropped:0.2f}')
                logger.warning(f't_eth_get_new_details: {t_eth_get_new_details:0.2f}')
                logger.warning(f't_eth_insert_new_txs: {t_eth_insert_new_txs:0.2f}')
                logger.warning(f't_eth_insert_new_txs_details: {t_eth_insert_new_txs_details:0.2f}')
            i += 1
            if i % 20 == 0:
                logger.info('Mempool collector alive!')
            await asyncio.sleep(max(time_left, 0))