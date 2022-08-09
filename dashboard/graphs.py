import re

from plotly import express as px

from dashboard.queries import BigQuery
from dashboard.utils import generate_time_range


def plot_connections_statistics(
    installation_reference,
    node_id,
    y_axis_column,
    time_range,
    custom_start_date,
    custom_end_date,
):
    start, finish = generate_time_range(time_range, custom_start_date, custom_end_date)

    df = BigQuery().get_aggregated_connection_statistics(
        installation_reference,
        node_id,
        start=start,
        finish=finish,
    )

    figure = px.line(df, x="datetime", y=y_axis_column)
    return figure


def plot_sensors(installation_reference, node_id, sensor_name, time_range, custom_start_date, custom_end_date):
    start, finish = generate_time_range(time_range, custom_start_date, custom_end_date)

    df, data_limit_applied = BigQuery().get_sensor_data(
        installation_reference,
        node_id,
        sensor_name,
        start=start,
        finish=finish,
    )

    return (
        px.line(
            df,
            x="datetime",
            y=[column for column in df.columns if column.startswith("f") and column.endswith("_")],
        ),
        data_limit_applied,
    )


def plot_pressure_bar_chart(installation_reference, node_id, datetime):
    df = BigQuery().get_sensor_data_at_datetime(installation_reference, node_id, "barometer", datetime, tolerance=1)

    sensor_names = [column for column in df.columns if column.startswith("f") and column.endswith("_")]

    df_transposed = df[sensor_names].transpose()
    df_transposed["Barometer number"] = [re.findall(r"f(\d+)_", sensor_name)[0] for sensor_name in sensor_names]

    if len(df) == 0:
        df_transposed[0] = 0

    df_transposed["Raw value"] = df_transposed[0]

    figure = px.line(df_transposed, x="Barometer number", y="Raw value")
    figure.add_bar(x=df_transposed["Barometer number"], y=df_transposed["Raw value"])
    figure.update_layout(showlegend=False)
    return figure
