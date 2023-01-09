from typing import List, Dict, Tuple
from datetime import datetime

from pymongo import MongoClient, Database
from web3 import Web3
from lido_sdk import Lido

from cfg import CONNECTION_STRING, TABLE_NAME, NODE_CONNECTION_STRING


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


def get_lido_validators(node_connection_string: str) -> List[str]:
    '''
    Get list of LIDO validators wallets

    Args:
        node_connection_string: Connection string of ETH node

    Returns:
        List of LIDO validators' ETH wallets addresses   
    '''

    # Connect to ETH Node
    w3 = Web3(Web3.HTTPProvider(
        f'{node_connection_string}'))
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
        return {
            'eth_wallet_address': wallet,
            'addition_date': datetime.now(),
            'delition_date': None
        }

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
    # Get all active records from table
    cursor = table.find({}).where('this.delition_date == null')
    active_wallets_in_table = cursor.distinct('eth_wallet_address')

    # Find difference between lists
    wallets_to_drop = list(set(active_wallets_in_table) - set(validators_wallets))
    wallets_to_add = list(set(validators_wallets) - set(active_wallets_in_table))

    return wallets_to_drop, wallets_to_add


def make_inactive(table: Database, wallets_to_drop: List[str]) -> int:
    '''
    Make wallet inactive

    Args:
        table:              Instance of db table
        wallets_to_drop:    List of LIDO validators' ETH wallets addresses to make inactive

    Returns:
        Count of wallets were made inactive
    '''
    cursor = table.find({})
    deleted_count = 0
    
    for wallet in wallets_to_drop:
        wallet_id = cursor.where(f'this.delition_date == null && this.eth_wallet_address == {wallet}').distinct('_id')
        table.update_one({'_id' : wallet_id}, {'$set': {'delition_date': datetime.now()}})   
        
        deleted_count += 1     
        
    return(deleted_count)



if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    validators_wallets = get_lido_validators(NODE_CONNECTION_STRING)
    wallets_to_drop, wallets_to_add = get_difference(table, validators_wallets)
    drop_res = make_inactive(wallets_to_drop)
    add_res = table.insert_many(list_to_json(wallets_to_add))

    print(f'{drop_res} wallets were made inactive')
    print(f'Added {len(add_res.inserted_ids)} active wallets to db')

    connection.close()
