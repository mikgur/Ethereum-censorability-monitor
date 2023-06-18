import os
import time
from typing import Dict

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

def main():
    data_path = os.environ.get("validators_data_path")
    data = pd.read_csv(data_path, compression="gzip")

    db_anl_url = os.environ.get('db_analytics_url', 'localhost')
    db_anl_port = os.environ.get('db_analytics_port', '27017')
    db_anl_usr = os.environ.get('db_analytics_username', 'root')
    db_anl_pass = os.environ.get('db_analytics_password', 'password')
    db_anl_name = os.environ.get('db_analytics_name', 'ethereum_censorship_monitor') # noqa E501
    mongo_analytics_url = f'mongodb://{db_anl_usr}:{db_anl_pass}@{db_anl_url}:{db_anl_port}/' # noqa E501

    mongo_client = MongoClient(mongo_analytics_url)
    db = mongo_client[db_anl_name]

    key_to_validator = {el["pubkey"]: el["label"] for _, el in data.iterrows()}
    validators_collection = db['validators']
    validators_db = validators_collection.find()
    validators = set([a['pubkey'] for a in validators_db])
    records = []
    current_time = int(time.time())
    for k, v in key_to_validator.items():
        if k in validators:
            continue
        record = {
            'pubkey': k,
            'pool_name': v,
            'name': v,
            'timestamp': current_time
        }
        records.append(record)
    print(f'Add {len(records)} new validators to db')
    if len(records) > 0:
        validators_collection.insert_many(records)


if __name__ == "__main__":
    main()
