import datetime

from plotly import express as px

from dashboard.queries import get_connection_statistics_agg


def plot_connections_statistics(installation_reference, y_axis_column, time_range):
    time_range_options = {
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

    df = get_connection_statistics_agg(installation_reference, start=start, finish=finish, all_time=all_time)
    figure = px.line(df, x="datetime", y=y_axis_column)
    return figure
