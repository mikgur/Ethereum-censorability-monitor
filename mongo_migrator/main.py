from pymongo import MongoClient

import os
import json


MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = os.environ['MONGO_PORT']
MONGO_USER = os.environ['MONGO_USER']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']

if __name__ == '__main__':
    mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'
    client = MongoClient(mongo_url)

    db = client['censorred']
    validators_collection = db['validators']
    validators_metrics_collection = db['validators_metrics']

    if (validators_metrics_collection.count_documents({}) == 0):
        with open('collections/validators.json', 'r') as val_file:
            validators = json.load(val_file)
        
        validators = [{key : val for key, val in record.items() if key != '_id'} for record in validators]

        validators_collection.insert_many(validators)

    if (validators_collection.count_documents({}) == 0):
        with open('collections/validators_metrics.json', 'r') as metrics_file:
            validators_metrics = json.load(metrics_file)
        
        validators_metrics = [{key : val for key, val in record.items() if key != '_id'} for record in validators_metrics]

        validators_metrics_collection.insert_many(validators_metrics)