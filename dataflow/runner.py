import os

from pymongo import MongoClient

from metrics_updater import update_metrics
from utils import init_logger

if __name__ == "__main__":
    logger = init_logger()

    MONGO_HOST = os.environ["MONGO_HOST"]
    MONGO_PORT = os.environ["MONGO_PORT"]
    MONGO_USER = os.environ["MONGO_USER"]
    MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]

    mongo_url = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"

    logger.info("Trying to connect to Mongo")
    client = MongoClient(mongo_url)
    logger.info("Connection has been established")

    db = client["censorred"]
    validators = db["validators"]
    validators_metrics = db["validators_metrics"]
    censored_txs = db["censored_txs"]
    prepared_metrics = db["prepared_metrics"]

    logger.info("The metrics update has started")
    update_metrics(
        validators_metrics,
        censored_txs,
        validators,
        prepared_metrics,
        logger,
    )
    logger.info("The metrics update has finished")
