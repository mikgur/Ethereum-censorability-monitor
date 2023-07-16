#!/bin/python
from datetime import datetime, timezone
from logging import Logger
from typing import List

import numpy as np
import pandas as pd
from pymongo.collection import Collection

from utils import get_last_dates, get_shifted_week, get_week


def update_metrics(
    metrics_collection: Collection,
    txs_collection: Collection,
    validators_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update metrics in database

    Args:
        metrics_collection      -   Mongo collection of raw metrics
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    update_censored_percentage(
        txs_collection, validators_collection, target_collection, logger
    )
    update_overall_average_latency(
        txs_collection, validators_collection, target_collection, logger
    )
    update_censored_average_latency(
        txs_collection, validators_collection, target_collection, logger
    )
    update_lido_vs_rest_censorship_resistance_index(
        metrics_collection, target_collection, logger
    )
    update_validators_censorship_resistance_index(
        metrics_collection, target_collection, logger
    )
    update_validators_compliance_ratio(
        metrics_collection, target_collection, logger
    )


def update_overall_average_latency(
    txs_collection: Collection,
    validators_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update overall average latency

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info("Calculating overall average latency")

    latency = get_overall_latency(txs_collection, validators_collection)
    record = {"metrics": "overall_average_latency", "values": latency}

    logger.info("Overall average latency has been calculated")

    logger.info("Updating overall average latency")

    target_collection.delete_one({"metrics": "overall_average_latency"})
    target_collection.insert_one(record)

    logger.info("Overall average latency has been updated")


def update_censored_percentage(
    txs_collection: Collection,
    validators_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update percentage of censored transactions

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info("Calculating percentage of censored transactions")

    percentage = get_censored_percentage(
        txs_collection, validators_collection, "last_month"
    )
    record = {"metrics": "censored_percentage", "values": percentage}

    logger.info("Percentage of censored transactions has been calculated")

    logger.info("Updating percentage of censored transactions")

    target_collection.delete_one({"metrics": "censored_percentage"})
    target_collection.insert_one(record)

    logger.info("Percentage of censored transactions has been updated")


def update_censored_average_latency(
    txs_collection: Collection,
    validators_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update average latency for censored transactions

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info("Calculating average latency for censored transactions")

    latency = get_censored_latency(
        txs_collection, validators_collection, "average"
    )
    record = {"metrics": "censored_average_latency", "values": latency}

    logger.info(
        "Average latency for censored transactions has been calculated"
    )

    logger.info("Updating average latency for censored transactions")

    target_collection.delete_one({"metrics": "censored_average_latency"})
    target_collection.insert_one(record)

    logger.info(
        "Average latency for censored transactions has been updated"
    )


def update_lido_vs_rest_censorship_resistance_index(
    metrics_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update lido vs rest censorship resistance index

    Args:
        metrics_collection      -   Mongo collection of raw metrics
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info(
        "Calculating Lido vs Rest censorship resistance index over last week"
    )

    lw_resistance_index = get_lido_vs_rest(metrics_collection, "last_week")

    logger.info(
        "Lido vs Rest censorship resistance index over last week has been calculated"
    )

    logger.info(
        "Calculating Lido vs Rest censorship resistance index over last month"
    )

    lm_resistance_index = get_lido_vs_rest(
        metrics_collection, "last_month"
    )

    logger.info(
        "Lido vs Rest censorship resistance index over last month has been calculated"
    )

    logger.info(
        "Calculating Lido vs Rest censorship resistance index over last halfyear"
    )

    lh_resistance_index = get_lido_vs_rest(
        metrics_collection, "last_half_year"
    )

    logger.info(
        "Lido vs Rest censorship resistance index over last halfyear has been calculated"
    )

    logger.info(
        "Calculating Lido vs Rest censorship resistance index over last year"
    )

    ly_resistance_index = get_lido_vs_rest(
        metrics_collection, "last_year"
    )

    logger.info(
        "Lido vs Rest censorship resistance index over last year has been calculated"
    )

    lw_record = {
        "metrics": "last_week_lido_vs_rest_censorship_resistance_index",
        "values": lw_resistance_index,
    }

    lm_record = {
        "metrics": "last_month_lido_vs_rest_censorship_resistance_index",
        "values": lm_resistance_index,
    }

    lh_record = {
        "metrics": "last_half_year_lido_vs_rest_censorship_resistance_index",
        "values": lh_resistance_index,
    }

    ly_record = {
        "metrics": "last_year_lido_vs_rest_censorship_resistance_index",
        "values": ly_resistance_index,
    }

    logger.info(
        "Updating Lido vs Rest censorship resistance index over last week"
    )

    target_collection.delete_one(
        {"metrics": "last_week_lido_vs_rest_censorship_resistance_index"}
    )
    target_collection.insert_one(lw_record)

    logger.info(
        "Lido vs Rest censorship resistance index over last week has been updated"
    )
    logger.info(
        "Updating Lido vs Rest censorship resistance index over last month"
    )

    target_collection.delete_one(
        {"metrics": "last_month_lido_vs_rest_censorship_resistance_index"}
    )
    target_collection.insert_one(lm_record)

    logger.info(
        "Lido vs Rest censorship resistance index over last month has been updated"
    )

    logger.info(
        "Updating Lido vs Rest censorship resistance index over last halfyear"
    )

    target_collection.delete_one(
        {"metrics": "last_half_year_lido_vs_rest_censorship_resistance_index"}
    )
    target_collection.insert_one(lh_record)

    logger.info(
        "Lido vs Rest censorship resistance index over last halfyear has been updated"
    )

    logger.info(
        "Updating Lido vs Rest censorship resistance index over last year"
    )

    target_collection.delete_one(
        {"metrics": "last_year_lido_vs_rest_censorship_resistance_index"}
    )
    target_collection.insert_one(ly_record)

    logger.info(
        "Lido vs Rest censorship resistance index over last year has been updated"
    )


def update_validators_censorship_resistance_index(
    metrics_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update validators censorship resistance index

    Args:
        metrics_collection      -   Mongo collection of raw metrics
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info(
        "Calculating validators censorship resistance index over last week"
    )

    lw_resistance_index = get_lido_validators_metrics(
        metrics_collection, "last_week", True
    )

    logger.info(
        "Validators censorship resistance index over last week has been calculated"
    )
    logger.info(
        "Calculating validators censorship resistance index over last month"
    )

    lm_resistance_index = get_lido_validators_metrics(
        metrics_collection, "last_month", True
    )

    logger.info(
        "Validators censorship resistance index over last month has been calculated"
    )

    logger.info(
        "Calculating validators censorship resistance index over last halfyear"
    )

    lh_resistance_index = get_lido_validators_metrics(
        metrics_collection, "last_half_year", True
    )

    logger.info(
        "Validators censorship resistance index over last halfyear has been calculated"
    )

    logger.info(
        "Calculating validators censorship resistance index over last year"
    )

    ly_resistance_index = get_lido_validators_metrics(
        metrics_collection, "last_year", True
    )

    logger.info(
        "Validators censorship resistance index over last year has been calculated"
    )

    lw_record = {
        "metrics": "last_week_validators_censorship_resistance_index",
        "values": lw_resistance_index,
    }

    lm_record = {
        "metrics": "last_month_validators_censorship_resistance_index",
        "values": lm_resistance_index,
    }

    lh_record = {
        "metrics": "last_half_year_validators_censorship_resistance_index",
        "values": lh_resistance_index,
    }

    ly_record = {
        "metrics": "last_year_validators_censorship_resistance_index",
        "values": ly_resistance_index,
    }

    logger.info(
        "Updating validators censorship resistance index over last week"
    )

    target_collection.delete_one(
        {"metrics": "last_week_validators_censorship_resistance_index"}
    )
    target_collection.insert_one(lw_record)

    logger.info(
        "Validators censorship resistance index over last week has been updated"
    )
    logger.info(
        "Updating validators censorship resistance index over last month"
    )

    target_collection.delete_one(
        {"metrics": "last_month_validators_censorship_resistance_index"}
    )
    target_collection.insert_one(lm_record)

    logger.info(
        "Validators censorship resistance index over last month has been updated"
    )

    logger.info(
        "Updating validators censorship resistance index over last halfyear"
    )

    target_collection.delete_one(
        {"metrics": "last_half_year_validators_censorship_resistance_index"}
    )
    target_collection.insert_one(lh_record)

    logger.info(
        "Validators censorship resistance index over last halfyear has been updated"
    )

    logger.info(
        "Updating validators censorship resistance index over last year"
    )

    target_collection.delete_one(
        {"metrics": "last_year_validators_censorship_resistance_index"}
    )
    target_collection.insert_one(ly_record)

    logger.info(
        "Validators censorship resistance index over last year has been updated"
    )


def update_validators_compliance_ratio(
    metrics_collection: Collection,
    target_collection: Collection,
    logger: Logger,
) -> None:
    """
    Update validators compliance ratio

    Args:
        metrics_collection      -   Mongo collection of raw metrics
        target_collection       -   Mongo collection to store prepared metrics
        logger                  -   Logger
    """

    logger.info("Calculating validators compliance ratio over last week")

    lw_ratio = get_lido_validators_metrics(
        metrics_collection, "last_week", False
    )

    logger.info(
        "Validators compliance ratio over last week has been calculated"
    )
    logger.info("Calculating validators compliance ratio over last month")

    lm_ratio = get_lido_validators_metrics(
        metrics_collection, "last_month", False
    )

    logger.info(
        "Validators compliance ratio over last month has been calculated"
    )

    logger.info("Calculating validators compliance ratio over last halfyear")

    lh_ratio = get_lido_validators_metrics(
        metrics_collection, "last_half_year", False
    )

    logger.info(
        "Validators compliance ratio over last halfyear has been calculated"
    )

    logger.info("Calculating validators compliance ratio over last year")

    ly_ratio = get_lido_validators_metrics(
        metrics_collection, "last_year", False
    )

    logger.info(
        "Validators compliance ratio over last year has been calculated"
    )

    lw_record = {
        "metrics": "last_week_validators_compliance_ratio",
        "values": lw_ratio,
    }

    lm_record = {
        "metrics": "last_month_validators_compliance_ratio",
        "values": lm_ratio,
    }

    lh_record = {
        "metrics": "last_half_year_validators_compliance_ratio",
        "values": lh_ratio,
    }

    ly_record = {
        "metrics": "last_year_validators_compliance_ratio",
        "values": ly_ratio,
    }

    logger.info("Updating validators compliance ratio over last week")

    target_collection.delete_one(
        {"metrics": "last_week_validators_compliance_ratio"}
    )
    target_collection.insert_one(lw_record)

    logger.info(
        "Validators compliance ratio over last week has been updated"
    )
    logger.info("Updating validators compliance ratio over last month")

    target_collection.delete_one(
        {"metrics": "last_month_validators_compliance_ratio"}
    )
    target_collection.insert_one(lm_record)

    logger.info(
        "Validators compliance ratio index over last month has been updated"
    )

    logger.info("Updating validators compliance ratio over last halfyear")

    target_collection.delete_one(
        {"metrics": "last_half_year_validators_compliance_ratio"}
    )
    target_collection.insert_one(lh_record)

    logger.info(
        "Validators compliance ratio over last halfyear has been updated"
    )
    logger.info("Updating validators compliance ratio over last year")

    target_collection.delete_one(
        {"metrics": "last_year_validators_compliance_ratio"}
    )
    target_collection.insert_one(ly_record)

    logger.info(
        "Validators compliance ratio index over last year has been updated"
    )


def _get_validators_metrics(
    collection: Collection, dates: List[str]
) -> pd.DataFrame:
    """
    Create dataframe from mongo metrics collection's records corresponding to the specific dates

    Args:
        collection  -   Mongo collection of metrics
        dates       -   List of dates for which metrics need to be obtained

    Returns:
        Pandas dataframe with metrics for the specific dates
    """
    # Filter query to get only nesessary fields from collection
    fields_dict = {date: 1 for date in dates}
    fields_dict["_id"] = 0
    fields_dict["name"] = 1
    fields_dict["pool"] = 1

    try:
        cursor = collection.find({}, fields_dict)
        records = list(cursor)
    except:
        raise Exception("Failed to fetch metrics data from db")

    return pd.DataFrame(records)


def _get_ofac_compliant_count(row: pd.Series, dates: List[str]) -> int:
    """
    Count OFAC compliant transactions over specific dates for the specific validator

    Args:
        row     -   Pandas series corresconding to the specific validator
        dates   -   List of dates for which transaction's count need to be calculated

    Returns:
        Count of OFAC compliant transactions over specific dates for the specific validator
    """
    count = 0
    for day in dates:
        if day in row.keys():
            if isinstance(row[day], dict):
                count += row[day].get("num_ofac_compliant_txs", 0)

    return count


def _get_ofac_non_compliant_count(row: pd.Series, dates: List[str]) -> int:
    """
    Count OFAC non compliant transactions over specific dates for the specific validator

    Args:
        row     -   Pandas series corresconding to the specific validator
        dates   -   List of dates for which transaction's count need to be calculated

    Returns:
        Count of OFAC non compliant transactions over specific dates for the specific validator
    """
    count = 0
    for day in dates:
        if day in row.keys():
            if isinstance(row[day], dict):
                count += len(row[day].get("non_ofac_compliant_txs", []))

    return count


def _prepare_share_df(df: pd.DataFrame, dates: List[str]) -> pd.DataFrame:
    """
    Calculate "share metric" over dataframe

    Args:
        df      -   Pandas dataframe with metrics
        dates   -   List of dates for which tmetrics need to be calculated

    Returns:
        Pandas dataframe with calculated metrics
    """
    _df = df.query("name != 'Unknown'").copy()

    _df["ofac_compliant_count"] = _df.apply(
        _get_ofac_compliant_count, axis=1, args=(dates,)
    )
    _df["ofac_non_compliant_count"] = _df.apply(
        _get_ofac_non_compliant_count, axis=1, args=(dates,)
    )
    
    compliant_count = _df.ofac_compliant_count.sum()
    non_compliant_count = _df.ofac_non_compliant_count.sum()

    _df["ofac_compliant_share"] = 100 * _df.ofac_compliant_count / compliant_count
    _df["ofac_non_compliant_share"] = 100 * _df.ofac_non_compliant_count / non_compliant_count

    # Select only needed colunms
    _df = _df[
        [
            "name",
            "pool",
            "ofac_compliant_share",
            "ofac_non_compliant_share",
            "ofac_compliant_count",
            "ofac_non_compliant_count"
        ]
    ]

    return _df


def _prepare_ratio_df(share_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate "ratio metric" over dataframe

    Args:
        df      -   Pandas dataframe with metrics
        dates   -   List of dates for which tmetrics need to be calculated

    Returns:
        Pandas dataframe with calculated metrics
    """
    _df = share_df.copy()

    _df["ratio"] = _df.ofac_non_compliant_share / _df.ofac_compliant_share
    _df.ratio = _df.ratio.replace(np.inf, 1)

    _df = _df[["name", "ratio"]]

    return _df


def _calc_lido_latency(
    censored_blocks: List[dict], lido_vals: List[str]
) -> int:
    """
    Calculate the censorship latency in case the Lido validators would not censor OFAC non compliant transactions

    Args:
        censored_blocks -   List of censored blocks
        lido_vals       -   List of Lido validators

    Returns:
        Censorship latency in case the Lido validators would not censor OFAC non compliant transactions in seconds
    """
    latency = 0
    if not isinstance(censored_blocks, list):
        return latency
    for censored_block in censored_blocks:
        # If we find validators of lido in the list of censors,
        # we will assume that he validated the transaction and
        # there was no further censorship
        if "validator_pool" in censored_block and censored_block["validator_pool"] != 'Lido':
            latency += 12
        elif censored_block["validator"] not in lido_vals:
            latency += 12
        else:
            break

    return latency


def _get_count_of_censored_blocks(censored: List[dict]) -> int:
    """
    Get count of blocks where transaction was censored

    Args:
        censored    -   Dict of blocks

    Returns:
        Count of blocks where transaction was censored
    """
    if isinstance(censored, list):
        return len(censored)
    else:
        return 0


def get_lido_validators_metrics(
    collection: Collection, period: str, calc_ratio: bool
) -> List[dict]:
    """
    Calculate censorship metrics over specific time period

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated (last_week or last_month)
        calc_ratio  -   Calculate "ratio metric" or not

    Returns:
        List of dicts with metrics for each Lido validator
    """
    if period == 'last_week':
        dates = get_last_dates(0, 7)
    elif period == "last_month":
        dates = get_last_dates(0, 30)
    elif period ==  "last_half_year":
        dates = get_last_dates(0, 180)
    elif period ==  "last_year":
        dates = get_last_dates(0, 365)        
    else :
        raise ValueError("Wrong period")

    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)

    metrics_df = metrics_df.query("pool == 'Lido'")

    metrics_df = metrics_df[
        ["name", "ofac_compliant_share", "ofac_non_compliant_share"]
    ]

    if calc_ratio:
        metrics_df = _prepare_ratio_df(metrics_df)

    return metrics_df.to_dict(orient="records")


def get_lido_vs_rest(collection: Collection, period: str) -> str:
    """
    Calculate "ratio metric" for Lido and other pools

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated (last_week or last_month)

    Returns:
        List of dicts with metrics for Lido and other pools
    """
    if period == 'last_week':
        dates = get_last_dates(0, 7)
    elif period == "last_month":
        dates = get_last_dates(0, 30)
    elif period ==  "last_half_year":
        dates = get_last_dates(0, 180)
    elif period ==  "last_year":
        dates = get_last_dates(0, 365)        
    else :
        raise ValueError("Wrong period")

    # Prepare dataframe to calculate metrics for pools
    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)
    
    #Group by pools
    metrics_df = metrics_df.groupby('pool').agg({
        'ofac_compliant_count': ['sum'],
        'ofac_non_compliant_count': ['sum']
    }).reset_index()
    
    metrics_df.columns = metrics_df.columns.droplevel(1)
    
    
    # Get count of transactions of both types
    total_ofac_compliant_count = metrics_df.ofac_compliant_count.sum()
    total_ofac_non_compliant_count = (
        metrics_df.ofac_non_compliant_count.sum()
    )
    
    total_count = total_ofac_compliant_count + total_ofac_non_compliant_count
    metrics_df['total_share'] = 100 * (
        (metrics_df.ofac_compliant_count + metrics_df.ofac_non_compliant_count) / total_count
    )
    
    metrics_df.loc[metrics_df.pool == 'Other', 'total_share'] = 0
    
    metrics_df.ofac_compliant_count /= total_ofac_compliant_count
    metrics_df.ofac_non_compliant_count /= total_ofac_non_compliant_count
    
    metrics_df['ratio'] = (
        metrics_df.ofac_non_compliant_count / metrics_df.ofac_compliant_count
    )
    
    metrics_df.ratio = metrics_df.ratio.fillna(1)
    
    lido_vs_rest = metrics_df[['pool','ratio','total_share']].to_dict(orient = 'records')

    return lido_vs_rest


def get_overall_latency(
    txs_collection: Collection, validators_collection: Collection
) -> List[dict]:
    """
    Calculate the censorship latency for all non OFAC compliant transactions

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators

    Returns:
        List of censorship latency over all weeks
    """
    # Find min and max timestamps in censored transactions' mongo collection
    try:
        ts_df = pd.DataFrame(
            list(txs_collection.find({}, {"_id": 0, "block_ts": 1}))
        )

        ts_df.dropna(inplace=True)

        min_ts = int(ts_df.block_ts.min())
        max_ts = int(ts_df.block_ts.max())
    except Exception:
        raise Exception("Failed to fetch transactions data from db")

    # Calculate corrensponding weeks for min and max timestamps
    first_monday_ts, first_sunday_ts = get_week(min_ts)
    _, last_monday_ts = get_week(max_ts)
    first_monday = datetime.utcfromtimestamp(first_monday_ts)
    first_sunday = datetime.utcfromtimestamp(first_sunday_ts)
    last_monday = datetime.utcfromtimestamp(last_monday_ts)
    # Week difference between min and max timestamps' weeks
    week_diff = (last_monday - first_monday).days // 7

    latency = []

    try:
        lido_vals = validators_collection.distinct(
            "name", {"pool_name": "Lido"}
        )
    except:
        raise Exception("Failed to fetch validators data from db")    
    
    for shift in range(week_diff + 1):
        # For each available week find it's boundaries
        monday_ts, sunday_ts, monday_dt, sunday_dt = get_shifted_week(
            first_monday, first_sunday, shift
        )
        # Find censored transactions that were added to
        # the blockchain in a certain week
        shifted_df = pd.DataFrame(
            list(
                txs_collection.find(
                    {
                        "block_ts": {"$gte": monday_ts, "$lte": sunday_ts},
                        "non_ofac_compliant": True,
                    },
                    {"_id": 0, "censored": 1},
                )
            )
        )

        # Сalculate censorship metrics
        shifted_df["censorship_latency"] = (
            shifted_df.censored.apply(_get_count_of_censored_blocks) * 12
        )
        shifted_df[
            "censorship_latency_without_lido_censorship"
        ] = shifted_df.censored.apply(
            _calc_lido_latency, args=(lido_vals,)
        )

        record = {
            "start_date": monday_dt,
            "end_date": sunday_dt,
            "overall_censorship_latency": shifted_df.censorship_latency.mean(),
            "overall_censorship_latency_without_lido_censorship": shifted_df.censorship_latency_without_lido_censorship.mean(),
        }

        latency.append(record)

    return latency


def get_censored_latency(
    txs_collection: Collection,
    validators_collection: Collection,
    mean: str,
) -> List[dict]:
    """
    Calculate the censorship latency for non OFAC compliant censored transactions

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        mean                    -   Type of mean (average or median)

    Returns:
        List of censorship latency over all weeks
    """
    # Find min and max timestamps in censored transactions' mongo collection
    try:
        ts_df = pd.DataFrame(
            list(txs_collection.find({}, {"_id": 0, "block_ts": 1}))
        )

        ts_df.dropna(inplace=True)

        min_ts = int(ts_df.block_ts.min())
        max_ts = int(ts_df.block_ts.max())
    except Exception:
        raise Exception("Failed to fetch transactions data from db")

    # Calculate corrensponding weeks for min and max timestamps
    first_monday_ts, first_sunday_ts = get_week(min_ts)
    _, last_monday_ts = get_week(max_ts)
    first_monday = datetime.utcfromtimestamp(first_monday_ts)
    first_sunday = datetime.utcfromtimestamp(first_sunday_ts)
    last_monday = datetime.utcfromtimestamp(last_monday_ts)
    # Week difference between min and max timestamps' weeks
    week_diff = (last_monday - first_monday).days // 7

    latency = []

    try:
        lido_vals = validators_collection.distinct(
            "name", {"pool_name": "Lido"}
        )
    except:
        raise Exception("Failed to fetch validators data from db")    
    
    for shift in range(week_diff + 1):
        # For each available week find it's boundaries
        monday_ts, sunday_ts, monday_dt, sunday_dt = get_shifted_week(
            first_monday, first_sunday, shift
        )
        # Find censored transactions that were added to
        # the blockchain in a certain week
        shifted_df = pd.DataFrame(
            list(
                txs_collection.find(
                    {
                        "block_ts": {"$gte": monday_ts, "$lte": sunday_ts},
                        "non_ofac_compliant": True,
                    },
                    {"_id": 0, "censored": 1},
                )
            )
        )
        # Drop all non censored transactions
        shifted_df.dropna(axis=0, subset=["censored"], inplace=True)

        # Сalculate censorship metrics
        shifted_df["censorship_latency"] = (
            shifted_df.censored.apply(len) * 12
        )
        shifted_df[
            "censorship_latency_without_lido_censorship"
        ] = shifted_df.censored.apply(
            _calc_lido_latency, args=(lido_vals,)
        )

        if mean == "average":
            record = {
                "start_date": monday_dt,
                "end_date": sunday_dt,
                "average_censorship_latency": shifted_df.censorship_latency.mean(),
                "average_censorship_latency_without_lido_censorship": shifted_df.censorship_latency_without_lido_censorship.mean(),
            }
        if mean == "median":
            record = {
                "start_date": monday_dt,
                "end_date": sunday_dt,
                "median_censorship_latency": shifted_df.censorship_latency.median(),
                "median_censorship_latency_without_lido_censorship": shifted_df.censorship_latency_without_lido_censorship.median(),
            }

        latency.append(record)

    return latency


def get_censored_percentage(
    txs_collection: Collection,
    validators_collection: Collection,
    period: str,
) -> List[dict]:
    """
    Calculate the percentage of censored transactions

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators
        period                  -   Time period for which censorship metrics need to be calculated (last_week or last_month)

    Returns:
        Percentage of censored transactions
    """
    # Find min and max timestamps in censored transactions' mongo collection
    if period == 'last_week':
        dates = get_last_dates(0, 7)
    elif period == "last_month":
        dates = get_last_dates(0, 30)
    elif period ==  "last_half_year":
        dates = get_last_dates(0, 180)
    elif period ==  "last_year":
        dates = get_last_dates(0, 365)        
    else :
        raise ValueError("Wrong period")

    start_date = datetime.strptime(dates[-1], "%d-%m-%y")
    end_date = datetime.strptime(dates[-0], "%d-%m-%y")

    start_date_ts = int(
        start_date.replace(tzinfo=timezone.utc).timestamp()
    )
    end_date_ts = int(end_date.replace(tzinfo=timezone.utc).timestamp())

    non_compliant_txs_df = pd.DataFrame(
        list(
            txs_collection.find(
                {
                    "block_ts": {
                        "$gte": start_date_ts,
                        "$lte": end_date_ts,
                    },
                    "non_ofac_compliant": True,
                },
                {"_id": 0, "censored": 1},
            )
        )
    )

    try:
        lido_vals = validators_collection.distinct(
            "name", {"pool_name": "Lido"}
        )
    except:
        raise Exception("Failed to fetch validators data from db")

    censored_txs_df = non_compliant_txs_df.dropna(axis=0)

    # Сalculate censorship metrics
    censored_txs_df["censorship_latency"] = (
        censored_txs_df.censored.apply(len) * 12
    )
    censored_txs_df[
        "censorship_latency_without_lido_censorship"
    ] = censored_txs_df.censored.apply(
        _calc_lido_latency, args=(lido_vals,)
    )

    lido_censored_txs_df = censored_txs_df[
        censored_txs_df.censorship_latency
        != censored_txs_df.censorship_latency_without_lido_censorship
    ]

    percentage = {
        "censored_percentage": len(censored_txs_df)
        / len(non_compliant_txs_df)
        * 100,
        "lido_censored_percentage": len(lido_censored_txs_df)
        / len(non_compliant_txs_df)
        * 100,
    }

    return [percentage]
