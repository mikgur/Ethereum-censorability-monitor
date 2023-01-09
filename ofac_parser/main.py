import urllib.request as req
import re
from typing import List, Dict, Tuple
from datetime import datetime

from pymongo import MongoClient, Database

from cfg import CONNECTION_STRING, TABLE_NAME, OFAC_LIST_URL


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


def get_banned_wallets(ofac_list_url: str) -> List[str]:
    '''
    Get list of ETH wallets banned by OFAC

    Args:
        ofac_list_url: URL of complete OFAC SDN list 

    Returns:
        List of ETH wallets addresses   
    '''
    def truncate_address(address: str) -> str:
        '''
        Truncate ETH wallets addresses

        Args:
            address: ETH wallet address in format ETH 0x...;

        Returns:
            ETH wallet address in format 0x...
        '''
        return address[4:-1]

    # Read txt file from OFAC website
    res = req.urlopen(ofac_list_url)
    banlist = res.read().decode('utf-8')

    # Regexp to find ETH wallets addresses
    pattern = re.compile('ETH 0x.{40};')

    # Find all ETH wallets addresses in document and truncate them
    banned_wallets = re.findall(pattern, banlist)
    banned_wallets = list(map(truncate_address, banned_wallets))

    return banned_wallets


def list_to_json(banned_wallets: List[str]) -> List[Dict]:
    '''
    Transform list of addresses to list of json objects

    Args:
        banned_wallets: List of banned ETH wallets addresses

    Returns:
        List of banned ETH wallets addresses in json format
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

    return list(map(wrapper, banned_wallets))


def get_difference(table: Database, banned_wallets: List[str]) -> Tuple[List[str], List[str]]:
    '''
    Get difference between addressed in db table and current banlist

    Args:
        table:          Instance of db table
        banned_wallets: List of banned wallets addressed

    Returns:
        Lists of wallets addressed to drop from table and to add to it
    '''
    # Get all active records from table
    cursor = table.find({}).where('this.delition_date == null')
    active_wallets_in_table = cursor.distinct('eth_wallet_address')

    # Find difference between lists
    wallets_to_drop = list(
        set(active_wallets_in_table) - set(banned_wallets))
    wallets_to_add = list(set(banned_wallets) -
                          set(active_wallets_in_table))

    return wallets_to_drop, wallets_to_add

def make_inactive(table: Database, wallets_to_drop: List[str]) -> int:
    '''
    Make wallet inactive

    Args:
        table:              Instance of db table
        wallets_to_drop:    List of banned validators' ETH wallets addresses to make inactive

    Returns:
        Count of wallets were made inactive
    '''
    cursor = table.find({})
    deleted_count = 0

    for wallet in wallets_to_drop:
        wallet_id = cursor.where(
            f'this.delition_date == null && this.eth_wallet_address == {wallet}').distinct('_id')
        table.update_one({'_id': wallet_id}, {
                         '$set': {'delition_date': datetime.now()}})

        deleted_count += 1

    return(deleted_count)

if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    banned_wallets = get_banned_wallets(OFAC_LIST_URL)
    wallets_to_drop, wallets_to_add = get_difference(table, banned_wallets)
    drop_res = make_inactive(wallets_to_drop)
    add_res = table.insert_many(list_to_json(wallets_to_add))

    print(f'{drop_res} wallets were made inactive')
    print(f'Added {len(add_res.inserted_ids)} active wallets to db')

    connection.close()
