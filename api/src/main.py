from fastapi import FastAPI, Query
import uvicorn
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import os
from typing import List, Union
import json

from metrics import get_lido_validators_metrics, get_lido_vs_rest, get_latency
import data

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = 'root'
MONGO_PASSWORD = 'test_pass'
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
censored_txs = db['censored_txs']


@app.get("/metrics/lido_validators_share/{period}")
async def get_lido_validators_share(period:str) -> List[dict]: 
    metrics = get_lido_validators_metrics(validators_metrics, period, False)

    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/metrics/lido_validators_ratio/{period}')
async def get_lido_validators_ratio(period:str) -> List[dict]:
    metrics = get_lido_validators_metrics(validators_metrics, period, True)

    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/metrics/lido_vs_rest_share/{period}')
async def get_total_validators_ratio(period:str) -> List[dict]:
    metrics = get_lido_vs_rest(validators_metrics, period)

    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/validators')
async def get_validators() -> str:
    cursor = validators.find({}, {'_id': 0})

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)

@app.get('/data/metrics_by_day')
async def get_metrics_by_date(date: str) -> str:
    metrics = data.get_metrics_by_day(validators_metrics, date)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/metrics_by_validators')
async def get_metrics_by_validators(names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators(validators_metrics, names)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/metrics_by_daterange')
async def get_metrics_by_daterange(start_date: str, end_date: str) -> str:
    metrics = data.get_metrics_by_daterange(validators_metrics, start_date, end_date)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/metrics_by_validators_by_day')
async def get_metrics_by_validators_by_day(date: str, names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators_by_day(validators_metrics, names, date)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/metrics_by_validators_by_daterange')
async def get_metrics_by_validators_by_daterange(start_date: str, end_date: str, names: Union[List[str], None] = Query(default=None)) -> str:
    metrics = data.get_metrics_by_validators_by_daterange(validators_metrics, names, start_date, end_date)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

@app.get('/data/latency')
async def get_latencies() -> str:
    metrics = get_latency(censored_txs, validators)
    res = jsonable_encoder(metrics)
    return JSONResponse(res)

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
    
