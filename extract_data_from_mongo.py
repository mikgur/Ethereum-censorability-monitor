import logging
import logging.config
import time
from datetime import datetime

import pandas as pd
import tqdm
import yaml
from pymongo import MongoClient
from web3.auto import Web3

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


def find_block_number(web3, timestamp, how=None):
    """
    Find block number for given timestamp
    :param web3:
    :param timestamp:
    :return:
    """
    # Get the block number for the timestamp
    current_time = time.time()
    last_block_number = web3.eth.block_number
    num_blocks_from_current = int((current_time - timestamp) / 12)
    block_number = last_block_number - num_blocks_from_current
    block = web3.eth.get_block(block_number)
    if block['timestamp'] > timestamp:
        while block['timestamp'] > timestamp:
            block_number -= 1
            block = web3.eth.get_block(block_number)
    else:
        while block['timestamp'] < timestamp:
            block_number += 1
            block = web3.eth.get_block(block_number)
    if how == 'before':
        while block['timestamp'] > timestamp:
            block_number -= 1
            block = web3.eth.get_block(block_number)
    elif how == 'after':
        while block['timestamp'] < timestamp:
            block_number += 1
            block = web3.eth.get_block(block_number)
    return block_number


def main():
    geth_ipc = '/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc'
    web3 = Web3(Web3.IPCProvider(geth_ipc))
    last_block_number = web3.eth.block_number
    logging.info(f'Last block number: {last_block_number}')
    current_time = time.time()
    current_time_dt = datetime.fromtimestamp(current_time)
    logging.info(f'Current time: {current_time_dt}, timestamp: {current_time}')

    period_start_dt = datetime.strptime('2022-12-20 00:00:00', '%Y-%m-%d %H:%M:%S')  # noqa E501
    period_start = datetime.timestamp(period_start_dt)
    logging.info(f'period_start: {period_start}')

    period_end_dt = datetime.strptime('2023-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')  # noqa E501
    period_end = datetime.timestamp(period_end_dt)
    logging.info(f'period_end: {period_end}')
    logging.info(f'difference: {period_end - period_start}')

    num_blocks_from_start = int((current_time - period_start) / 12)
    start_block_n = last_block_number - num_blocks_from_start

    start_block_n = find_block_number(web3, period_start, 'after')
    start_block = web3.eth.get_block(start_block_n)
    start_block_dt = datetime.fromtimestamp(start_block['timestamp'])
    logging.info(f'start_block {start_block_dt}, timestamp: {start_block["timestamp"]}')  # noqa E501
    end_block_n = find_block_number(web3, period_end, 'before')
    end_block = web3.eth.get_block(end_block_n)
    end_block_dt = datetime.fromtimestamp(end_block['timestamp'])
    logging.info(f'end_block {end_block_dt}, timestamp: {end_block["timestamp"]}')  # noqa E501

    # Save all transactions between start and end block
    transactions_with_timestamp = []
    for block_number in tqdm.tqdm(range(start_block_n, end_block_n + 1)):
        block = web3.eth.get_block(block_number)
        for tx in block['transactions']:
            tx = web3.eth.get_transaction(tx)
            transactions_with_timestamp.append(
                (tx['hash'].hex(), tx['from'], tx['to'], tx['gas'],
                 tx['gasPrice'],
                 block['number'], block['timestamp'], block['miner'])
                 )
    df = pd.DataFrame(
        transactions_with_timestamp,
        columns=['tx_hash', 'from', 'to', 'gas',
                 'gasPrice', 'blockNumber', 'timestamp', 'miner'])
    df.to_csv('transactions.csv', index=False)

    mongo_url = 'mongodb://root:test_pass@localhost:27017/'
    client = MongoClient(mongo_url)
    db = client['ethereum_mempool']
    first_seen = db['first_seen']

    mongo_transactions = []
    batch_size = 10000
    # Транзакции появляются в мемпуле раньше чем в блокчейне,
    # поэтому берем мемпул с запасом 12 часов
    margin = 60 * 60 * 12  # 12 hours
    for t in tqdm.tqdm(range(int(period_start) - margin,
                             int(period_end),
                             batch_size)):
        result = first_seen.find(
            {"timestamp": {"$gte":  t, "$lt": t + batch_size}})
        for r in result:
            mongo_transactions.append((r['hash'].hex(), r['timestamp']))
    mongo_df = pd.DataFrame(mongo_transactions,
                            columns=['tx_hash', 'timestamp'])
    mongo_df.to_csv('mongo_transactions.csv', index=False)


if __name__ == '__main__':
    main()
