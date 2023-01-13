import urllib.request as req
import re
from typing import List, Dict, Tuple
from datetime import datetime

from pymongo import MongoClient, Database
import pandas as pd

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


def get_banned_wallets(ofac_list_url: str) -> List[Dict[str, str]]:
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

    # Read txt file from OFAC website
    res = req.urlopen(ofac_list_url)
    banlist = str(res.read().decode('utf-8'))
    banlist = banlist.replace('\n', ' ')

    # Regexp to find cryptowallets addresses
    pattern = re.compile('Digital Currency Address - .{20,60};')

    # Find all cryptowallets addresses in document and truncate them
    banned_wallets = re.findall(pattern, banlist)
    banned_wallets = list(map(truncate_address, banned_wallets))

    return banned_wallets

def get_grouped_by_prefixes(banned_wallets: List[Dict[str, str]]) -> Dict:
    '''
    Group all wallets by address prefix
    
    Args:
        banned_wallets: List of cryptowallets addresses in format {prefix:address}

    Returns:
        Dict in format {prefix : list of addresses}
    '''
    wallets = pd.DataFrame(banned_wallets, columns=['Prefix', 'Wallet'])
    grouped_wallets = wallets.groupby('Prefix')['Wallet'].apply(list)
    grouped_wallets = grouped_wallets.to_dict()
    grouped_wallets['dt'] = str(datetime.utcnow())
    
    return grouped_wallets

if __name__ == '__main__':
    connection, table = get_mongo_table(CONNECTION_STRING, TABLE_NAME)
    banned_wallets = get_banned_wallets(OFAC_LIST_URL)
    add_res = table.insert_one(get_grouped_by_prefixes(banned_wallets))

    print(f'{datetime.utcnow}: Added list of {len(banned_wallets)} banned wallets to db')

    connection.close()
