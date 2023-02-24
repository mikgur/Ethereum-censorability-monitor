import re
import time
import urllib.request as req
from urllib.error import URLError

import pandas as pd


def get_banned_wallets(ofac_list_url: str):
    '''
    Get list of cryptowallets banned by OFAC
    Args:
        ofac_list_url:  URL of complete OFAC SDN list
        logger:         Logger
    Returns:
        List of cryptowallets addresses
    '''
    def truncate_address(address: str):
        '''
        Truncate cryptowallets addresses
        Args:
            address: Cryptowallet address in format
            Digital Currency Address - ...;
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
        print(e)
        is_successful = False

    return banned_wallets, is_successful


def get_grouped_by_prefixes(banned_wallets):
    '''
    Group all wallets by address prefix
    Args:
        banned_wallets: List of cryptowallets addresses
        in format {prefix:address}
    Returns:
        Dict in format {wallets: {prefix : list of addresses}, dt: time}
    '''
    wallets = pd.DataFrame([[(k, v) for k, v in el.items()][0]
                            for el in banned_wallets],
                           columns=['Prefix', 'Wallet'])
    grouped_wallets = wallets.groupby('Prefix')['Wallet'].apply(list)
    grouped_wallets = grouped_wallets.to_dict()

    entity = {}
    entity['wallets'] = grouped_wallets
    entity['dt'] = int(time.time())

    return entity
