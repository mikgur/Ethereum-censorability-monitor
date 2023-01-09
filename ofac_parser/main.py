import urllib.request as req
import re
from typing import List, Dict, Tuple
from datetime import datetime

from pymongo import MongoClient, Database

from cfg import CONNECTION_STRING, TABLE_NAME, OFAC_LIST_URL


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


def list_to_json(banned_wallets: List[str]) -> Dict:
    '''
    Transform list of addresses to json object

    Args:
        banned_wallets: List of banned ETH wallets addresses

    Returns:
        JSON with list of banned wallets
    '''

    return {
        'dt': datetime.utcnow,
        'banned_wallets': banned_wallets
    }


if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    banned_wallets = get_banned_wallets(OFAC_LIST_URL)
    add_res = table.insert_one(list_to_json(banned_wallets))

    print(f'{datetime.utcnow}: Added list of {len(banned_wallets)} banned wallets to db')

    connection.close()
