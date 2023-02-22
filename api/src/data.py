from typing import List
from pymongo.collection import Collection

import datetime

from utils import str_date_repr


def _get_daterange(start_date: str, end_date: str) -> List[str]:
    """
    Get list of dates between two days (inclusively)

    Args:
        start_date  -   Left bound of the date range
        end_date    -   Right bound of the date range

    Returns:
        List of dates in dd-mm-yy format between two days (inclusively)

    """
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
    """
    Get all keys of Mongo collection

    Args:
        collection  -   Mongo collection

    Returns:
        List of collection keys
    """
    # TODO: there might be more efficient way to obtain a list of collection keys
    records = collection.find({})
    keys = set()
    for record in records:
        for key in record.keys():
            keys.add(key)

    return list(keys)


def get_metrics(collection: Collection) -> List[dict]:
    """
    Get all data from metrics collection

    Args:
        collection  -   Mongo collection of metrics

    Returns:
        List of all records in the metrics collection
    """
    cursor = collection.find({}, {"_id": 0})
    return list(cursor)


def get_metrics_by_day(collection: Collection, date: str) -> List[dict]:
    """
    Get all metrics for the single day

    Args:
        collection  -   Mongo collection of metrics
        date        -   Date to get metrics

    Returns:
        List of all records in the metrics collection for the chosen day
    """
    keys = get_collection_keys(collection)
    # Filter query to get only nesessary fields from collection
    cols_to_take = list(set([date]).intersection(set(keys))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({}, cols)
    return list(cursor)


def get_metrics_by_validators(collection: Collection, names: List[str]) -> List[dict]:
    """
    Get all metrics for multiple validators

    Args:
        collection  -   Mongo collection of metrics
        names       -   List of validators names

    Returns:
        List of all records in the metrics collection for the chosen validators
    """
    cursor = collection.find({"name": {"$in": names}}, {"_id": 0})
    return list(cursor)


def get_metrics_by_daterange(
    collection: Collection, start_date: str, end_date: str
) -> List[dict]:
    """
    Get all metrics for the date range

    Args:
        collection  -   Mongo collection of metrics
        start_date  -   Left bound of the date range
        end_date    -   Right bound of the date range

    Returns:
        List of all records in the metrics collection for the chosen date range
    """
    daterange = _get_daterange(start_date, end_date)
    keys = get_collection_keys(collection)
    # Filter query to get only nesessary fields from collection
    cols_to_take = list(set(keys).intersection(set(daterange))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({}, cols)
    return list(cursor)


def get_metrics_by_validators_by_day(
    collection: Collection, names: List[str], date: str
) -> List[dict]:
    """
    Get all metrics for multiple validators for the single day

    Args:
        collection  -   Mongo collection of metrics
        names       -   List of validators names
        date        -   Date to get metrics

    Returns:
        List of all records in the metrics collection for the chosen validators
        for the chosen day
    """
    keys = get_collection_keys(collection)
    # Filter query to get only nesessary fields from collection
    cols_to_take = list(set([date]).intersection(set(keys))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({"name": {"$in": names}}, cols)
    return list(cursor)


def get_metrics_by_validators_by_daterange(
    collection: Collection, names: List[str], start_date: str, end_date: str
) -> List[dict]:
    """
    Get all metrics for multiple validators for the date range

    Args:
        collection  -   Mongo collection of metrics
        names       -   List of validators names
        start_date  -   Left bound of the date range
        end_date    -   Right bound of the date range

    Returns:
        List of all records in the metrics collection for the chosen validators
        for the date range
    """
    daterange = _get_daterange(start_date, end_date)
    keys = get_collection_keys(collection)
    # Filter query to get only nesessary fields from collection
    cols_to_take = list(set(keys).intersection(set(daterange))) + ["name"]
    cols = {col: (1 if col in cols_to_take else 0) for col in keys}

    cursor = collection.find({"name": {"$in": names}}, cols)
    return list(cursor)


def get_censored_transactions(collection: Collection) -> List[dict]:
    """
    Get all censored transactions

    Args:
        collection  -   Mongo collection of censored transactions

    Returns:
        List of all records from in the censored transactions collection
    """
    cursor = collection.find({}, {"_id": 0})
    return list(cursor)


def get_censored_transactions_by_day(collection: Collection, date: str) -> List[dict]:
    """
    Get all censored transactions for the single day

    Args:
        collection  -   Mongo collection of censored transactions
        date        -   Date to get censored transactions

    Returns:
        List of all records from in the censored transactions collection for the chosen day
    """
    start_dt = datetime.datetime.strptime(date, "%d-%m-%y")
    end_dt = start_dt + datetime.timedelta(days=1)

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    # Find all transactions with timestamp between
    # timestamps of the start of the day and it's end
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
    """
    Get all censored transactions for the single day

    Args:
        collection  -   Mongo collection of censored transactions
        start_date  -   Left bound of the date range
        end_date    -   Right bound of the date range

    Returns:
        List of all records from in the censored transactions collection for the date range
    """
    start_dt = datetime.datetime.strptime(start_date, "%d-%m-%y")
    end_dt = datetime.datetime.strptime(end_date, "%d-%m-%y") + datetime.timedelta(
        days=1
    )

    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    # Find all transactions with timestamp between
    # timestamps of the start of the first day
    # and the end of the last day of the date range
    cursor = collection.find(
        {
            "timestamp": {"$gte": start_ts, "$lt": end_ts},
            "non_ofac_compliant": True,
        },
        {"_id": 0},
    )

    return list(cursor)
