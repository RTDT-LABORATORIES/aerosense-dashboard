from dash import dcc


def SensorSelect(sensor_names):
    return dcc.Dropdown(
        options=sensor_names,
        id="y-axis-select",
        value=sensor_names[0],
        persistence=True,
    )
