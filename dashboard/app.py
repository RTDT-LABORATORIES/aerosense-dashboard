import dash
from dash import html
from flask_caching import Cache

from aerosense_tools.queries import BigQuery
from dashboard.callbacks import register_callbacks
from dashboard.layouts import create_pressure_profile_tab_layout, create_sensors_tab_layout


SENSOR_TYPES = BigQuery().get_sensor_types()
EXCLUDED_SENSORS = {"microphone", "connection_statistics", "battery_info"}

app = dash.Dash(
    name=__name__,
    assets_folder="../assets",
    title="Aerosense Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.config.suppress_callback_exceptions = True

server = app.server

CACHE_TIMEOUT = 3600
cache = Cache(server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".dashboard_cache"})

tabs = {
    "information_sensors": create_sensors_tab_layout(
        app,
        tab_name="information_sensors",
        sensor_names=["tx_power", "filtered_rssi", "raw_rssi", "allocated_heap_memory", "battery_info"],
        graph_id="information-sensors-graph",
        data_limit_warning_id="information-sensor-data-limit-warning",
    ),
    "sensors": create_sensors_tab_layout(
        app,
        tab_name="sensors",
        sensor_names=[sensor for sensor in SENSOR_TYPES if sensor not in EXCLUDED_SENSORS],
        graph_id="sensors-graph",
        data_limit_warning_id="sensor-data-limit-warning",
    ),
    "pressure_profile": create_pressure_profile_tab_layout(app),
}

app.layout = html.Div(
    [html.Div(tabs["information_sensors"], id="app")],
    className="row flex-display",
    style={"height": "100vh"},
)

register_callbacks(
    app,
    cache=cache,
    cache_timeout=CACHE_TIMEOUT,
    tabs=tabs,
    sensor_types=SENSOR_TYPES,
)


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
