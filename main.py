import asyncio
import logging
import logging.config
import time

import yaml
from pymongo import MongoClient
from web3.auto import Web3
from web3.exceptions import TransactionNotFound

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# enter your web socket node credentials here
# this will allow us to stream transactions
geth_ipc = '/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc'
web3 = Web3(Web3.IPCProvider(geth_ipc))


# test to see if you are connected to your node
# this will print out True if you are successfully connected to a node
logger.info(f'Connected to ETH node: {web3.isConnected()}')

mongo_url = 'mongodb://root:test_pass@localhost:27017/'
client = MongoClient(mongo_url)
db = client['ethereum_mempool']
first_seen = db['first_seen']
details = db['details']
accounts = db['account_n_transactions']

not_found_transactions = set()


def handle_event(event):
    # print the transaction hash
    # print(Web3.toJSON(event))
    # use a try / except to have the program continue if there is
    # a bad transaction in the list
    try:
        # remove the quotes in the transaction hash
        transaction_hash = Web3.toJSON(event).strip('"')
        print(transaction_hash)
    except Exception as err:
        # print transactions with errors. Expect to see
        # transactions people submitted with errors
        print(f'error: {err}')


async def log_loop(event_filter, poll_interval):
    while True:
        current_time = int(time.time())
        new_transactions = event_filter.get_new_entries()
        n = len(new_transactions)

        # Insert first_seen
        # Find new transactions
        found_in_db = first_seen.find({"hash": {"$in": new_transactions}})
        hashes_in_db = [d['hash'] for d in found_in_db]
        new_hashes = [h for h in new_transactions if h not in hashes_in_db]
        # Prepare data for insertion
        new_transactions_first_seen = [{'hash': h, 'timestamp': current_time}
                                       for h in new_hashes]
        # Insert new transactions
        if new_transactions_first_seen:
            first_seen.insert_many(new_transactions_first_seen)
        fs_inserted = len(new_transactions_first_seen)

        # Insert details
        # Find new transactions
        found_in_db = details.find({"hash": {"$in": new_transactions}})
        hashes_in_db = [d['hash'] for d in found_in_db]
        new_hashes = [h for h in new_transactions if h not in hashes_in_db]
        # Prepare data for insertion
        new_transactions_data = []
        accounts_n_transactions = []
        for h in new_hashes:
            try:
                transaction = web3.eth.get_transaction(h)
                transaction_dict = dict(**transaction)
                if 'value' in transaction_dict:
                    transaction_dict['value'] = str(transaction_dict['value'])
                new_transactions_data.append(transaction_dict)
                # Add account current n transactions:
                acc_n_transactions = web3.eth.get_transaction_count(
                    transaction['from'])
                accounts_n_transactions.append(
                    {'hash': h,
                     'account': transaction_dict['from'],
                     'n_transactions': acc_n_transactions})
            except TransactionNotFound:
                not_found_transactions.add((h, current_time))
            except Exception as err:
                logger.info(f'Error during fetching details: {err}')
        # Insert new transactions
        if new_transactions_data:
            details.insert_many(new_transactions_data)
        d_inserted = len(new_transactions_data)

        # Insert account n transactions
        if accounts_n_transactions:
            accounts.insert_many(accounts_n_transactions)
        # n_accounts_inserted = len(accounts_n_transactions)

        # Try to fetch details for not found transactions
        new_transactions_data = []
        accounts_n_transactions = []
        remove_from_not_found_list = set()
        for h, t in not_found_transactions:
            try:
                transaction = web3.eth.get_transaction(h)
                transaction_dict = dict(**transaction)
                if 'value' in transaction_dict:
                    transaction_dict['value'] = str(transaction_dict['value'])
                new_transactions_data.append(transaction_dict)
                remove_from_not_found_list.add((h, t))

                # Add account current n transactions:
                acc_n_transactions = web3.eth.get_transaction_count(
                    transaction['from'])
                accounts_n_transactions.append(
                    {'hash': h,
                     'account': transaction_dict['from'],
                     'n_transactions': acc_n_transactions})

            except TransactionNotFound:
                pass
            except Exception as err:
                logger.info(f'Error during fetching details: {err}')
                remove_from_not_found_list.add((h, t))
            if current_time - t > 60:
                remove_from_not_found_list.add((h, t))
        # Insert new transactions
        if new_transactions_data:
            details.insert_many(new_transactions_data)
        nf_inserted = len(new_transactions_data)

        # Insert account n transactions
        if accounts_n_transactions:
            accounts.insert_many(accounts_n_transactions)
        # nf_accounts_inserted = len(accounts_n_transactions)

        # Remove from not found list
        not_found_transactions.difference_update(remove_from_not_found_list)
        n_old = len(remove_from_not_found_list) - nf_inserted

        n_not_found = len(not_found_transactions)

        logger.info(f'Hashes: {fs_inserted:4} Details: {d_inserted:4} Total: {n:4} Found: {nf_inserted:4} Not found: {n_not_found:4} Old removed: {n_old:4}') # noqa E501

        # for event in event_filter.get_new_entries():
        #     handle_event(event)
        await asyncio.sleep(poll_interval)


def main():
    # filter for pending transactions
    tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(tx_filter, 0.5)))
    finally:
        loop.close()


if __name__ == '__main__':
    main()
