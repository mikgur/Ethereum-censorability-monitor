''' This script is for local use only. It was written ad hoc for
populating historical data
'''

import datetime
import json
from collections import defaultdict
import os
from pathlib import Path

from dotenv import load_dotenv
import tqdm
from web3.auto import Web3
from web3.beacon import Beacon

from pymongo import MongoClient

load_dotenv()

DB_USR = os.environ.get('db_collector_username', '')
DB_PASS = os.environ.get('db_collector_password', '')
DB_URL = os.environ.get('db_collector_url', '')
DB_PORT = os.environ.get('db_collector_port', '')

data_path = Path("historical_data")


with open(data_path / "validators.json", "r") as f:
    validators_raw = json.load(f)

validators = {v["pubkey"]: {"pool_name": v["pool_name"], "name": v["name"]}
              for v in validators_raw}

with open(data_path / "block_validators.json", "r") as f:
    block_validators = json.load(f)

mongo_url = f'mongodb://{DB_USR}:{DB_PASS}@{DB_URL}:{DB_PORT}/'
mongo_client = MongoClient(mongo_url)
db = mongo_client["blocks_info"]
blocks_collection = db["blocks"]

w3 = Web3(Web3.IPCProvider(
    "/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc"))
beacon = Beacon("http://localhost:5052")
print("Latest Ethereum block number", w3.eth.blockNumber)


def save_historical_data_from_eth_node():
    first_pos_block = 15537394
    last_block = max([int(a) for a in block_validators.keys()])
    block = w3.eth.getBlock(first_pos_block)
    ts = block["timestamp"]
    dt = datetime.datetime.utcfromtimestamp(ts)
    current_block_date = dt.strftime('%d-%m-%y')

    validator_metrics = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: int())))
    print(f"from {first_pos_block} to {last_block}")
    for block_number in tqdm.tqdm(range(first_pos_block, last_block)):
        block = w3.eth.getBlock(block_number)
        pub_key = block_validators[str(block_number)]
        validator_info = validators.get(pub_key, {"pool_name": "Other",
                                                  "name": "Other"})

        ts = block["timestamp"]
        dt = datetime.datetime.utcfromtimestamp(ts)
        block_date = dt.strftime('%d-%m-%y')

        if current_block_date != block_date:
            filepath = data_path / f"validators_metrics_gathered_{current_block_date}.json" # noqa E501
            with open(filepath, "w") as f:
                json.dump(validator_metrics, f)
            current_block_date = block_date

        transactions = block["transactions"]
        block_info = {
            "block_number": block_number,
            "timestamp": ts,
            "day": current_block_date,
            "pub_key": pub_key,
            "validator_name": validator_info["name"],
            "validator_pool": validator_info["pool_name"],
            "transactions": list([tx.hex() for tx in transactions])
        }
        blocks_collection.insert_one(block_info)


if __name__ == "__main__":
    save_historical_data_from_eth_node()
