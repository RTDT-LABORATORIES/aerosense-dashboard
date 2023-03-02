from dash import dcc

from aerosense_tools.queries import BigQuery


def SensorSelect(excluded_sensors=None):
    excluded_sensors = excluded_sensors or []
    sensor_types = [sensor for sensor in BigQuery().get_sensor_types() if sensor["name"] not in excluded_sensors]
    sensor_names = [sensor["name"] for sensor in sensor_types]

    return dcc.Dropdown(
        options=sensor_names,
        id="y-axis-select",
        value=sensor_names[0],
        persistence=True,
    )
