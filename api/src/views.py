import os
from typing import List, Union

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.errors import OperationFailure

import data
from .metrics import (
    get_censored_latency,
    get_censored_percentage,
    get_lido_validators_metrics,
    get_lido_vs_rest,
    get_overall_latency,
)
from .mongo import get_collection

AUTH_KEY = os.environ["AUTH_KEY"]

inner_router = APIRouter()
outer_router = APIRouter()
monitoring_router = APIRouter()


@inner_router.get("/lido_validators_share/{period}")
async def _get_lido_validators_share(period: str) -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_lido_validators_metrics(prepared_metrics, period, False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@inner_router.get("/lido_validators_ratio/{period}")
async def _get_lido_validators_ratio(period: str) -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_lido_validators_metrics(prepared_metrics, period, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@inner_router.get("/lido_vs_rest_share/{period}")
async def _get_total_validators_ratio(period: str) -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = metrics = get_lido_vs_rest(prepared_metrics, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@inner_router.get("/overall_latency")
async def _get_latency() -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_overall_latency(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@inner_router.get("/censored_latency/{mean_type}")
async def _get_censorship_latency(mean_type: str) -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_censored_latency(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@inner_router.get("/censored_percentage/{period}")
async def _get_censorship_percentage(period: str) -> JSONResponse:
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_censored_percentage(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/validators")
async def _get_validators(api_key: str) -> JSONResponse:
    validators = get_collection("validators")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        cursor = validators.find({}, {"_id": 0})
    except OperationFailure:
        raise HTTPException(status_code=500, detail="Failed to fetch validators data from db")

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@outer_router.get("/data/metrics")
async def _get_metrics(api_key: str) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics(validators_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/metrics_by_day")
async def _get_metrics_by_date(api_key: str, date: str) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics_by_day(validators_metrics, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/metrics_by_validators")
async def _get_metrics_by_validators(api_key: str, names: Union[List[str], None] = Query(default=None)) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics_by_validators(validators_metrics, names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/metrics_by_daterange")
async def _get_metrics_by_daterange(api_key: str, start_date: str, end_date: str) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics_by_daterange(validators_metrics, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/metrics_by_validators_by_day")
async def _get_metrics_by_validators_by_day(
    api_key: str, date: str, names: Union[List[str], None] = Query(default=None)
) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics_by_validators_by_day(validators_metrics, names, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/metrics_by_validators_by_daterange")
async def _get_metrics_by_validators_by_daterange(
    api_key: str,
    start_date: str,
    end_date: str,
    names: Union[List[str], None] = Query(default=None),
) -> JSONResponse:
    validators_metrics = get_collection("validators_metrics")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_metrics_by_validators_by_daterange(validators_metrics, names, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/censored_transactions")
async def _get_transactions(api_key: str) -> JSONResponse:
    censored_txs = get_collection("censored_txs")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_censored_transactions(censored_txs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/censored_transactions_by_day")
async def _get_transactions_by_day(api_key: str, date: str) -> JSONResponse:
    censored_txs = get_collection("censored_txs")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_censored_transactions_by_day(censored_txs, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/censored_transactions_by_daterange")
async def _get_transactions_by_daterange(api_key: str, start_date: str, end_date: str) -> JSONResponse:
    censored_txs = get_collection("censored_txs")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_censored_transactions_by_day(censored_txs, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/ofac_addresses")
async def _get_ofac_list(api_key: str) -> JSONResponse:
    ofac_list = get_collection("ofac_list")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        cursor = ofac_list.find({}, {"_id": 0})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@outer_router.get("/data/ofac_addresses_by_day")
async def _get_ofac_list_by_day(api_key: str, date: str) -> JSONResponse:
    ofac_list = get_collection("ofac_list")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_ofac_list_by_day(ofac_list, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@outer_router.get("/data/ofac_addresses_by_daterange")
async def _get_ofac_list_by_daterange(api_key: str, start_date: str, end_date: str) -> JSONResponse:
    ofac_list = get_collection("ofac_list")

    if not api_key == AUTH_KEY:
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = data.get_ofac_list_by_daterange(ofac_list, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


def add_routing(outer_app: FastAPI, inner_app: FastAPI):
    outer_app.include_router(outer_router)
    inner_app.include_router(inner_router)
