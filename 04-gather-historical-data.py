''' This script is for local use only. It was written ad hoc for
populating historical data
'''

import asyncio
import datetime
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict

import requests
import tqdm
from requests.exceptions import HTTPError
from web3.auto import Web3
from web3.beacon import Beacon

from censorability_monitor.data_collection.utils import split_on_equal_chunks

data_path = Path("historical_data")

# Load data
with open(data_path / "ofac_addresses_json.json", "r") as f:
    ofac_lists = json.load(f)


with open(data_path / "validators.json", "r") as f:
    validators_raw = json.load(f)

validators = {v["pubkey"]: {"pool_name": v["pool_name"], "name": v["name"]}
              for v in validators_raw}

with open(data_path / "block_validators.json", "r") as f:
    block_validators = json.load(f)


w3 = Web3(Web3.IPCProvider(
    "/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc"))
beacon = Beacon("http://localhost:5052")
print("Latest Ethereum block number", w3.eth.blockNumber)


class TXStatusAnalyzer():
    def __init__(self):
        self.web3_url = "/media/Warehouse/Warehouse/Ethereum/data/.ethereum/geth.ipc" # noqa E501

    def check_txs_statuses(self, transactions, current_ofac):
        non_compliant_txs = []
        w3 = Web3(Web3.IPCProvider(self.web3_url))
        for tx in transactions:
            tx_receipt = w3.eth.get_transaction_receipt(tx)
            addresses = get_addresses_from_receipt(tx_receipt)
            ofac_compliance = len(addresses.intersection(current_ofac)) == 0
            if not ofac_compliance:
                non_compliant_txs.append(tx)
        return [tx.hex() for tx in non_compliant_txs]


async def save_historical_data_from_eth_node():
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
        validator_data = validator_metrics[f"{validator_info['pool_name']}_{validator_info['name']}"] # noqa E501
        validator_data["pool"] = validator_info["pool_name"]
        validator_data["name"] = validator_info["name"]

        ts = block["timestamp"]
        dt = datetime.datetime.utcfromtimestamp(ts)
        block_date = dt.strftime('%d-%m-%y')

        if current_block_date != block_date:
            filepath = data_path / f"validators_metrics_gathered_{current_block_date}.json" # noqa E501
            with open(filepath, "w") as f:
                json.dump(validator_metrics, f)
            current_block_date = block_date

        validator_day = validator_data[block_date]
        if "non_censored_blocks" not in validator_day:
            validator_day["non_censored_blocks"] = []
        if "non_ofac_compliant_txs" not in validator_day:
            validator_day["non_ofac_compliant_txs"] = []
        validator_day["num_blocks"] += 1
        # t2 = time.time()

        current_ofac = [a.lower() for a in get_ofac_list_for_timestamp(ts)["addresses"]] # noqa E501
        transactions = block["transactions"]
        validator_day["num_txs"] += len(transactions)

        # t3 = time.time()
        max_workers = 20
        tx_analyzers = [TXStatusAnalyzer() for _ in range(max_workers)]
        chunks = split_on_equal_chunks(transactions, max_workers)
        event_loop = asyncio.get_event_loop()
        process_executor = ProcessPoolExecutor(max_workers=max_workers)
        get_status_tasks = [
            event_loop.run_in_executor(
                process_executor,
                tx_analyzer.check_txs_statuses,
                chunk,
                current_ofac
            )
            for chunk, tx_analyzer in zip(chunks, tx_analyzers)
        ]
        non_compliant_txs = []
        try:
            data = await asyncio.gather(*get_status_tasks)
            for d in data:
                non_compliant_txs.extend(d)
        except Exception as e:
            print(f"Error collecting address data: {e} {type(e)}")
            raise e

        if len(non_compliant_txs) > 0:
            validator_day["non_censored_blocks"].append(block_number)
            validator_day["non_ofac_compliant_txs"].extend(non_compliant_txs)


def check_txs_status(transactions, current_ofac, w3_conn):
    non_compliant_txs = []
    for tx in transactions:
        tx_receipt = w3_conn.eth.get_transaction_receipt(tx)
        addresses = get_addresses_from_receipt(tx_receipt)
        ofac_compliance = len(addresses.intersection(current_ofac)) == 0
        if not ofac_compliance:
            non_compliant_txs.append(tx)
    return [tx.hex() for tx in non_compliant_txs]


def get_ofac_list_for_timestamp(ts: int, ofac_lists=ofac_lists):
    ofac_lists = sorted(ofac_lists, key=lambda x: x["timestamp"])
    i = 0
    while i < len(ofac_lists) and ofac_lists[i]["timestamp"] < ts:
        i += 1
    if i == 0:
        return ofac_lists[0]
    return ofac_lists[i - 1]


def get_block_slot(block: dict, beacon: Beacon,
                   base_slot: int,
                   base_ts: int) -> int:
    block_number = block["number"]
    block_ts = block["timestamp"]
    ts_diff = base_ts - block_ts
    expected_slot = int(base_slot) - ts_diff // 12
    n_attempt = 0
    found_correct_slot = False
    while not found_correct_slot and n_attempt < 100:
        n_attempt += 1
        try:
            expected_block_number = int(beacon.get_block(
                expected_slot
            )["data"]["message"]["body"]["execution_payload"]["block_number"])
            found_correct_slot = True
        except HTTPError:
            expected_slot -= 1

    while expected_block_number > block_number:
        expected_slot -= 1
        try:
            expected_block_number = int(beacon.get_block(
                expected_slot
            )["data"]["message"]["body"]["execution_payload"]["block_number"])
        except HTTPError:
            pass
    while expected_block_number < block_number:
        expected_slot += 1
        try:
            expected_block_number = int(beacon.get_block(
                expected_slot
            )["data"]["message"]["body"]["execution_payload"]["block_number"])
        except HTTPError:
            pass
    assert block_number == expected_block_number
    return expected_slot


def get_slot_validator_pubkey(slot: int,
                              block_number: int,
                              beacon: Beacon,
                              w3: Web3) -> str:
    ''' Get block validator'''
    try:
        beacon_block = beacon.get_block(slot)
    except requests.exceptions.HTTPError:
        return ""
    beacon_message = beacon_block["data"]["message"]
    assert block_number == int(
        beacon_message["body"]["execution_payload"]["block_number"])
    validator_index = beacon_message["proposer_index"]
    validator = beacon.get_validator(validator_index)["data"]["validator"]
    validator_pubkey = validator["pubkey"]
    return validator_pubkey


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
                addresses.add(el.lower())
            elif len_el > 20:
                prefix = el[:len_el - 20]
                if len(prefix) == prefix.count(b'\x00'):
                    addresses.add(el[len_el - 20:].hex().lower())
    addresses_list = [el.lower() for el in addresses]
    receipt_possible_addresses = set(addresses_list)
    receipt_possible_addresses.add(tx_receipt['from'].lower())
    to_addr = tx_receipt['to']
    if to_addr:
        receipt_possible_addresses.add(to_addr.lower())
    return receipt_possible_addresses


if __name__ == "__main__":
    asyncio.run(save_historical_data_from_eth_node())
