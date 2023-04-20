from typing import Any, Dict, List

import numpy as np
import pandas as pd
from pymongo.database import Database
from web3.auto import Web3


def load_mempool_state(db: Database, block_number: int, w3: Web3) -> List[str]:
    first_seen_collection = db['tx_first_seen_ts']
    # first_seen_collection.create_index('timestamp')
    # first_seen_collection.create_index('block_number')
    tx_details_collection = db['tx_details']
    block = w3.eth.getBlock(block_number)
    block_ts = block['timestamp']
    # Get transactions from mempool that are not in the blocks
    # and update them from accounts data
    transactions = first_seen_collection.find(
        {'timestamp': {'$lte': block_ts},
         '$and': [
            {'$or': [{'block_number': {'$exists': False}},
                     {'block_number': {'$gte': block_number}}
                     ]
             },
            {'$or': [{'maxFeePerGas': {'$exists': False}},
                     {'maxFeePerGas': {'$gte': block["baseFeePerGas"]}}
                     ]}
            ]
         })
    mempool_txs = set([tx['hash'] for tx in transactions])

    # Get details
    tx_details_collection = db['tx_details']
    tx_details_db = tx_details_collection.find(
        {'hash': {'$in': list(mempool_txs)}})
    tx_details = {tx['hash']: tx for tx in tx_details_db}

    # Fetch address info
    addresses = set()
    for _, tx in tx_details.items():
        addresses.add(tx['from'])

    accounts_collection = db['addresses_info']
    accounts_details_db = accounts_collection.find(
        {'address': {'$in': list(addresses)}})

    # Берем информацию об аккаунте на предыдущий блок или
    # если недоступно, то на самый поздний из доступных
    block_accounts_info = {}
    for a in accounts_details_db:
        if str(block_number - 1) in a:
            block_accounts_info[a['address']] = {
                'eth': a[str(block_number - 1)]['eth'],
                'n_txs': a[str(block_number - 1)]['n_txs']
            }
            continue
        keys_available = np.array([int(k) for k in a.keys()
                                  if k not in ['_id', 'address']])
        keys = keys_available[keys_available <= block_number]
        if len(keys) == 0:
            continue
        max_key = keys.max()
        block_accounts_info[a['address']] = {
                'eth': a[str(max_key)]['eth'],
                'n_txs': a[str(max_key)]['n_txs']
            }

    # Make df for nonce analysis
    records = []
    for _, tx in tx_details.items():
        records.append({'hash': tx['hash'],
                        'from': tx['from'],
                        'nonce': tx['nonce']})

    tx_df = pd.DataFrame.from_records(records)
    if len(records) == 0:
        return []
    tx_grouped = tx_df.groupby(['from', 'hash']).agg({'nonce': 'first'})

    # Remove transactions that can't be included to block due to high nonce
    all_nonce_blocked = set()
    for addr in tx_df['from'].unique():
        if addr not in block_accounts_info:
            continue
        block_txs = False
        n_txs = block_accounts_info[addr]['n_txs']
        transactions_from_addr = tx_grouped.loc[addr].sort_values(
            'nonce', ascending=True
        ).reset_index()
        for i, row in transactions_from_addr.iterrows():
            if row['nonce'] > n_txs:
                block_txs = True
                break
            n_txs += 1
        if block_txs:
            nonce_blocked = transactions_from_addr['hash'].values[i:]
            all_nonce_blocked.update(nonce_blocked)

    non_blocked = tx_df[~tx_df['hash'].isin(all_nonce_blocked)]
    non_blocked_hashes = non_blocked['hash'].values

    # Remove transactions with not enough value to transfer
    eligible_transactions = []
    for tx_hash in non_blocked_hashes:
        if tx_hash not in tx_details:
            continue
        details = tx_details[tx_hash]
        addr = details['from']
        if addr not in block_accounts_info:
            eligible_transactions.append(tx_hash)
            continue
        if 'value' in details:
            value = int(details['value']) / 10 ** 18
            if value >= block_accounts_info[addr]['eth']:
                continue
        eligible_transactions.append(tx_hash)
    return eligible_transactions


def get_addresses_from_receipt(tx_receipt: Dict[str, Any]) -> set:
    ''' Get addressess touched by transaction
        from tx receip'''
    addresses = set()
    for log in tx_receipt['logs']:
        if 'address' in log:
            addresses.add(log['address'])
        for el in log['topics']:
            len_el = len(el)
            if len_el == 20:
                addresses.add(el)
            elif len_el > 20:
                prefix = el[:len_el - 20]
                if len(prefix) == prefix.count(b'\x00'):
                    addresses.add(el[len_el - 20:].hex())
    addresses_list = [el.lower() for el in addresses]
    receipt_possible_addresses = set(addresses_list)
    receipt_possible_addresses.add(tx_receipt['from'])
    receipt_possible_addresses.add(tx_receipt['to'])
    return receipt_possible_addresses
