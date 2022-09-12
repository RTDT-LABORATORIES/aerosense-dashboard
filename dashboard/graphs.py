from plotly import express as px

from aerosense_tools.queries import BigQuery
from dashboard.utils import get_cleaned_sensor_column_names


def plot_connections_statistics(installation_reference, node_id, y_axis_column, start, finish):
    df = BigQuery().get_aggregated_connection_statistics(
        installation_reference=installation_reference,
        node_id=node_id,
        start=start,
        finish=finish,
    )

    figure = px.line(df, x="datetime", y=y_axis_column)
    figure.update_layout(xaxis_title="Date/time", yaxis_title="Raw value")
    return figure


def plot_sensors(installation_reference, node_id, sensor_name, start, finish):
    df, data_limit_applied = BigQuery().get_sensor_data(
        installation_reference,
        node_id,
        sensor_name,
        start=start,
        finish=finish,
    )

    original_sensor_names, cleaned_sensor_names = get_cleaned_sensor_column_names(df)

    df.rename(
        columns={
            original_name: cleaned_name
            for original_name, cleaned_name in zip(original_sensor_names, cleaned_sensor_names)
        },
        inplace=True,
    )

    figure = px.line(df, x="datetime", y=cleaned_sensor_names)
    figure.update_layout(xaxis_title="Date/time", yaxis_title="Raw value")
    return (figure, data_limit_applied)


def plot_pressure_bar_chart(df, minimum, maximum):
    original_sensor_names, cleaned_sensor_names = get_cleaned_sensor_column_names(df)
    df_transposed = df[original_sensor_names].transpose()
    df_transposed["Barometer number"] = cleaned_sensor_names

    if len(df) == 0:
        df_transposed["Raw value"] = 0
    else:
        df_transposed["Raw value"] = df_transposed.iloc[:, 0]

    figure = px.line(df_transposed, x="Barometer number", y="Raw value")
    figure.add_bar(x=df_transposed["Barometer number"], y=df_transposed["Raw value"])
    figure.update_layout(showlegend=False, yaxis_range=[minimum, maximum])
    return figure
