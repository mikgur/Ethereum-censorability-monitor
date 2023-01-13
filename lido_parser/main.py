from typing import List, Dict, Tuple
from datetime import datetime

from pymongo import MongoClient, Database
from web3 import Web3
from lido_sdk import Lido

from cfg import CONNECTION_STRING, TABLE_NAME, NODE_CONNECTION_STRING


def get_mongo_table(
    connection_string: str,
    table_name: str
) -> Tuple[MongoClient, Database]:
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


def list_to_json(validators_wallets: List[str]) -> Dict:
    '''
    Transform list of addresses to json object

    Args:
        validators_wallets: List of LIDO validators' ETH wallets addresses

    Returns:
        JSON with list of LIDO validators' ETH wallets addresses
    '''

    return {
        'dt': datetime.utcnow,
        'lido_validators': validators_wallets
    }


if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    validators_wallets = get_lido_validators(NODE_CONNECTION_STRING)
    table.insert_one(list_to_json(validators_wallets))

    print(f'{datetime.utcnow}: Added list of {len(validators_wallets)} LIDO validators wallets to db')

    connection.close()
