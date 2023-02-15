import asyncio
import json
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import current_process
from typing import List

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError
from web3.auto import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound

logger = logging.getLogger(__name__)


class DataCollector:
    '''Base class for data collectors'''
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float, verbose: bool, name: str = 'DataCollector'):
        self.mongo_url = mongo_url
        self.web3_type = web3_type
        self.web3_url = web3_url
        self.interval = interval
        self.verbose = verbose
        self.name = name

    def run(self):
        asyncio.run(self.collect())

    async def wait_if_needed(self, t1: float):
        logger = logging.getLogger(self.name)
        t2 = time.time()
        time_left = self.interval - (t2 - t1)
        if time_left < 0:
            logger.warning(f'Slow collector: {self.name}')
        await asyncio.sleep(max(time_left, 0))

    def get_mongo_client(self):
        return MongoClient(self.mongo_url)

    def get_web3_client(self):
        logger = logging.getLogger(self.name)
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            logger.info(f'Connected to ETH node: {w3.isConnected()}')
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            logger.error(msg)
            raise Exception(msg)

    async def collect(self):
        raise NotImplementedError


class MempoolCollector(DataCollector):
    '''Collects transactions from the mempool
       and stores the first seen timestamp in MongoDB'''
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float = 0.5, verbose: bool = True):
        super().__init__(mongo_url, web3_type, web3_url,
                         interval, verbose, 'MempoolCollector')

    async def collect(self):
        # Connect to the ETH node and MongoDB
        logger = logging.getLogger(self.name)
        mongo_client = self.get_mongo_client()
        w3 = self.get_web3_client()
        logger.info('Start collecting mempool data')

        # Get the collections
        db = mongo_client['ethereum_mempool']
        first_seen_collection = db['tx_first_seen_ts']
        tx_details_collection = db['tx_details']
        first_seen_collection.create_index('hash', unique=True)
        tx_details_collection.create_index('hash', unique=True)
        tx_filter = w3.eth.filter('pending')
        i = 0
        while True:
            t1 = time.time()
            new_transactions = tx_filter.get_new_entries()
            n = len(new_transactions)
            # Find new transactions
            found_in_db = first_seen_collection.find(
                {"hash": {"$in": new_transactions}})
            existing_hashes = [d['hash'] for d in found_in_db]
            new_hashes = set([h for h in new_transactions
                              if h not in existing_hashes])
            # Prepare data for insertion
            new_transactions_first_seen = [{'hash': h, 'timestamp': int(t1)}
                                           for h in new_hashes]
            # Add details to new transactions
            details_not_found = 0
            new_transactions_details = []
            for tx in new_transactions_first_seen:
                try:
                    tx_data = w3.eth.getTransaction(tx['hash'])
                    tx['from'] = tx_data['from']
                    tx['nonce'] = tx_data['nonce']
                    if 'maxFeePerGas' in tx_data:
                        tx['maxFeePerGas'] = tx_data['maxFeePerGas']
                    else:
                        tx['maxFeePerGas'] = tx_data['gasPrice']
                    # Collect all details in the tx_details collection
                    transaction_dict = dict(**tx_data)
                    if 'value' in transaction_dict:
                        transaction_dict['value'] = str(transaction_dict['value']) # noqa E501
                    new_transactions_details.append(transaction_dict)
                except TransactionNotFound:
                    details_not_found += 1
                    continue
            n_new_txs = len(new_transactions_first_seen)
            details_found = n_new_txs - details_not_found

            # Insert new transactions
            if new_transactions_first_seen:
                first_seen_collection.insert_many(new_transactions_first_seen)
            n_inserted = len(new_transactions_first_seen)
            if self.verbose:
                logger.info((f'Inserted {n_inserted} new txs, '
                             f'found {details_found}/{n_new_txs}'
                             f'txs from {n} total'))
            # Insert details
            if new_transactions_details:
                try:
                    tx_details_collection.insert_many(
                        new_transactions_details, ordered=False)
                except BulkWriteError as bwe:
                    for err_details in bwe.details['writeErrors']:
                        if err_details['code'] != 11000:
                            raise bwe
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning(f'Slow collector: {current_process().name}')
            i += 1
            if i % 20 == 0:
                logger.info('Mempool collector alive!')
            await asyncio.sleep(max(time_left, 0))


class AddressDataCollector:
    def __init__(self, web3_type: str, web3_url: str):
        self.logger = logging.getLogger('AddressDataCollector')
        self.web3_type = web3_type
        self.web3_url = web3_url

    def get_web3_client(self):
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            self.logger.error(msg)
            raise Exception(msg)

    def get_address_data(self, addresses: List[str], block_number: int):
        w3 = self.get_web3_client()
        result = {}
        for address in addresses:
            n_transactions = w3.eth.get_transaction_count(
                address, block_number)
            eth_account = w3.eth.get_balance(
                address, block_number) / 10 ** 18
            result[address] = {'n_txs': n_transactions,
                               'eth': eth_account}
        return result


def split_on_chunks(a: List, chunk_size: int):
    # looping till length l
    for i in range(0, len(a), chunk_size):
        yield a[i:i + chunk_size]


class GasEstimator:
    def __init__(self, web3_type: str, web3_url: str):
        self.logger = logging.getLogger('GasEstimator')
        self.web3_type = web3_type
        self.web3_url = web3_url

    def get_web3_client(self):
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
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


class BlockCollector(DataCollector):
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float = 3, verbose: bool = True):
        super().__init__(mongo_url, web3_type, web3_url,
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
                    await self.process_block_data(
                        block_number, w3, mongo_client)
                last_processed_block = current_block
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning(f'Slow collector: {current_process().name}')
            await asyncio.sleep(max(time_left, 0))

    async def process_block_data(self, block_number: int,
                                 w3: Web3, mongo_client: MongoClient):
        t1 = time.time()
        logger = logging.getLogger(self.name)
        logger.info(f'Start processing block {block_number}')
        db = mongo_client['ethereum_mempool']
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
        result = first_seen_collection.update_many(
            {'hash': {'$in': block['transactions']}},
            {'$set': {'block_number': block_number}})
        logger.info((f'Updated {result.modified_count} transactions of '
                     f'{len(block["transactions"])} in block'))
        logger.info((f'Processing with {num_workers} workers addresses '
                     f'took {int(time.time() - t2)} s'))
        logger.info(f'Block processing took {int(time.time() - t1)} s')

        # Add blocknumber to processed blocks
        processed_blocks_collection = db['processed_blocks']
        processed_blocks_collection.insert_one(
            {'block_info_saved': block_number})


class MemPoolGasEstimator(DataCollector):
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float = 3, verbose: bool = True):
        super().__init__(mongo_url, web3_type, web3_url,
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
        db = mongo_client['ethereum_mempool']
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
                    await self.estimate_gas_for_mempool(
                        block_number, w3, mongo_client)
                    processed_blocks.insert_one(
                        {'block_gas_estimated': block_number})
                last_gas_est_block = current_block
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning(f'Slow collector: {current_process().name}')
            await asyncio.sleep(max(time_left, 0))

            # Get last processed block
            last_block_info_prepared_query = processed_blocks.find().sort(
                'block_info_saved', -1).limit(1)
            last_block_info_prepared = next(last_block_info_prepared_query)
            current_block = last_block_info_prepared['block_info_saved']

    async def estimate_gas_for_mempool(self, block_number: int,
                                       w3: Web3, mongo_client: MongoClient):
        t1 = time.time()
        logger = logging.getLogger(self.name)
        logger.info(f'Start gasestimation {block_number}')
        db = mongo_client['ethereum_mempool']
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

        logger.info(f'Will estimate gas for {len(txs_for_gas_estimate)} txs')

        # Estimate gas for txs
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
        for i in range(0, len(chunks), num_workers):
            current_chunks = chunks[i:i + num_workers]
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
            data = await asyncio.gather(*collection_tasks)
            for d in data:
                estimated_gas.update(d)
        # TODO Save gas estimation to Mongo DB
        tx_gas_collection = db['tx_estimated_gas']
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
                     f'seconds - got {len(estimated_gas)}'))


class CollectorManager:
    '''Manages the data collectors.
       Run them concurrently in a process pool.
       Each collector can use asyncio to run tasks concurrently'''
    def __init__(self, data_collectors: List[DataCollector],
                 max_workers: int = 8):

        self.pool_executor = ProcessPoolExecutor(max_workers=max_workers)
        self.data_collectors = data_collectors

    async def start(self):
        '''Start the data collectors in a fire and forget manner'''
        self.event_loop = asyncio.get_event_loop()
        collection_tasks = [
            self.event_loop.run_in_executor(
                self.pool_executor,
                collector.run,
            )
            for collector in self.data_collectors
        ]
        await asyncio.gather(*collection_tasks)
