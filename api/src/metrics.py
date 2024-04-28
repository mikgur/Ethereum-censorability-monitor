from typing import List

from pymongo.collection import Collection


def get_lido_validators_metrics(
    collection: Collection, period: str, calc_ratio: bool
) -> List[dict]:
    """
    Calculate censorship metrics over specific time period

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated
        calc_ratio  -   Calculate "ratio metric" or not

    Returns:
        List of dicts with metrics for each Lido validator
    """
    if period in ['last_week','last_month','last_3_months','last_half_year','last_year']:
        if calc_ratio:
            data = collection.find_one(
                {"metrics": f"{period}_validators_censorship_resistance_index"}
            )
        else:
            data = collection.find_one({"metrics": f"{period}_validators_compliance_ratio"})
    else:
        raise ValueError("Wrong period")

    return data["values"]


def get_lido_vs_rest(collection: Collection, period: str) -> List[dict]:
    """
    Calculate "ratio metric" for Lido and other pools

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated

    Returns:
        List of dicts with metrics for Lido and other pools
    """
    if period in ['last_week','last_month','last_3_months','last_half_year','last_year']:
        data = collection.find_one(
            {"metrics": f"{period}_lido_vs_rest_censorship_resistance_index"}
        )
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

    data = collection.find_one({"metrics": "overall_average_latency"})

    return data["values"]


def get_censored_latency(collection: Collection) -> List[dict]:
    """
    Calculate the censorship latency for non OFAC compliant censored transactions

    Args:
        collection  -   Mongo collection of metrics                -   Type of mean (average or median)

    Returns:
        List of censorship latency over all weeks
    """

    data = collection.find_one({"metrics": "censored_average_latency"})

    return data["values"]


def get_censored_percentage(collection: Collection) -> List[dict]:
    """
    Calculate the percentage of censored transactions

    Args:
        collection  -   Mongo collection of metrics
        period      -   Time period for which censorship metrics need to be calculated (last_week or last_month)

    Returns:
        Percentage of censored transactions
    """

    data = collection.find_one({"metrics": "censored_percentage"})

    return data["values"]
