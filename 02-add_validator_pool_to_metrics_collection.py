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
    validators_collection = db["validators_metrics"]
    names = [el["name"] for el in validators_collection.find()]

    for name in names:
        new_name = "Other" if name == "Other" else "Lido"
        validators_collection.update_one(
            {"name": {"$eq": name}},
            {"$set": {"pool": new_name}},
            upsert=False)


if __name__ == "__main__":
    main()
