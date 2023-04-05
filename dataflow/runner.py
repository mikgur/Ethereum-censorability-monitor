import os

from pymongo import MongoClient

from metrics_updater import update_metrics

MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]

mongo_url = (
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
)
client = MongoClient(mongo_url)

db = client["censorred"]
validators = db["validators"]
validators_metrics = db["validators_metrics"]
censored_txs = db["censored_txs"]
prepared_metrics = db["prepared_metrics"]

if __name__ == "__main__":
    update_metrics(
        validators_metrics, censored_txs, validators, prepared_metrics
    )
