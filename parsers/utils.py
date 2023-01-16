from typing import List, Dict, Tuple
from logging import Logger
from time import time
import urllib.request as req
from urllib.error import URLError
import re

from pymongo.errors import ConnectionError
from web3 import Web3
from web3.exceptions import Web3Exception
from lido_sdk import Lido, LidoException
from pymongo import MongoClient, Collection
import pandas as pd


def get_mongo_collection(
    connection_string: str,
    table_name: str,
    collection_name: str,
    logger: Logger
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
        logger.info('DB connection has opened successfully')
    except ConnectionError as e:
        is_successful = False
        logger.error(f'Connection error: {e}')

    return client, collection, is_successful

def get_lido_validators(node_connection_string: str, logger: Logger) -> Tuple[List[str], bool]:
    '''
    Get list of LIDO validators wallets

    Args:
        node_connection_string: Connection string of ETH node
        logger:                 Logger 

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
    
def get_banned_wallets(ofac_list_url: str, logger: Logger) -> Tuple[List[Dict[str, str]], bool]:
    '''
    Get list of cryptowallets banned by OFAC

    Args:
        ofac_list_url:  URL of complete OFAC SDN list
        logger:         Logger

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