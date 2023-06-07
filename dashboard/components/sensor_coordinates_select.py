from dash import dcc

from aerosense_tools.queries import BigQuery


def SensorCoordinatesSelect():
    sensor_coordinates = BigQuery().get_sensor_coordinates()

    return dcc.Dropdown(
        options=sensor_coordinates["reference"],
        id="sensor-coordinates-reference-input",
        value=sensor_coordinates.iloc[0]["reference"],
        persistence=True,
    )
