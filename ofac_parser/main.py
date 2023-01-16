import urllib.request as req
from urllib.error import URLError
import re
from typing import List, Dict, Tuple
from time import time, sleep
import logging
import sys

from pymongo import MongoClient, Collection
from pymongo.errors import ConnectionError, OperationFailure, PyMongoError
import pandas as pd

from cfg import CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME, OFAC_LIST_URL


logger = logging.getLogger()
fileHandler = logging.FileHandler('logs/ofac_parser_logs.log')
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
) -> Tuple[MongoClient, Collection, bool]:
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


def get_banned_wallets(ofac_list_url: str) -> Tuple[List[Dict[str, str]], bool]:
    '''
    Get list of cryptowallets banned by OFAC

    Args:
        ofac_list_url: URL of complete OFAC SDN list

    Returns:
        List of cryptowallets addresses
    '''
    def truncate_address(address: str) -> Dict[str, str]:
        '''
        Truncate cryptowallets addresses

        Args:
            address: Cryptowallet address in format Digital Currency Address - ...;

        Returns:
            Cryptowallet address in format {prefix : address}
        '''
        splitted = address.split(' ')
        prefix = splitted[-2]
        address_ = splitted[-1][:-1]
        return {prefix: address_}

    is_successful = True

    try:
        # Read txt file from OFAC website
        res = req.urlopen(ofac_list_url)
        banlist = str(res.read().decode('utf-8'))
        banlist = banlist.replace('\n', ' ')

        # Regexp to find cryptowallets addresses
        pattern = re.compile('Digital Currency Address - .{20,60};')

        # Find all cryptowallets addresses in document and truncate them
        banned_wallets = re.findall(pattern, banlist)
        banned_wallets = list(map(truncate_address, banned_wallets))
    except URLError as e:
        is_successful = False
        logger.error(f'Urllib exception: {e}')

    return banned_wallets, is_successful


def get_grouped_by_prefixes(banned_wallets: List[Dict[str, str]]) -> Dict:
    '''
    Group all wallets by address prefix

    Args:
        banned_wallets: List of cryptowallets addresses in format {prefix:address}

    Returns:
        Dict in format {wallets: {prefix : list of addresses}, dt: time}
    '''
    wallets = pd.DataFrame(banned_wallets, columns=['Prefix', 'Wallet'])
    grouped_wallets = wallets.groupby('Prefix')['Wallet'].apply(list)
    grouped_wallets = grouped_wallets.to_dict()

    entity = {}
    entity['wallets'] = grouped_wallets
    entity['dt'] = int(time())

    return entity


if __name__ == '__main__':
    is_successful = False

    while not is_successful:
        logging.info('OFAC list parsing has started')

        connection, collection, is_successful = get_mongo_table(
            CONNECTION_STRING, TABLE_NAME, COLLECTION_NAME)
        if not is_successful:
            logging.warning('Parsing has failed. Restart in 1 minute')
            sleep(60)
            continue

        banned_wallets, is_successful = get_banned_wallets(
            OFAC_LIST_URL)
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
