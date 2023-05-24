import os

from pymongo import MongoClient
from pymongo.collection import Collection

API_HOST = os.environ["API_HOST"]
API_PORT = os.environ["API_PORT"]
MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
AUTH_KEY = os.environ["AUTH_KEY"]


collections = {}


def load_mongo_collections() -> None:
    """
    Connect to MongoDB and load collections
    """
    mongo_url = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
    client: MongoClient = MongoClient(mongo_url)

    db = client["ethereum_censorship_monitor"]
    collections["validators"] = db["validators"]
    collections["validators_metrics"] = db["validators_metrics"]
    collections["censored_txs"] = db["censored_txs"]
    collections["ofac_list"] = db["ofac_addresses"]
    collections["prepared_metrics"] = db["prepared_metrics"]


def get_collection(collection_name: str) -> Collection:
    """
    Get specific collection
    """

    try:
        collection = collections[collection_name]
    except KeyError as err:
        raise err

    return collection
