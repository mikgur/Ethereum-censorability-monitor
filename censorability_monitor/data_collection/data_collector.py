import asyncio
import logging
import time

import pandas as pd
from pymongo import MongoClient
from web3.auto import Web3


logger = logging.getLogger(__name__)


class DataCollector:
    '''Base class for data collectors'''
    def __init__(self, mongo_url: str, db_name: str,
                 web3_type: str, web3_url: str,
                 interval: float, verbose: bool, name: str = 'DataCollector'):
        self.mongo_url = mongo_url
        self.db_name = db_name
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
            logger.warning((f'Slow collector: {self.name} - '
                            f'{t2 - t1:0.2f} of {self.interval} sec'))
        await asyncio.sleep(max(time_left, 0))

    def get_mongo_client(self):
        return MongoClient(self.mongo_url)

    def get_web3_client(self):
        logger = logging.getLogger(self.name)
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            logger.info(f'Connected to ETH node: {w3.isConnected()}')
            return w3
        elif self.web3_type == 'http':
            w3 = Web3(Web3.HTTPProvider(self.web3_url))
            logger.info(f'Connected to ETH node: {w3.isConnected()}')
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            logger.error(msg)
            raise Exception(msg)

    async def collect(self):
        raise NotImplementedError


