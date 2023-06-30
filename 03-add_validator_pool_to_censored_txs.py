import os
import time
from typing import Dict

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

def main():
    db_anl_url = os.environ.get("db_analytics_url", "localhost")
    db_anl_port = os.environ.get("db_analytics_port", "27017")
    db_anl_usr = os.environ.get("db_analytics_username", "root")
    db_anl_pass = os.environ.get("db_analytics_password", "password")
    db_anl_name = os.environ.get("db_analytics_name", "ethereum_censorship_monitor") # noqa E501
    mongo_analytics_url = f"mongodb://{db_anl_usr}:{db_anl_pass}@{db_anl_url}:{db_anl_port}/" # noqa E501

    mongo_client = MongoClient(mongo_analytics_url)
    db = mongo_client[db_anl_name]
    censored_txs = db["censored_txs"]

    print("unset")
    censored_txs.update_many(
        {},
        {'$unset': {'validator_pool': 1}})

    print("Adding Other")
    censored_txs.update_many(
        {"validator_pool": {"$exists": False},
         "validator": {"$eq": "Other"}},
        {'$set': {'validator_pool': "Other"}})
    print("Adding Unknown")
    censored_txs.update_many(
        {"validator_pool": {"$exists": False},
         "validator": {"$eq": "Unknown"}},
        {'$set': {'validator_pool': "Unknown"}})
    print("Adding Lido")
    censored_txs.update_many(
        {"validator_pool": {"$exists": False},
         "validator": {"$exists": True}},
        {'$set': {'validator_pool': "Lido"}})


if __name__ == "__main__":
    main()
