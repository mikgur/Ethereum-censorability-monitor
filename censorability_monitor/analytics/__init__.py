import asyncio
import logging

from pymongo import MongoClient
from web3.auto import Web3
from pymongo.database import Database


class CensorshipMonitor:
    ''' Monitor non included into block transactions'''
    def __init__(self, mongo_url: str, web3_type: str, web3_url: str,
                 interval: float, verbose: bool, start_block: int = 0,
                 name: str = 'CensorshipMonitoe'):
        self.mongo_url = mongo_url
        self.web3_type = web3_type
        self.web3_url = web3_url
        self.interval = interval
        self.verbose = verbose
        self.name = name
        self.start_block = start_block

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
        db_collector = mongo_client['ethereum_mempool']
        db_analytics = mongo_client['ethereum_censorship_monitor']

        logger.info('Select starting block')
        last_processed_block = self.get_last_processed_block_number(
            db_analytics)

        first_ready_block = await self.get_first_ready_block_number(
            db_collector)
        if self.start_block > 1:
            first_ready_block = max(self.start_block - 1, first_ready_block)

        last_ready_block = await self.get_last_ready_block_number(
            db_collector)

        if last_processed_block > last_ready_block:
            logger.error(('Last processed block is higher than first ready '
                          'block - something is wrong with DB'))
            raise Exception('Check database')

        # Set current block
        current_block = max(first_ready_block, last_processed_block) + 1
        while True:
            while current_block > last_ready_block:
                asyncio.sleep(1)
                last_ready_block = await self.get_last_ready_block_number(
                    db_collector)
            while current_block <= last_ready_block:
                await self.process_block(current_block)
                current_block += 1
                await asyncio.sleep(1)

    async def process_block(self, block_number: int):
        logger = logging.getLogger(self.name)
        logger.info(f'processing {block_number}')
        mongo_client = self.get_mongo_client()
        db_analytics = mongo_client['ethereum_censorship_monitor']
        # Save block_number to db
        processed_blocks = db_analytics['processed_blocks']
        processed_blocks.insert_one(
            {'block_number': block_number})
