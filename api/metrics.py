from typing import List
from pymongo.collection import Collection
import pandas as pd

import datetime
import json

from utils import str_date_repr


def _get_last_dates(period_start: int, period_end: int) -> List[str]:
    return [str_date_repr(datetime.date.today() - datetime.timedelta(days = i)) for i in range(period_start,period_end)]

def _get_validators_metrics(collection: Collection, dates: List[str]) -> pd.DataFrame:
    fields_dict = {date:1 for date in dates}
    fields_dict['_id'] = 0
    fields_dict['name'] = 1

    cursor = collection.find({}, fields_dict)
    records = list(cursor)

    return pd.DataFrame(records)

def _get_ofac_compliant_count(row: pd.Series, dates: List[str]) -> int:
    count = 0
    for day in dates:
        if day in row.keys():
            count += row[day]['num_ofac_compliant_txs']

    return count

def _get_ofac_non_compliant_count(row: pd.Series, dates: List[str]) -> int:
    count = 0
    for day in dates:
        if day in row.keys():
            count += row[day]['num_non_ofac_compliant_txs']

    return count

def _get_ofac_compliant_share(row: pd.Series, df: pd.DataFrame) -> float:
    return 100 * row['ofac_compliant_count'] / df[df.name != 'Other'].ofac_compliant_count.sum()

def _get_ofac_non_compliant_share(row: pd.Series, df: pd.DataFrame) -> float:
    return 100 * row['ofac_non_compliant_count'] / df[df.name != 'Other'].ofac_non_compliant_count.sum()

def _get_ratio(row: pd.Series) -> float:
    if row['ofac_compliant_share'] != 0:
        return row['ofac_non_compliant_share'] / row['ofac_compliant_share']
    else:
        return 1
    
def _prepare_share_df(df: pd.DataFrame, dates: List[str]) -> pd.DataFrame:
    _df = df.copy()

    _df['ofac_compliant_count'] = _df.apply(_get_ofac_compliant_count, axis = 1, args=(dates, ))
    _df['ofac_non_compliant_count'] = _df.apply(_get_ofac_non_compliant_count, axis = 1, args=(dates, ))

    _df['ofac_compliant_share'] = _df[df.name != 'Other'].apply(_get_ofac_compliant_share, axis=1, args=(_df, ))
    _df['ofac_non_compliant_share'] = _df[df.name != 'Other'].apply(_get_ofac_non_compliant_share, axis=1, args=(_df, ))

    _df = _df[['name','ofac_compliant_count','ofac_non_compliant_count','ofac_compliant_share', 'ofac_non_compliant_share']]

    return _df

def _prepare_ratio_df(share_df: pd.DataFrame) -> pd.DataFrame:
    _df = share_df.copy()

    _df['ratio'] = _df[_df.name != 'Other'].apply(_get_ratio, axis = 1)

    _df = _df[['name','ratio']]

    return _df

def get_lido_validators_metrics(collection: Collection, period: str, calc_share: bool) -> str:
    if period == 'last_week':
        dates = _get_last_dates(0,7)
    elif period == 'last_month':
        dates = _get_last_dates(0,30)

    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)

    metrics_df = metrics_df[['name', 'ofac_compliant_share', 'ofac_non_compliant_share']]

    if calc_share:
        metrics_df = _prepare_ratio_df(metrics_df)

    metrics_df = metrics_df[metrics_df.name != 'Other']

    return metrics_df.to_json(orient='records')

def get_lido_vs_rest(collection: Collection, period: str) -> str:
    if period == 'last_week':
        dates = _get_last_dates(0,7)
    elif period == 'last_month':
        dates = _get_last_dates(0,30)

    metrics_df = _get_validators_metrics(collection, dates)
    metrics_df = _prepare_share_df(metrics_df, dates)

    total_ofac_compliant_count = metrics_df.ofac_compliant_count.sum()
    total_ofac_non_compliant_count = metrics_df.ofac_non_compliant_count.sum()

    lido_ofac_compliant_count = metrics_df[metrics_df.name != 'Other'].ofac_compliant_count.sum()
    lido_ofac_non_compliant_count = metrics_df[metrics_df.name != 'Other'].ofac_non_compliant_count.sum()

    lido_ofac_compliant_share = lido_ofac_compliant_count / total_ofac_compliant_count
    lido_ofac_non_compliant_share = lido_ofac_non_compliant_count / total_ofac_non_compliant_count

    other_ofac_compliant_share = metrics_df[metrics_df.name == 'Other'].ofac_compliant_count.values[0] / total_ofac_compliant_count
    other_ofac_non_compliant_share = metrics_df[metrics_df.name == 'Other'].ofac_non_compliant_count.values[0] / total_ofac_non_compliant_count

    lido_ratio = lido_ofac_non_compliant_share / lido_ofac_compliant_share
    other_ratio = other_ofac_non_compliant_share / other_ofac_compliant_share

    lido_vs_rest = [{
        'pool': 'lido',
        'ratio': lido_ratio
    },
    {
        'pool': 'other pools',
        'ratio': other_ratio
    }]

    return json.dumps(lido_vs_rest)