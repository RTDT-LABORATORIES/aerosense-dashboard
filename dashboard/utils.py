import datetime


TIME_RANGE_OPTIONS = {
    "Last minute": datetime.timedelta(minutes=1),
    "Last hour": datetime.timedelta(hours=1),
    "Last day": datetime.timedelta(days=1),
    "Last week": datetime.timedelta(weeks=1),
    "Last month": datetime.timedelta(days=31),
    "Last year": datetime.timedelta(days=365),
}


def generate_time_range(time_range, measurement_session=None):
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
    :param str|None measurement_session:
    :return (datetime.datetime, datetime.datetime, bool): the start and finish datetimes
    """
    if time_range == "All time":
        return datetime.datetime.min, datetime.datetime.utcnow()

    if time_range == "Measurement session":
        try:
            start, finish = measurement_session.split(" to ")
            start = datetime.datetime.fromisoformat(start)
            finish = datetime.datetime.fromisoformat(finish)
            return start, finish
        except (ValueError, AttributeError):
            return None, None

    finish = datetime.datetime.utcnow()
    start = finish - TIME_RANGE_OPTIONS[time_range]
    return start, finish
