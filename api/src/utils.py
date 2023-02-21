import datetime


def str_date_repr(dt: datetime.timedelta) -> str:
    return datetime.datetime.strftime(dt, "%d-%m-%y")
