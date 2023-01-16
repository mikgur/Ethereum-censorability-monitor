from typing import List, Dict, Tuple
from time import time, sleep
import logging
import sys

from pymongo import MongoClient, Database
from pymongo.errors import ConnectionError, OperationFailure, PyMongoError
from web3 import Web3
from web3.exceptions import Web3Exception
from lido_sdk import Lido, LidoException

from cfg import CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, NODE_CONNECTION_STRING


logger = logging.getLogger()
fileHandler = logging.FileHandler('logs/lido_parser_logs.log')
fileHandler.setFormatter(logging.Formatter(
    fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(fileHandler)
streamHandler = logging.StreamHandler(stream=sys.stdout)
streamHandler.setFormatter(logging.Formatter(
    fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(streamHandler)


def get_mongo_table(
    connection_string: str,
    table_name: str,
    collection_name: str
) -> Tuple[MongoClient, Database, bool]:
    '''
    Get MongoDB connection and table

    Args:
        connection_string:  Connection string of the MongoDB
        table_name:         Name of table inside MongoDB
        collection_name:    Name of collection inside table

    Returns:
        Connection object and the instance of required table
    '''
    client, collection, is_successful = None, None, True

    try:
        client = MongoClient(connection_string)
        collection = client[f'{table_name}'][f'{collection_name}']
        logging.info('DB connection has opened successfully')
    except ConnectionError as e:
        is_successful = False
        logging.error(f'Connection error: {e}')

    return client, collection, is_successful


def get_lido_validators(node_connection_string: str) -> Tuple[List[str], bool]:
    '''
    Get list of LIDO validators wallets

    Args:
        node_connection_string: Connection string of ETH node

    Returns:
        List of LIDO validators' ETH wallets addresses
    '''
    wallets, is_successful = None, True

    try:
        # Connect to ETH Node
        w3 = Web3(Web3.HTTPProvider(
            f'{node_connection_string}'))
        try:
            lido = Lido(w3)
            # Get list of indexes of LIDO validators
            indexes = lido.get_operators_indexes()
            # Get validators data
            validators_data = lido.get_operators_data(indexes)

            wallets = [validator['rewardAddress']
                       for validator in validators_data]
        except LidoException as le:
            is_successful = False
            logger.error(f'LIDO exception: {le}')

    except Web3Exception as w3e:
        is_successful = False
        logger.error(f'Web3 exception: {w3e}')

    return wallets, is_successful


def list_to_json(validators_wallets: List[str]) -> Dict:
    '''
    Transform list of addresses to json object

    Args:
        validators_wallets: List of LIDO validators' ETH wallets addresses

    Returns:
        JSON with list of LIDO validators' ETH wallets addresses
    '''

    return {
        'dt': time(),
        'lido_validators': validators_wallets
    }


if __name__ == '__main__':
    is_successful = False

    while not is_successful:
        logging.info('LIDO parsing has started')

        connection, table, is_successful = get_mongo_table(
            CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME)
        if not is_successful:
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        validators_wallets, is_successful = get_lido_validators(
            NODE_CONNECTION_STRING)
        if not is_successful:
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        try:
            table.insert_one(list_to_json(validators_wallets))
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
            f'Added list of {len(validators_wallets)} LIDO validators wallets to db')
        logging.info('LIDO parsing has successfully completed')

        connection.close()
        logging.info('DB connection has closed')

        is_successful = True
