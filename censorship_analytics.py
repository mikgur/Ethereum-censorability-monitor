import asyncio
import logging
import logging.config

import yaml
from dotenv import load_dotenv

from censorability_monitor.analytics import CensorshipMonitor


load_dotenv()

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def main():
    web3_url = '/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc'
    web3_connection_type = 'ipc'
    mongo_url = 'mongodb://root:YAzV*CUiHakxi!Q2FUmWKaBJ@localhost:27017/'
    mongo_analytics_url = 'mongodb://root:YAzV*CUiHakxi!Q2FUmWKaBJ@localhost:27017/' # noqa E501
    beacon_url = 'http://localhost:5052'
    model_path = 'models/classifier_isotonic_20000_blocks.pkl'

    censorship_monitor = CensorshipMonitor(
                mongo_url=mongo_url,
                mongo_analytics_url=mongo_analytics_url,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                beacon_url=beacon_url,
                model_path=model_path,
                interval=0.5,
                # start_block=16649566,
                start_block=16649641,
                verbose=False)

    asyncio.run(censorship_monitor.run())


if __name__ == '__main__':
    main()
