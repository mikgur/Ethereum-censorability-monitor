from typing import List

import numpy as np
import pandas as pd
from pymongo.database import Database
from web3.auto import Web3


def load_mempool_state(db: Database, block_number: int, w3: Web3) -> List[str]:
    first_seen_collection = db['tx_first_seen_ts']
    tx_details_collection = db['tx_details']
    block = w3.eth.getBlock(block_number)
    block_ts = block['timestamp']
    # Get transactions from mempool that are not in the blocks
    # and update their from accounts data
    transactions = first_seen_collection.find(
        {'timestamp': {'$lte': block_ts},
         '$or': [{'block_number': {'$exists': False}},
                 {'block_number': {'$gte': block_number}}]
         })
    # Get mempool accounts and remove old txs without details
    n_mempool_txs = 0
    # Get list of interesting transactions
    mempool_txs = set()
    for tx in transactions:
        n_mempool_txs += 1
        # check that tx maxGasPrice is higher than blocks BaseFeePerGas
        if ('maxFeePerGas' in tx
                and tx['maxFeePerGas'] < block['baseFeePerGas']):
            continue
        # Put into list for gas estimation
        mempool_txs.add(tx['hash'])

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

    # block_accounts_info = {
    #     a['address']: {
    #                     'eth': a[str(block_number - 1)]['eth'],
    #                     'n_txs': a[str(block_number - 1)]['n_txs']
    #                    }
    #     for a in accounts_details_db
    #     if str(block_number - 1) in a}

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
