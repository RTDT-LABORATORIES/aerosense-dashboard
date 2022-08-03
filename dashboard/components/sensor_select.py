from dash import dcc

from dashboard.queries import BigQuery


def SensorSelect():
    sensor_types = [sensor_type for sensor_type in BigQuery().get_sensor_types() if sensor_type != "microphone"]

    return dcc.Dropdown(
        options=sensor_types,
        id="y-axis-select",
        value=sensor_types[0],
        persistence=True,
    )
