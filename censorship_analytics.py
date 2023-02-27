import asyncio
import logging
import logging.config
import os

import yaml
from dotenv import load_dotenv

from censorability_monitor.analytics import CensorshipMonitor

load_dotenv()

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def main():
    # web3_url = '/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc'
    web3_url = os.environ.get('node_url', '')
    web3_connection_type = os.environ.get('node_connection_type', '')

    db_col_url = os.environ.get('db_collector_url', 'localhost')
    db_col_port = os.environ.get('db_collector_port', '27017')
    db_col_usr = os.environ.get('db_collector_username', 'root')
    db_col_pass = os.environ.get('db_collector_password', 'password')
    db_col_name = os.environ.get('db_collector_name', 'ethereum_mempool')
    mongo_url = f'mongodb://{db_col_usr}:{db_col_pass}@{db_col_url}:{db_col_port}/' # noqa E501

    db_anl_url = os.environ.get('db_analytics_url', 'localhost')
    db_anl_port = os.environ.get('db_analytics_port', '27017')
    db_anl_usr = os.environ.get('db_analytics_username', 'root')
    db_anl_pass = os.environ.get('db_analytics_password', 'password')
    db_anl_name = os.environ.get('db_analytics_name', 'ethereum_censorship_monitor') # noqa E501
    mongo_analytics_url = f'mongodb://{db_anl_usr}:{db_anl_pass}@{db_anl_url}:{db_anl_port}/' # noqa E501

    beacon_url = os.environ.get('beacon_url', 'http://localhost:5052')
    model_path = os.environ.get('model_path',
                                'models/classifier_isotonic_20000_blocks.pkl')

    censorship_monitor = CensorshipMonitor(
                mongo_url=mongo_url,
                collector_db_name=db_col_name,
                mongo_analytics_url=mongo_analytics_url,
                analytics_db_name=db_anl_name,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                beacon_url=beacon_url,
                model_path=model_path,
                interval=0.5,
                start_block=16649566,  # the earlies block possible to start
                verbose=False)

    asyncio.run(censorship_monitor.run())


if __name__ == '__main__':
    main()
