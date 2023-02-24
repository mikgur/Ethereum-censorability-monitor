import asyncio
import logging
import logging.config
import os

import yaml
from dotenv import load_dotenv

from censorability_monitor.data_collection import (BlockCollector,
                                                   CollectorManager,
                                                   MempoolCollector,
                                                   MemPoolGasEstimator)

load_dotenv()

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def main():
    web3_url = os.environ.get('node_url', '')
    web3_connection_type = os.environ.get('node_connection_type', '')

    db_col_url = os.environ.get('db_collector_url', 'localhost')
    db_col_port = os.environ.get('db_collector_port', '27017')
    db_col_usr = os.environ.get('db_collector_username', 'root')
    db_col_pass = os.environ.get('db_collector_password', 'password')
    db_col_name = os.environ.get('db_collector_name', 'ethereum_mempool')
    mongo_url = f'mongodb://{db_col_usr}:{db_col_pass}@{db_col_url}:{db_col_port}/' # noqa E501

    mempool_collecotr = MempoolCollector(
                mongo_url=mongo_url,
                db_name=db_col_name,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                interval=0.5,
                verbose=False)
    block_collector = BlockCollector(
                mongo_url=mongo_url,
                db_name=db_col_name,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                interval=3,
                verbose=True)
    mempool_gas_estimator = MemPoolGasEstimator(
                mongo_url=mongo_url,
                db_name=db_col_name,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                interval=3,
                verbose=True)
    collectors = [mempool_collecotr, block_collector, mempool_gas_estimator]

    data_collector = CollectorManager(collectors)
    asyncio.run(data_collector.start())


if __name__ == '__main__':
    main()
