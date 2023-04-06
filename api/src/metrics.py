from typing import List
from pymongo.collection import Collection
import pandas as pd

from  datetime import datetime, timezone

from utils import get_last_dates, get_shifted_week, get_week


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
    if period == "last_week" and calc_ratio:
        data = collection.find_one({
            "metrics":"last_week_validators_censorship_resistance_index"
        })
    elif period == "last_week" and not calc_ratio:
        data = collection.find_one({
            "metrics":"last_week_validators_compliance_ratio"
        })
    elif period == "last_month" and calc_ratio:
        data = collection.find_one({
            "metrics":"last_month_validators_censorship_resistance_index"
        })
    elif period == "last_month" and not calc_ratio:
        data = collection.find_one({
            "metrics":"last_month_validators_compliance_ratio"
        })
    else:
        raise ValueError("Wrong period")

    return data["values"]


def get_lido_vs_rest(collection: Collection, period: str) -> List[dict]:
    """
    Calculate "ratio metric" for Lido and other pools

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated (last_week or last_month)

    Returns:
        List of dicts with metrics for Lido and other pools
    """
    if period == "last_week":
        data = collection.find_one({
            "metrics":"last_week_lido_vs_rest_censorship_resistance_index"
        })
    elif period == "last_month":
        data = collection.find_one({
            "metrics":"last_month_lido_vs_rest_censorship_resistance_index"
        })
    else:
        raise ValueError("Wrong period")

    return data["values"]


def get_overall_latency(collection: Collection) -> List[dict]:
    """
    Calculate the censorship latency for all non OFAC compliant transactions

    Args:
        collection  -   Mongo collection of metrics

    Returns:
        List of censorship latency over all weeks
    """

    data = collection.find_one({
        "metrics":"overall_average_latency"
    })

    return data["values"]


def get_censored_latency(collection: Collection) -> List[dict]:
    """
    Calculate the censorship latency for non OFAC compliant censored transactions

    Args:
        collection  -   Mongo collection of metrics                -   Type of mean (average or median)

    Returns:
        List of censorship latency over all weeks
    """

    data = collection.find_one({
        "metrics":"censored_average_latency"
    })

    return data["values"]


def get_censored_percentage(
    collection: Collection
) -> List[dict]:
    """
    Calculate the percentage of censored transactions

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated (last_week or last_month)

    Returns:
        Percentage of censored transactions
    """
    
    data = collection.find_one({
        "metrics":"censored_percentage"
    })

    return data["values"]
