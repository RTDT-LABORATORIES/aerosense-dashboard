from dash import dcc

from aerosense_tools.queries import BigQuery


EXCLUDED_SENSORS = {"microphone", "information_sensors", "battery_info"}


def SensorSelect():
    sensor_types = [sensor for sensor in BigQuery().get_sensor_types() if sensor["name"] not in EXCLUDED_SENSORS]
    sensor_names = [sensor["name"] for sensor in sensor_types]

    return dcc.Dropdown(
        options=sensor_names,
        id="y-axis-select",
        value=sensor_names[0],
        persistence=True,
    )
