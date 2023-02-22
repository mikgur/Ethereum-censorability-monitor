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

    censorship_monitor = CensorshipMonitor(
                mongo_url=mongo_url,
                web3_type=web3_connection_type,
                web3_url=web3_url,
                interval=0.5,
                start_block=16649566,
                verbose=False)

    asyncio.run(censorship_monitor.run())


if __name__ == '__main__':
    main()
