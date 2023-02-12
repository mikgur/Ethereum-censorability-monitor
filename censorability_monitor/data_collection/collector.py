import asyncio
import logging
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import current_process
from typing import List

from pymongo import MongoClient
from web3.auto import Web3

logger = logging.getLogger(__name__)


class DataCollector:
    '''Base class for data collectors'''
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float, name: str = 'DataCollector'):
        self.mongo_url = mongo_url
        self.web3_type = web3_type
        self.web3_url = web3_url
        self.interval = interval
        self.name = name

    def run(self):
        asyncio.run(self.collect())

    async def collect(self):
        raise NotImplementedError


class MempoolCollector(DataCollector):
    '''Collects transactions from the mempool
       and stores the first seen timestamp in MongoDB'''
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float = 0.5):
        super().__init__(mongo_url, web3_type, web3_url,
                         interval, 'MempoolCollector')

    async def collect(self):
        # Connect to the ETH node and MongoDB
        logger = logging.getLogger('MempoolCollector')
        if self.web3_type == 'ipc':
            self.w3 = Web3(Web3.IPCProvider(self.web3_url))
            self.mongo_client = MongoClient(self.mongo_url)
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            logger.error(msg)
            raise Exception(msg)
        logger.info(f'Connected to ETH node: {self.w3.isConnected()}')

        # Get the collections
        db = self.mongo_client['ethereum_mempool']
        first_seen_collection = db['tx_first_seen_ts']
        tx_filter = self.w3.eth.filter('pending')
        while True:
            t1 = time.time()
            new_transactions = tx_filter.get_new_entries()
            n = len(new_transactions)
            # Find new transactions
            found_in_db = first_seen_collection.find(
                {"hash": {"$in": new_transactions}})
            existing_hashes = [d['hash'] for d in found_in_db]
            new_hashes = [h for h in new_transactions
                          if h not in existing_hashes]
            # Prepare data for insertion
            new_transactions_first_seen = [{'hash': h, 'timestamp': t1}
                                           for h in new_hashes]
            # Insert new transactions
            if new_transactions_first_seen:
                first_seen_collection.insert_many(new_transactions_first_seen)
            n_inserted = len(new_transactions_first_seen)
            logger.info((f'Inserted {n_inserted} new '
                         f'transactions from {n} total'))
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning(f'Slow collector: {current_process().name}')
            await asyncio.sleep(max(time_left, 0))


class BlockCollector(DataCollector):
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float = 3):
        super().__init__(mongo_url, web3_type, web3_url,
                         interval, 'BlockCollector')

    async def collect(self):
        logger = logging.getLogger('BlockCollector')
        if self.web3_type == 'ipc':
            self.w3 = Web3(Web3.IPCProvider(self.web3_url))
            self.mongo_client = MongoClient(self.mongo_url)
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            logger.error(msg)
            raise Exception(msg)

        logger.info(f'Connected to ETH node: {self.w3.isConnected()}')
        while True:
            t1 = time.time()
            logger.info('BlockCollector ping')
            t2 = time.time()
            time_left = self.interval - (t2 - t1)
            if time_left < 0:
                logger.warning(f'Slow collector: {current_process().name}')
            await asyncio.sleep(max(time_left, 0))


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
