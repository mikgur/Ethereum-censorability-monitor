from fastapi import FastAPI, Query, HTTPException
import uvicorn
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import os
from typing import List, Union

from metrics import get_lido_validators_metrics, get_lido_vs_rest, get_latency
import data


API_HOST = os.environ["API_HOST"]
API_PORT = os.environ["API_PORT"]
MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"])

mongo_url = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
client = MongoClient(mongo_url)

db = client["censorred"]
validators = db["validators"]
validators_metrics = db["validators_metrics"]
censored_txs = db["censored_txs"]
ofac_list = db["ofac_addresses"]


@app.get("/metrics/lido_validators_share/{period}")
async def get_lido_validators_share(period: str) -> JSONResponse:
    # Query examples: /metrics/lido_validators_share/last_week
    # Query examples: /metrics/lido_validators_share/last_month
    try:
        metrics = get_lido_validators_metrics(validators_metrics, period, False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/lido_validators_ratio/{period}")
async def get_lido_validators_ratio(period: str) -> JSONResponse:
    # Query examples: /metrics/get_lido_validators_ratio/last_week
    # Query examples: /metrics/get_lido_validators_ratio/last_month
    try:
        metrics = get_lido_validators_metrics(validators_metrics, period, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/lido_vs_rest_share/{period}")
async def get_total_validators_ratio(period: str) -> JSONResponse:
    # Query examples: /metrics/lido_vs_rest_share/last_week
    # Query examples: /metrics/lido_vs_rest_share/last_month
    try:
        metrics = metrics = get_lido_vs_rest(validators_metrics, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/validators")
async def get_validators() -> JSONResponse:
    # Query example: /data/validators
    try:
        cursor = validators.find({}, {"_id": 0})
    except:
        raise HTTPException(
            status_code=500, detail="Failed to fetch validators data from db"
        )

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@app.get("/data/metrics")
async def get_metrics() -> JSONResponse:
    # Query example: /data/metrics
    try:
        metrics = data.get_metrics(validators_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/metrics_by_day")
async def get_metrics_by_date(date: str) -> JSONResponse:
    # Query example: /data/metrics_by_day?date=17-02-23
    try:
        metrics = data.get_metrics_by_day(validators_metrics, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/metrics_by_validators")
async def get_metrics_by_validators(
    names: Union[List[str], None] = Query(default=None)
) -> JSONResponse:
    # Query example: /data/metrics_by_validators?names=stakefish&names=Figment
    try:
        metrics = data.get_metrics_by_validators(validators_metrics, names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/metrics_by_daterange")
async def get_metrics_by_daterange(start_date: str, end_date: str) -> JSONResponse:
    # Query example: /data/metrics_by_daterange?start_date=15-02-23&end_date=17-02-23
    try:
        metrics = data.get_metrics_by_daterange(
            validators_metrics, start_date, end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/metrics_by_validators_by_day")
async def get_metrics_by_validators_by_day(
    date: str, names: Union[List[str], None] = Query(default=None)
) -> JSONResponse:
    # Query example: /data/metrics_by_validators_by_day?date=17-02-23&names=stakefish&names=Figment
    try:
        metrics = data.get_metrics_by_validators_by_day(validators_metrics, names, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/metrics_by_validators_by_daterange")
async def get_metrics_by_validators_by_daterange(
    start_date: str, end_date: str, names: Union[List[str], None] = Query(default=None)
) -> str:
    # Query example: /data/metrics_by_validators_by_daterange?start_date=17-02-23&end_date=19-02-23&names=stakefish&names=Figment
    try:
        metrics = data.get_metrics_by_validators_by_daterange(
            validators_metrics, names, start_date, end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/latency")
async def get_latencies() -> JSONResponse:
    # Query example: /metrics/latency
    try:
        metrics = get_latency(censored_txs, validators)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/censored_transactions")
async def get_transactions() -> JSONResponse:
    # Query example: /data/censored_transactions
    try:
        metrics = data.get_censored_transactions(censored_txs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/censored_transactions_by_day")
async def get_transactions(date: str) -> JSONResponse:
    # Query example: /data/censored_transactions_by_day?date=17-02-23
    try:
        metrics = data.get_censored_transactions_by_day(censored_txs, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/censored_transactions_by_daterange")
async def get_transactions(start_date: str, end_date: str) -> JSONResponse:
    # Query example: /data/censored_transactions_by_daterange?start_date=15-02-23&end_date=17-02-23
    try:
        metrics = data.get_censored_transactions_by_day(
            censored_txs, start_date, end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/ofac_addresses")
async def get_ofac_list() -> JSONResponse:
    # Query example: /data/ofac_addresses
    try:
        cursor = ofac_list.find({}, {"_id": 0})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@app.get("/data/ofac_addresses_by_day")
async def get_ofac_list_by_day(date: str) -> JSONResponse:
    # Query example: /data/ofac_addresses?date=17-02-23
    try:
        metrics = data.get_ofac_list_by_day(ofac_list, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/data/ofac_addresses_by_day")
async def get_ofac_list_by_daterange(start_date: str, end_date: str) -> JSONResponse:
    # Query example: /data/get_ofac_list_by_daterange?start_date=15-02-23&end_date=17-02-23
    try:
        metrics = data.get_ofac_list_by_daterange(ofac_list, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=True, workers=4)
