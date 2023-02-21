from typing import List, Tuple
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

def _get_shifted_week(monday: datetime.datetime, sunday: datetime.datetime, shift: int) -> Tuple[int, int, str, str]:
    shifted_monday = monday + datetime.timedelta(days = shift * 7)
    shifted_sunday = sunday + datetime.timedelta(days = shift * 7)
    
    monday_ts = int(shifted_monday.timestamp())
    sunday_ts = int(shifted_sunday.timestamp())
    monday_dt = datetime.datetime.strftime(shifted_monday, '%d-%m-%y')
    sunday_dt = datetime.datetime.strftime(shifted_sunday, '%d-%m-%y')
    
    return monday_ts, sunday_ts, monday_dt, sunday_dt

def _get_week(ts: int) -> Tuple[int, int]:
    today = datetime.datetime.fromtimestamp(ts)
    this_week_monday = today - datetime.timedelta(
        days = today.weekday(), 
        seconds=today.second, 
        microseconds=today.microsecond, 
        minutes=today.minute, 
        hours=today.hour
    )
    this_week_sunday = this_week_monday + datetime.timedelta(days = 7) - datetime.timedelta(microseconds = 1)
    
    monday_ts = int(this_week_monday.timestamp())
    sunday_ts = int(this_week_sunday.timestamp())
    
    return monday_ts, sunday_ts

def _calc_lido_latency(censored_blocks: List[dict], lido_vals: List[str]) -> int:
    latency = 0
    for censored_block in censored_blocks:
        if censored_block['validator'] not in lido_vals:
            latency += 12
        else:
            break
            
    return latency

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

def get_latency(txs_collection: Collection, validators_collection: Collection) -> List[dict]:
    pipeline = [
        {"$group": {"_id": {}, "minTS": {"$min": '$timestamp'}, "maxTS": {"$max": "$timestamp"}}}
    ]
    agg_res = txs_collection.aggregate(pipeline).next()
    
    min_ts = agg_res['minTS']
    max_ts = agg_res['maxTS']
    
    first_monday_ts, first_sunday_ts = _get_week(min_ts)
    _, last_monday_ts = _get_week(max_ts)
    
    first_monday = datetime.datetime.fromtimestamp(first_monday_ts)
    first_sunday = datetime.datetime.fromtimestamp(first_sunday_ts)
    last_monday = datetime.datetime.fromtimestamp(last_monday_ts)
    
    week_diff = (last_monday - first_monday).days // 7
    
    latency = []

    lido_vals = validators_collection.distinct('name', {'pool_name': 'Lido'})
    
    for shift in range(week_diff + 1):
        monday_ts, sunday_ts, monday_dt, sunday_dt = _get_shifted_week(first_monday, first_sunday, shift)
        
        shifted_df = pd.DataFrame(list(txs_collection.find(
            {'timestamp': {'$gte': monday_ts, '$lte': sunday_ts},
             'non_ofac_compliant': True },
            {'_id':0, 'censored': 1})))

        shifted_df['censorship_latency'] = shifted_df.censored.apply(len) * 12
        shifted_df['censorship_latency_without_lido_censorship'] = shifted_df.censored.apply(_calc_lido_latency, args=(lido_vals, ))
        
        latency.append({
            'start_date': monday_dt,
            'end_date': sunday_dt,
            'censorship_latency': shifted_df.censorship_latency.mean(),
            'censorship_latency_without_lido_censorship': shifted_df.censorship_latency_without_lido_censorship.mean()
        })
        
    return latency