from time import sleep
import logging
import sys

from pymongo.errors import OperationFailure, PyMongoError

from cfg import CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, OFAC_LIST_URL
from utils import get_mongo_collection, get_banned_wallets, get_grouped_by_prefixes


if __name__ == '__main__':
    is_successful = False
    # logging stuff
    logger = logging.getLogger()
    fileHandler = logging.FileHandler('logs/ofac_parser_logs.log')
    fileHandler.setFormatter(logging.Formatter(
        fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(fileHandler)
    streamHandler = logging.StreamHandler(stream=sys.stdout)
    streamHandler.setFormatter(logging.Formatter(
        fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(streamHandler)

    while not is_successful:
        logging.info('OFAC list parsing has started')

        connection, collection, is_successful = get_mongo_collection(
            CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, logger)
        if not is_successful:
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        banned_wallets, is_successful = get_banned_wallets(
            OFAC_LIST_URL, logger)
        if not is_successful:
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        try:
            collection.insert_one(get_grouped_by_prefixes(banned_wallets))
        except OperationFailure as ope:
            logging.error(f'Insertion error: {ope}')
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue
        except PyMongoError as e:
            logging.error(f'PyMongo error: {e}')
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        logging.info(
            f'Added list of {len(banned_wallets)} banned wallets to db')
        logging.info('OFAC parsing has successfully completed')

        connection.close()
        logging.info('DB connection has closed')

        is_successful = True
