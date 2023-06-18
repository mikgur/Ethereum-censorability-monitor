import asyncio
import logging
import logging.config
from pathlib import Path
import os

import yaml
from dotenv import load_dotenv
from prometheus_client import start_http_server

from censorability_monitor.data_collection import MemPoolGasEstimator

load_dotenv()

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

start_http_server(8000)


def main():
    web3_url = os.environ.get('node_url', '')
    web3_connection_type = os.environ.get('node_connection_type', '')

    db_col_url = os.environ.get('db_collector_url', 'localhost')
    db_col_port = os.environ.get('db_collector_port', '27017')
    db_col_usr = os.environ.get('db_collector_username', 'root')
    db_col_pass = os.environ.get('db_collector_password', 'password')
    db_col_name = os.environ.get('db_collector_name', 'ethereum_mempool')
    mongo_url = f'mongodb://{db_col_usr}:{db_col_pass}@{db_col_url}:{db_col_port}/' # noqa E501

    mempool_gas_estimator = MemPoolGasEstimator(
                mongo_url=mongo_url,
                db_name=db_col_name,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                interval=6,
                verbose=True)
    asyncio.run(mempool_gas_estimator.collect())


if __name__ == '__main__':
    main()
