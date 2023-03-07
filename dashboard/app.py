import dash
import dash_daq as daq
from dash import dcc, html
from flask_caching import Cache

from aerosense_tools.queries import BigQuery
from dashboard.callbacks import register_callbacks
from dashboard.components import About, InstallationSelect, Logo, Navigation, Title
from dashboard.components.node_select import NodeSelect
from dashboard.layouts import create_sensors_tab_layout


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
    "pressure_profile": [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Navigation(selected_tab="pressure_profile"),
                html.Br(),
                html.Div(
                    [
                        html.Label(html.B("Installation")),
                        html.Label("Installation reference"),
                        InstallationSelect(),
                        html.Label("Node id"),
                        NodeSelect(),
                        html.Br(),
                        html.Label(html.B("Start date/time")),
                        html.Label("Date"),
                        dcc.DatePickerSingle(
                            id="date-select",
                            display_format="Do MMM Y",
                            persistence=True,
                        ),
                        html.Br(),
                        html.Label("Hour"),
                        daq.NumericInput(id="hour", value=0, min=0, max=23, persistence=True),
                        html.Label("Minute"),
                        daq.NumericInput(id="minute", value=0, min=0, max=59, persistence=True),
                        html.Label("Second"),
                        daq.NumericInput(id="second", value=0, min=0, max=59, persistence=True),
                        html.Br(),
                        html.Label(html.B("Step forward (seconds)")),
                        html.Br(),
                        dcc.Slider(
                            id="time-slider",
                            min=0,
                            max=60,
                            step=1,
                            marks={i: str(i) for i in range(0, 60, 5)},
                            value=0,
                            updatemode="drag",
                        ),
                        html.Br(),
                        html.Button("Plot", id="refresh-button", n_clicks=0),
                        html.Button("Check for new installations", id="installation-check-button", n_clicks=0),
                    ],
                    id="buttons-section",
                    className="sidebar-content",
                ),
            ],
            className="four columns sidebar",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Pressure profile", id="graph-title"),
                    ],
                    className="text-box",
                ),
                dcc.Graph(id="pressure-profile-graph", style={"margin": "0px 20px", "height": "45vh"}),
            ],
            className="eight columns",
        ),
    ],
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
