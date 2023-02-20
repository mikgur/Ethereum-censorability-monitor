from fastapi import FastAPI, Query
import uvicorn
from pymongo import MongoClient

import os
from typing import List, Union
import json

from metrics import get_lido_validators_metrics, get_lido_vs_rest
import data

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = 'root'
MONGO_PASSWORD = '3akFUZ8x'
API_HOST = '127.0.0.1'
API_PORT = 8000

# API_HOST = os.environ['API_HOST']
# API_PORT = os.environ['API_PORT']
# MONGO_HOST = os.environ['MONGO_HOST']
# MONGO_PORT = os.environ['MONGO_PORT']
# MONGO_USER = os.environ['MONGO_USER']
# MONGO_PASSWORD = os.environ['MONGO_PASSWORD']

app = FastAPI()

mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'
client = MongoClient(mongo_url)

db = client['censorred']
validators = db['validators']
validators_metrics = db['validator_metrics']


@app.get("/metrics/lido_validators_share/{period}")
async def get_lido_validators_share(period:str) -> str:  
    return get_lido_validators_metrics(validators_metrics, period, False)

@app.get('/metrics/lido_validators_ratio/{period}')
async def get_lido_validators_ratio(period:str) -> str:
    return get_lido_validators_metrics(validators_metrics, period, True)

@app.get('/metrics/lido_vs_rest_share/{period}')
async def get_total_validators_ratio(period:str) -> str:
    return  get_lido_vs_rest(validators_metrics, period)

@app.get('/data/validators')
async def get_validators() -> str:
    cursor = validators.find({}, {'_id': 0})

    return json.dumps(list(cursor))

@app.get('/data/metrics_by_day')
async def get_metrics_by_date(date: str) -> str:
    metrics = data.get_metrics_by_day(validators_metrics, date)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validator')
async def get_metrics_by_validator(name: str) -> str:
    metrics = data.get_metrics_by_validator(validators_metrics, name)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validators')
#TODO: fix
async def get_metrics_by_validators(names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators(validators_metrics, names)
    return json.dumps(metrics)

@app.get('/data/metrics_by_daterange')
async def get_metrics_by_daterange(start_date: str, end_date: str) -> str:
    metrics = data.get_metrics_by_daterange(validators_metrics, start_date, end_date)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validator_by_day')
async def get_metrics_by_validator_by_day(name: str, date: str) -> str:
    metrics = data.get_metrics_by_validator_by_day(validators_metrics, name, date)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validator_by_daterange')
async def get_metrics_by_validator_by_daterange(name: str, start_date: str, end_date: str) -> str:
    metrics = data.get_metrics_by_validator_by_daterange(validators_metrics, name, start_date, end_date)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validators_by_day')
async def get_metrics_by_validators_by_day(date: str, names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators_by_day(validators_metrics, names, date)
    return json.dumps(metrics)

@app.get('/data/metrics_by_validators_by_daterange')
async def get_metrics_by_validators_by_daterange(start_date: str, end_date: str, names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators_by_daterange(validators_metrics, names, start_date, end_date)
    return json.dumps(metrics)

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
    
