import datetime
import datetime as dt


TIME_RANGE_OPTIONS = {
    "Last minute": datetime.timedelta(minutes=1),
    "Last hour": datetime.timedelta(hours=1),
    "Last day": datetime.timedelta(days=1),
    "Last week": datetime.timedelta(weeks=1),
    "Last month": datetime.timedelta(days=31),
    "Last year": datetime.timedelta(days=365),
}


def _combine_dates_and_times(
    start_date,
    start_hour,
    start_minute,
    start_second,
    end_date,
    end_hour,
    end_minute,
    end_second,
):
    """If all inputs are given, combine the start inputs into a start datetime and the end inputs into an end datetime;
    otherwise, return `None` as the start and end datetimes.

    :param str|None start_date:
    :param int|None start_hour:
    :param int|None start_minute:
    :param int|None start_second:
    :param str|None end_date:
    :param int|None end_hour:
    :param int|None end_minute:
    :param int|None end_second:
    :return (datetime.datetime, datetime.datetime)|(None, None):
    """
    if all(
        argument is not None
        for argument in (
            start_date,
            start_hour,
            start_minute,
            start_second,
            end_date,
            end_hour,
            end_minute,
            end_second,
        )
    ):
        start = datetime.datetime.combine(
            dt.date.fromisoformat(start_date),
            datetime.time(hour=start_hour, minute=start_minute, second=start_second),
        )

        end = datetime.datetime.combine(
            dt.date.fromisoformat(end_date),
            datetime.time(hour=end_hour, minute=end_minute, second=end_second),
        )

        return (start, end)

    return (None, None)


def generate_time_range(
    time_range,
    start_date=None,
    start_hour=None,
    start_minute=None,
    start_second=None,
    end_date=None,
    end_hour=None,
    end_minute=None,
    end_second=None,
):
    """Generate a convenient time range to plot. The options are:
    - Last minute
    - Last hour
    - Last day
    - Last week
    - Last month
    - Last year
    - All time
    - Measurement session

    :param str time_range:
    :param str|None measurement_session:
    :return (datetime.datetime, datetime.datetime, bool): the start and finish datetimes
    """
    if time_range == "All time":
        return datetime.datetime.min, datetime.datetime.utcnow()

    if time_range == "Custom":
        try:
            return _combine_dates_and_times(
                start_date,
                start_hour,
                start_minute,
                start_second,
                end_date,
                end_hour,
                end_minute,
                end_second,
            )
        except (ValueError, AttributeError):
            return None, None

    finish = datetime.datetime.utcnow()
    start = finish - TIME_RANGE_OPTIONS[time_range]
    return start, finish
