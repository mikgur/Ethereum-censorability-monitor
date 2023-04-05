import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple


def str_date_repr(dt: timedelta) -> str:
    """
    Wrapper for the strftime

    Args:
        dt  -   Datetime object

    Returns:
        Datetime object's representation as the string in the dd-mm-yy format
    """
    return datetime.strftime(dt, "%d-%m-%y")


def get_last_dates(period_start: int, period_end: int) -> List[str]:
    """
    Get last n dates

    Args:
        period_start    -   Day difference between today and the last date of the date range
        period_end      -   Day difference between today and the first date of the date range

    Returns:
        List of dates that started period_end days ago and finished period_end days ago
    """
    return [
        str_date_repr(datetime.utcnow().date() - timedelta(days=i))
        for i in range(period_start, period_end)
    ]


def get_shifted_week(
    monday: datetime, sunday: datetime, shift: int
) -> Tuple[int, int, str, str]:
    """
    Get shifted week

    Args:
        monday  -   Original week's monday datetime object
        sunday  -   Original week's sunday datetime object
        shift   -   Shift in weeks

    Returns:
        Shifted week's monday and sunday timestamps and dates
    """
    shifted_monday = monday + timedelta(days=shift * 7)
    shifted_sunday = sunday + timedelta(days=shift * 7)

    monday_ts = int(
        shifted_monday.replace(tzinfo=timezone.utc).timestamp()
    )
    sunday_ts = int(
        shifted_sunday.replace(tzinfo=timezone.utc).timestamp()
    )
    monday_dt = datetime.strftime(shifted_monday, "%d-%m-%y")
    sunday_dt = datetime.strftime(shifted_sunday, "%d-%m-%y")

    return monday_ts, sunday_ts, monday_dt, sunday_dt


def get_week(ts: int) -> Tuple[int, int]:
    """
    Get week's borders based on timestamp

    Args:
        ts  -   Timestamp of the specific datetime

    Returns:
        Week's monday and sunday timestamps and dates corresponding to the given timestamp
    """
    today = datetime.utcfromtimestamp(ts)
    this_week_monday = today - timedelta(
        days=today.weekday(),
        seconds=today.second,
        microseconds=today.microsecond,
        minutes=today.minute,
        hours=today.hour,
    )
    this_week_sunday = (
        this_week_monday + timedelta(days=7) - timedelta(microseconds=1)
    )

    monday_ts = int(
        this_week_monday.replace(tzinfo=timezone.utc).timestamp()
    )
    sunday_ts = int(
        this_week_sunday.replace(tzinfo=timezone.utc).timestamp()
    )

    return monday_ts, sunday_ts


def init_logger() -> logging.Logger:
    """
    Initialize logger

    Returns:
        Logger
    """
    logger = logging.getLogger("nwatch_logger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s \t [%(levelname)s | %(filename)s:%(lineno)s] > %(message)s"
    )

    now = datetime.now()
    dirname = "./log"

    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    fileHandler = logging.FileHandler(
        dirname + "/log_" + now.strftime("%Y-%m-%d") + ".log"
    )

    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    return logger
