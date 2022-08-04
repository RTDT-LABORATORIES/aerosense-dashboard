import datetime


TIME_RANGE_OPTIONS = {
    "Last minute": datetime.timedelta(minutes=1),
    "Last hour": datetime.timedelta(hours=1),
    "Last day": datetime.timedelta(days=1),
    "Last week": datetime.timedelta(weeks=1),
    "Last month": datetime.timedelta(days=31),
    "Last year": datetime.timedelta(days=365),
}


def generate_time_range(time_range, custom_start_date=None, custom_end_date=None):
    """Generate a convenient time range to plot. The options are:
    - Last minute
    - Last hour
    - Last day
    - Last week
    - Last month
    - Last year
    - All time
    - Custom

    :param str time_range:
    :param datetime.date|None custom_start_date:
    :param datetime.date|None custom_end_date:
    :return (datetime.datetime, datetime.datetime, bool): the start and finish datetimes
    """
    if time_range == "All time":
        return datetime.datetime.min, datetime.datetime.now()

    if time_range == "Custom":
        return custom_start_date, custom_end_date

    finish = datetime.datetime.now()
    start = finish - TIME_RANGE_OPTIONS[time_range]
    return start, finish
