from typing import List
from pymongo.collection import Collection

import datetime

from utils import str_date_repr


def _get_daterange(start_date: str, end_date: str) -> List[str]:
    format = "%d-%m-%y"
    start_date = datetime.datetime.strptime(start_date, format)
    end_date = datetime.datetime.strptime(end_date, format)

    daydiff = (end_date - start_date).days + 1

    daterange = [
        str_date_repr(start_date + datetime.timedelta(days=diff))
        for diff in range(daydiff)
    ]

    return daterange


def get_collection_keys(collection: Collection) -> List[str]:
    records = collection.find({})
    keys = set()
    for record in records:
        for key in record.keys():
            keys.add(key)

    return list(keys)


def get_metrics(collection: Collection) -> List[dict]:
    cursor = collection.find({}, {"_id": 0})
    return list(cursor)


def get_metrics_by_day(collection: Collection, date: str) -> List[dict]:
    keys = get_collection_keys(collection)
    cols_to_take = list(set([date]).intersection(set(keys))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({}, cols)
    return list(cursor)


def get_metrics_by_validators(collection: Collection, names: List[str]) -> List[dict]:
    cursor = collection.find({"name": {"$in": names}}, {"_id": 0})
    return list(cursor)


def get_metrics_by_daterange(
    collection: Collection, start_date: str, end_date: str
) -> List[dict]:
    daterange = _get_daterange(start_date, end_date)
    keys = get_collection_keys(collection)

    cols_to_take = list(set(keys).intersection(set(daterange))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({}, cols)
    return list(cursor)


def get_metrics_by_validators_by_day(
    collection: Collection, names: List[str], date: str
) -> List[dict]:
    keys = get_collection_keys(collection)
    cols_to_take = list(set([date]).intersection(set(keys))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({"name": {"$in": names}}, cols)
    return list(cursor)


def get_metrics_by_validators_by_daterange(
    collection: Collection, names: List[str], start_date: str, end_date: str
) -> List[dict]:
    daterange = _get_daterange(start_date, end_date)
    keys = get_collection_keys(collection)

    cols_to_take = list(set(keys).intersection(set(daterange))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({"name": {"$in": names}}, cols)
    return list(cursor)


def get_censored_transactions(collection: Collection) -> List[dict]:
    cursor = collection.find({}, {"_id": 0})
    return list(cursor)


def get_censored_transactions_by_day(collection: Collection, date: str) -> List[dict]:
    start_dt = datetime.datetime.strptime(date, "%d-%m-%y")
    end_dt = start_dt + datetime.timedelta(days=1)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    cursor = collection.find(
        {
            "timestamp": {"$gte": start_ts, "$lt": end_ts},
            "non_ofac_compliant": True,
        },
        {"_id": 0},
    )

    return list(cursor)


def get_censored_transactions_by_daterange(
    collection: Collection, start_date: str, end_date: str
) -> List[dict]:
    start_dt = datetime.datetime.strptime(start_date, "%d-%m-%y")
    end_dt = datetime.datetime.strptime(end_date, "%d-%m-%y") + datetime.timedelta(
        days=1
    )

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    cursor = collection.find(
        {
            "timestamp": {"$gte": start_ts, "$lt": end_ts},
            "non_ofac_compliant": True,
        },
        {"_id": 0},
    )

    return list(cursor)
