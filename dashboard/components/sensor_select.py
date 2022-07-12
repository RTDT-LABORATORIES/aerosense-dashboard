from dash import dcc

from dashboard.queries import BigQuery


def SensorSelect():
    sensor_types = BigQuery().get_sensor_types()

    return dcc.Dropdown(
        options=sensor_types,
        id="y-axis-select",
        value=sensor_types[0],
        persistence=True,
    )
