from typing import List
from pymongo.collection import Collection
import pandas as pd

import datetime

from utils import get_last_dates, get_shifted_week, get_week


def _get_validators_metrics(collection: Collection, dates: List[str]) -> pd.DataFrame:
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
            count += len(row[day].get("non_ofac_compliant_txs", []))

    return count


def _get_ofac_compliant_share(row: pd.Series, df: pd.DataFrame) -> float:
    """
    Calculate the share of a particular validator in the validation of ofac compliant transactions inside Ethereum blockchain

    Args:
        row -   Pandas series corresconding to the specific validator
        df  -   Whole dataframe with metrics

    Returns:
        Share of a particular validator in the validation of ofac compliant transactions inside Ethereum blockchain in percents
    """
    return 100 * row["ofac_compliant_count"] / df.ofac_compliant_count.sum()


def _get_ofac_non_compliant_share(row: pd.Series, df: pd.DataFrame) -> float:
    """
    Calculate the share of a particular validator in the validation of ofac non compliant transactions inside Ethereum blockchain

    Args:
        row -   Pandas series corresconding to the specific validator
        df  -   Whole dataframe with metrics

    Returns:
        Share of a particular validator in the validation of ofac non compliant transactions inside Ethereum blockchain in percents
    """
    return 100 * row["ofac_non_compliant_count"] / df.ofac_non_compliant_count.sum()


def _get_ratio(row: pd.Series) -> float:
    """
    Calculate the ratio between validator's ofac non compliant share and validator's ofac compliant share

    Args:
        row -   Pandas series corresconding to the specific validator

    Returns:
        Ratio between validator's ofac non compliant share and validator's ofac compliant share
    """
    if row["ofac_compliant_share"] != 0:
        return row["ofac_non_compliant_share"] / row["ofac_compliant_share"]
    else:
        return 1


def _prepare_share_df(df: pd.DataFrame, dates: List[str]) -> pd.DataFrame:
    """
    Calculate "share metric" over dataframe

    Args:
        df      -   Pandas dataframe with metrics
        dates   -   List of dates for which tmetrics need to be calculated

    Returns:
        Pandas dataframe with calculated metrics
    """
    _df = df.copy()

    _df["ofac_compliant_count"] = _df.apply(
        _get_ofac_compliant_count, axis=1, args=(dates,)
    )
    _df["ofac_non_compliant_count"] = _df.apply(
        _get_ofac_non_compliant_count, axis=1, args=(dates,)
    )

    _df["ofac_compliant_share"] = _df[df.name != "Other"].apply(
        _get_ofac_compliant_share, axis=1, args=(_df,)
    )
    _df["ofac_non_compliant_share"] = _df[df.name != "Other"].apply(
        _get_ofac_non_compliant_share, axis=1, args=(_df,)
    )

    # Select only needed colunms
    _df = _df[
        [
            "name",
            "ofac_compliant_count",
            "ofac_non_compliant_count",
            "ofac_compliant_share",
            "ofac_non_compliant_share",
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

    _df["ratio"] = _df[_df.name != "Other"].apply(_get_ratio, axis=1)

    _df = _df[["name", "ratio"]]

    return _df


def _calc_lido_latency(censored_blocks: List[dict], lido_vals: List[str]) -> int:
    """
    Calculate the censorship latency in case the Lido validators would not censor OFAC non compliant transactions

    Args:
        censored_blocks -   List of censored blocks
        lido_vals       -   List of Lido validators

    Returns:
        Censorship latency in case the Lido validators would not censor OFAC non compliant transactions in seconds
    """
    latency = 0
    if not isinstance(censored_block, list):
        return latency
    for censored_block in censored_blocks:
        # If we find validators of lido in the list of censors,
        # we will assume that he validated the transaction and
        # there was no further censorship
        if censored_block["validator"] not in lido_vals:
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
    if period == "last_week":
        dates = get_last_dates(0, 7)
    elif period == "last_month":
        dates = get_last_dates(0, 30)
    else:
        raise ValueError("Wrong period")

    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)

    metrics_df = metrics_df[
        ["name", "ofac_compliant_share", "ofac_non_compliant_share"]
    ]

    if calc_ratio:
        metrics_df = _prepare_ratio_df(metrics_df)

    metrics_df = metrics_df[metrics_df.name != "Other"]

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
    if period == "last_week":
        dates = get_last_dates(0, 7)
    elif period == "last_month":
        dates = get_last_dates(0, 30)
    else:
        raise ValueError("Wrong period")

    # Prepare dataframe to calculate metrics for pools
    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)
    # Get count of transactions of both types
    total_ofac_compliant_count = metrics_df.ofac_compliant_count.sum()
    total_ofac_non_compliant_count = metrics_df.ofac_non_compliant_count.sum()

    lido_ofac_compliant_count = metrics_df[
        metrics_df.name != "Other"
    ].ofac_compliant_count.sum()
    lido_ofac_non_compliant_count = metrics_df[
        metrics_df.name != "Other"
    ].ofac_non_compliant_count.sum()
    # Calculate share of Lido
    lido_ofac_compliant_share = lido_ofac_compliant_count / total_ofac_compliant_count
    lido_ofac_non_compliant_share = (
        lido_ofac_non_compliant_count / total_ofac_non_compliant_count
    )
    # Calculate share of other pools together
    other_ofac_compliant_share = (
        metrics_df[metrics_df.name == "Other"].ofac_compliant_count.values[0]
        / total_ofac_compliant_count
    )
    other_ofac_non_compliant_share = (
        metrics_df[metrics_df.name == "Other"].ofac_non_compliant_count.values[0]
        / total_ofac_non_compliant_count
    )

    lido_ratio = lido_ofac_non_compliant_share / lido_ofac_compliant_share
    other_ratio = other_ofac_non_compliant_share / other_ofac_compliant_share

    lido_vs_rest = [
        {"pool": "lido", "ratio": lido_ratio},
        {"pool": "other pools", "ratio": other_ratio},
    ]

    return lido_vs_rest


def get_latency(
    txs_collection: Collection, validators_collection: Collection
) -> List[dict]:
    """
    Calculate the censorship latency

    Args:
        txs_collection          -   Mongo collection of censored transactions
        validators_collection   -   Mongo collection of validators

    Returns:
        List of censorship latency over all weeks
    """
    # Find min and max timestamps in censored transactions' mongo collection
    try:
        ts_df = pd.DataFrame(list(txs_collection.find({}, {"_id": 0, "block_ts": 1})))

        ts_df.dropna(inplace=True)

        min_ts = int(ts_df.block_ts.min())
        max_ts = int(ts_df.block_ts.max())
    except Exception:
        raise Exception("Failed to fetch transactions data from db")

    # Calculate corrensponding weeks for min and max timestamps
    first_monday_ts, first_sunday_ts = get_week(min_ts)
    _, last_monday_ts = get_week(max_ts)
    first_monday = datetime.datetime.utcfromtimestamp(first_monday_ts)
    first_sunday = datetime.datetime.utcfromtimestamp(first_sunday_ts)
    last_monday = datetime.datetime.utcfromtimestamp(last_monday_ts)
    # Week difference between min and max timestamps' weeks
    week_diff = (last_monday - first_monday).days // 7

    latency = []
    # List of Lido validators
    try:
        lido_vals = validators_collection.distinct("name", {"pool_name": "Lido"})
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
        ] = shifted_df.censored.apply(_calc_lido_latency, args=(lido_vals,))
        latency.append(
            {
                "start_date": monday_dt,
                "end_date": sunday_dt,
                "censorship_latency": shifted_df.censorship_latency.mean(),
                "censorship_latency_without_lido_censorship": shifted_df.censorship_latency_without_lido_censorship.mean(),
            }
        )

    return latency
