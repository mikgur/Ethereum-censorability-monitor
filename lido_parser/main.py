from typing import List, Dict, Tuple

from pymongo import MongoClient, Database
from web3 import Web3
from lido_sdk import Lido

from cfg import CONNECTION_STRING, TABLE_NAME, INFURA_PROJECT_ID


def get_mongo_table(connection_string: str, table_name: str) -> Tuple[MongoClient, Database]:
    '''
    Get MongoDB connection and table

    Args:
        connection_string:  Connection string of the MongoDB
        table_name:         Name of table inside MongoDB

    Returns:
        Connection object and the instance of required table     
    '''
    client = MongoClient(connection_string)
    return client, client[f'{table_name}']


def get_lido_validators(infura_project_id: str) -> List[str]:
    '''
    Get list of LIDO validators wallets

    Args:
        infura_project_id: API key for Infura

    Returns:
        List of LIDO validators' ETH wallets addresses   
    '''

    # Connect to Infura API
    w3 = Web3(Web3.HTTPProvider(
        f'https://mainnet.infura.io/v3/{infura_project_id}'))
    lido = Lido(w3)

    # Get list of indexes of LIDO validators
    indexes = lido.get_operators_indexes()
    # Get validators data
    validators_data = lido.get_operators_data(indexes)

    wallets = [validator['rewardAddress'] for validator in validators_data]

    return wallets


def list_to_json(validators_wallets: List[str]) -> List[Dict]:
    '''
    Transform list of addresses to list of json objects

    Args:
        validators_wallets: List of LIDO validators' ETH wallets addresses

    Returns:
        List of LIDO validators' ETH wallets addresses in json format
    '''
    def wrapper(wallet: str) -> Dict:
        '''
        Wrap wallet address in json

        Args:
            wallet: ETH wallet address

        Returns:
            Wrapped address
        '''
        return {'eth_wallet_address': wallet}

    return list(map(wrapper, validators_wallets))


def get_difference(table: Database, validators_wallets: List[str]) -> Tuple[List[str], List[str]]:
    '''
    Get difference between addressed in db table and current list of LIDO validators

    Args:
        table:              Instance of db table
        validators_wallets: List of LIDO validators' ETH wallets addresses

    Returns:
        Lists of wallets addressed to drop from table and to add to it
    '''
    # Get all records from table
    cursor = table.find({})
    wallets_in_table = cursor.distinct('eth_wallet_address')

    # Find difference between lists
    wallets_to_drop = list(set(validators_wallets) - set(wallets_in_table))
    wallets_to_add = list(set(wallets_in_table) - set(validators_wallets))

    return wallets_to_drop, wallets_to_add


if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    validators_wallets = get_lido_validators(INFURA_PROJECT_ID)
    wallets_to_drop, wallets_to_add = get_difference(table, validators_wallets)
    drop_res = table.delete_many(list_to_json(wallets_to_drop))
    add_res = table.insert_many(list_to_json(wallets_to_add))

    print(f'Deleted {drop_res.deleted_count} wallets to db')
    print(f'Added {len(add_res.inserted_ids)} wallets to db')

    connection.close()
