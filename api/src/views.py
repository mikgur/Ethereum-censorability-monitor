import os
from typing import List, Union

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .data import *
from .metrics import (
    get_censored_latency,
    get_censored_percentage,
    get_lido_validators_metrics,
    get_lido_vs_rest,
    get_overall_latency,
)
from .mongo import get_collection

AUTH_KEY = os.environ["AUTH_KEY"]

router = APIRouter()


@router.get("/metrics/lido_validators_share/{period}")
async def _get_lido_validators_share(period: str) -> JSONResponse:
    # Query examples: /metrics/lido_validators_share/last_week
    # Query examples: /metrics/lido_validators_share/last_month
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_lido_validators_metrics(prepared_metrics, period, False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/metrics/lido_validators_ratio/{period}")
async def _get_lido_validators_ratio(period: str) -> JSONResponse:
    # Query examples: /metrics/get_lido_validators_ratio/last_week
    # Query examples: /metrics/get_lido_validators_ratio/last_month
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_lido_validators_metrics(prepared_metrics, period, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/metrics/lido_vs_rest_share/{period}")
async def _get_total_validators_ratio(period: str) -> JSONResponse:
    # Query examples: /metrics/lido_vs_rest_share/last_week
    # Query examples: /metrics/lido_vs_rest_share/last_month
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = metrics = get_lido_vs_rest(prepared_metrics, period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/metrics/overall_latency")
async def _get_latency() -> JSONResponse:
    # Query example: /metrics/overall_latency
    # Query example: /metrics/overall_latency
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_overall_latency(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/metrics/censored_latency/{mean_type}")
async def _get_censorship_latency(mean_type: str) -> JSONResponse:
    # Query example: /metrics/censored_latency/average
    # Query example: /metrics/censored_latency/median
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_censored_latency(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/metrics/censored_percentage/{period}")
async def _get_censorship_percentage(period: str) -> JSONResponse:
    # Query example: /metrics/censorship_percentage/last_week
    # Query example: /metrics/censorship_percentage/last_month
    prepared_metrics = get_collection("prepared_metrics")

    try:
        metrics = get_censored_percentage(prepared_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/validators")
async def _get_validators(api_key: str) -> JSONResponse:
    # Query example: /data/validators?api_key=123
    validators = get_collection("validators")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        cursor = validators.find({}, {"_id": 0})
    except:
        raise HTTPException(
            status_code=500, detail="Failed to fetch validators data from db"
        )

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@router.get("/data/metrics")
async def _get_metrics(api_key: str) -> JSONResponse:
    # Query example: /data/metrics?api_key=123
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics(validators_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/metrics_by_day")
async def _get_metrics_by_date(api_key: str, date: str) -> JSONResponse:
    # Query example: /data/metrics_by_day?api_key=123&date=17-02-23
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics_by_day(validators_metrics, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/metrics_by_validators")
async def _get_metrics_by_validators(
    api_key: str, names: Union[List[str], None] = Query(default=None)
) -> JSONResponse:
    # Query example: /data/metrics_by_validators?api_key=123&names=stakefish&names=Figment
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics_by_validators(validators_metrics, names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/metrics_by_daterange")
async def _get_metrics_by_daterange(
    api_key: str, start_date: str, end_date: str
) -> JSONResponse:
    # Query example: /data/metrics_by_daterange?api_key=123&start_date=15-02-23&end_date=17-02-23
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics_by_daterange(validators_metrics, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/metrics_by_validators_by_day")
async def _get_metrics_by_validators_by_day(
    api_key: str, date: str, names: Union[List[str], None] = Query(default=None)
) -> JSONResponse:
    # Query example: /data/metrics_by_validators_by_day?api_key=123&date=17-02-23&names=stakefish&names=Figment
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics_by_validators_by_day(validators_metrics, names, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/metrics_by_validators_by_daterange")
async def _get_metrics_by_validators_by_daterange(
    api_key: str,
    start_date: str,
    end_date: str,
    names: Union[List[str], None] = Query(default=None),
) -> JSONResponse:
    # Query example: /data/metrics_by_validators_by_daterange?api_key=123&start_date=17-02-23&end_date=19-02-23&names=stakefish&names=Figment
    validators_metrics = get_collection("validators_metrics")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_metrics_by_validators_by_daterange(
            validators_metrics, names, start_date, end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/censored_transactions")
async def _get_transactions(api_key: str) -> JSONResponse:
    # Query example: /data/censored_transactions?api_key=123
    censored_txs = get_collection("censored_txs")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_censored_transactions(censored_txs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/censored_transactions_by_day")
async def _get_transactions_by_day(api_key: str, date: str) -> JSONResponse:
    # Query example: /data/censored_transactions_by_day?api_key=123&date=17-02-23
    censored_txs = get_collection("censored_txs")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_censored_transactions_by_day(censored_txs, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/censored_transactions_by_daterange")
async def _get_transactions_by_daterange(
    api_key: str, start_date: str, end_date: str
) -> JSONResponse:
    # Query example: /data/censored_transactions_by_daterange?api_key=123&start_date=15-02-23&end_date=17-02-23
    censored_txs = get_collection("censored_txs")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_censored_transactions_by_day(censored_txs, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/ofac_addresses")
async def _get_ofac_list(api_key: str) -> JSONResponse:
    # Query example: /data/ofac_addresses?api_key=123
    ofac_list = get_collection("ofac_list")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        cursor = ofac_list.find({}, {"_id": 0})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(list(cursor))
    return JSONResponse(res)


@router.get("/data/ofac_addresses_by_day")
async def _get_ofac_list_by_day(api_key: str, date: str) -> JSONResponse:
    # Query example: /data/ofac_addresses?api_key=123&date=17-02-23
    ofac_list = get_collection("ofac_list")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_ofac_list_by_day(ofac_list, date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@router.get("/data/ofac_addresses_by_daterange")
async def _get_ofac_list_by_daterange(
    api_key: str, start_date: str, end_date: str
) -> JSONResponse:
    # Query example: /data/get_ofac_list_by_daterange?api_key=123&start_date=15-02-23&end_date=17-02-23
    ofac_list = get_collection("ofac_list")

    if not (api_key == AUTH_KEY):
        return HTTPException(status_code=401, detail="You need api key to receive data")
    try:
        metrics = get_ofac_list_by_daterange(ofac_list, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


def add_routing(app: FastAPI):
    app.include_router(router)
