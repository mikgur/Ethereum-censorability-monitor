from time import sleep
import logging
import sys

from pymongo.errors import OperationFailure, PyMongoError

from cfg import CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, NODE_CONNECTION_STRING
from utils import get_mongo_collection, get_lido_validators, list_to_json


if __name__ == '__main__':
    is_successful = False
    # Logging stuff
    logger = logging.getLogger()
    fileHandler = logging.FileHandler('logs/lido_parser_logs.log')
    fileHandler.setFormatter(logging.Formatter(
        fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(fileHandler)
    streamHandler = logging.StreamHandler(stream=sys.stdout)
    streamHandler.setFormatter(logging.Formatter(
        fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(streamHandler)

    while not is_successful:
        logger.info('LIDO parsing has started')

        connection, table, is_successful = get_mongo_collection(
            CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, logger)
        if not is_successful:
            logger.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        validators_wallets, is_successful = get_lido_validators(
            NODE_CONNECTION_STRING, logger)
        if not is_successful:
            logger.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        try:
            table.insert_one(list_to_json(validators_wallets))
        except OperationFailure as ope:
            logger.error(f'Insertion error: {ope}')
            logger.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue
        except PyMongoError as e:
            logger.error(f'PyMongo error: {e}')
            logger.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        logger.info(
            f'Added list of {len(validators_wallets)} LIDO validators wallets to db')
        logger.info('LIDO parsing has successfully completed')

        connection.close()
        logger.info('DB connection has closed')

        is_successful = True
