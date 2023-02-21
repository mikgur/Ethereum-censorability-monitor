import datetime
from typing import List, Tuple


def str_date_repr(dt: datetime.timedelta) -> str:
    return datetime.datetime.strftime(dt, "%d-%m-%y")


def get_last_dates(period_start: int, period_end: int) -> List[str]:
    return [
        str_date_repr(datetime.date.today() - datetime.timedelta(days=i))
        for i in range(period_start, period_end)
    ]


def get_shifted_week(
    monday: datetime.datetime, sunday: datetime.datetime, shift: int
) -> Tuple[int, int, str, str]:
    shifted_monday = monday + datetime.timedelta(days=shift * 7)
    shifted_sunday = sunday + datetime.timedelta(days=shift * 7)

    monday_ts = int(shifted_monday.timestamp())
    sunday_ts = int(shifted_sunday.timestamp())
    monday_dt = datetime.datetime.strftime(shifted_monday, "%d-%m-%y")
    sunday_dt = datetime.datetime.strftime(shifted_sunday, "%d-%m-%y")

    return monday_ts, sunday_ts, monday_dt, sunday_dt


def get_week(ts: int) -> Tuple[int, int]:
    today = datetime.datetime.fromtimestamp(ts)
    this_week_monday = today - datetime.timedelta(
        days=today.weekday(),
        seconds=today.second,
        microseconds=today.microsecond,
        minutes=today.minute,
        hours=today.hour,
    )
    this_week_sunday = (
        this_week_monday
        + datetime.timedelta(days=7)
        - datetime.timedelta(microseconds=1)
    )

    monday_ts = int(this_week_monday.timestamp())
    sunday_ts = int(this_week_sunday.timestamp())

    return monday_ts, sunday_ts
