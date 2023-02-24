import logging
from typing import Tuple

from web3.beacon import Beacon
from pymongo.database import Database
from web3.auto import Web3


logger = logging.getLogger(__name__)


def get_slot_by_block_number(block_number: int,
                             block_ts: int,
                             beacon: Beacon,
                             db: Database) -> int:
    slots_collection = db['block_numbers_slots']
    result = slots_collection.find().sort(
        'block_number', -1).limit(1)
    block_db = [r for r in result]
    if len(block_db) > 0:
        base_slot = block_db[0]['slot_number']
    else:
        base_slot = beacon.get_beacon_state()['data']['latest_block_header']['slot'] # noqa E501
    base_ts = int(beacon.get_block(
        base_slot
    )['data']['message']['body']['execution_payload']['timestamp'])

    ts_diff = base_ts - block_ts
    expected_slot = int(base_slot) - ts_diff // 12

    expected_block_number = int(beacon.get_block(
        expected_slot
    )['data']['message']['body']['execution_payload']['block_number'])
    while expected_block_number > block_number:
        expected_slot -= 1
        expected_block_number = int(beacon.get_block(
            expected_slot
        )['data']['message']['body']['execution_payload']['block_number'])
    while expected_block_number < block_number:
        expected_slot += 1
        expected_block_number = int(beacon.get_block(
            expected_slot
        )['data']['message']['body']['execution_payload']['block_number'])
    assert block_number == expected_block_number
    return expected_slot


def get_slot_with_cache(block_number: int,
                        block_ts: int,
                        beacon: Beacon,
                        w3: Web3,
                        db: Database) -> int:
    slots_collection = db['block_numbers_slots']
    result = slots_collection.find({'block_number': {'$eq': block_number}})
    result_db = [r for r in result]
    if len(result_db) > 0:
        return result_db[0]['slot_number']

    block = w3.eth.getBlock(block_number)
    block_ts = block['timestamp']

    slot = get_slot_by_block_number(block_number, block_ts, beacon, db)
    slots_collection.insert_one({'block_number': block_number,
                                 'slot_number': slot})
    return slot


def get_validator_pubkey(block_number: int,
                         block_ts: int,
                         beacon: Beacon,
                         w3: Web3,
                         db: Database) -> str:
    ''' Get block validator'''
    slot = get_slot_with_cache(block_number, block_ts, beacon, w3, db)
    beacon_block = beacon.get_block(slot)
    beacon_message = beacon_block['data']['message']
    assert block_number == int(
        beacon_message['body']['execution_payload']['block_number'])

    validator_index = beacon_message['proposer_index']
    validator = beacon.get_validator(validator_index)['data']['validator']
    validator_pubkey = validator['pubkey']
    return validator_pubkey


def get_validator_info(validator_pubkey, db: Database) -> Tuple[str, str]:
    validators_collection = db['validators']
    validators_collection.create_index('pubkey', unique=True)
    result = validators_collection.find({'pubkey': {'$eq': validator_pubkey}})
    db_validators = [v for v in result]
    if len(db_validators) == 0:
        validator_pool = 'Other'
        validator_name = 'Other'
    elif len(db_validators) == 1:
        validator_pool = 'Lido'
        validator_info = db_validators[0]
        validator_name = validator_info['name']
    else:
        validator_pool = 'Lido'
        validator_names = [v['name'] for v in db_validators]
        logger.warning((f'Many validators found!: {validator_names} '
                        f'pubkey: {validator_pubkey}'))
        validator_name = validator_names[0]
    return validator_pool, validator_name
