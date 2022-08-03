import datetime

from plotly import express as px

from dashboard.queries import BigQuery


def _generate_time_range(time_range):
    """Generate a convenient time range to plot. The options are:
    - Last minute
    - Last hour
    - Last day
    - Last week
    - Last month
    - Last year
    - All time

    :param str time_range:
    :return (datetime.datetime, datetime.datetime, bool): the start datetime, finish datetime, and whether all time has been selected
    """
    time_range_options = {
        "Last minute": datetime.timedelta(minutes=1),
        "Last hour": datetime.timedelta(hours=1),
        "Last day": datetime.timedelta(days=1),
        "Last week": datetime.timedelta(weeks=1),
        "Last month": datetime.timedelta(days=31),
        "Last year": datetime.timedelta(days=365),
    }

    if time_range == "All time":
        all_time = True
        start = None
        finish = None
    else:
        all_time = False
        finish = datetime.datetime.now()
        start = finish - time_range_options[time_range]

    return start, finish, all_time


def plot_connections_statistics(installation_reference, node_id, y_axis_column, time_range):
    start, finish, all_time = _generate_time_range(time_range)

    df = BigQuery().get_aggregated_connection_statistics(
        installation_reference,
        node_id,
        start=start,
        finish=finish,
        all_time=all_time,
    )

    figure = px.line(df, x="datetime", y=y_axis_column)
    return figure


def plot_sensors(installation_reference, node_id, sensor_name, time_range):
    start, finish, all_time = _generate_time_range(time_range)

    df = BigQuery().get_sensor_data(
        installation_reference,
        node_id,
        sensor_name,
        start=start,
        finish=finish,
        all_time=all_time,
    )

    return px.line(
        df,
        x="datetime",
        y=[column for column in df.columns if column.startswith("f") and column.endswith("_")],
    )
