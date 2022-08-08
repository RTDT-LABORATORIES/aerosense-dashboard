import datetime as dt

import dash
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask_caching import Cache

from dashboard.components import About, InstallationSelect, Logo, Nav, Title
from dashboard.components.node_select import NodeSelect
from dashboard.components.sensor_select import SensorSelect
from dashboard.components.time_range_select import TimeRangeSelect
from dashboard.components.y_axis_select import YAxisSelect
from dashboard.graphs import plot_connections_statistics, plot_pressure_bar_chart, plot_sensors
from dashboard.queries import ROW_LIMIT, BigQuery


CACHE_TIMEOUT = 3600


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Aerosense Dashboard"

cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".dashboard_cache"})
app.config.suppress_callback_exceptions = True


tabs = {
    "connection_statistics": [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Nav(selected_tab="connection_statistics"),
                html.Label("Installation reference", className="sidebar-content"),
                InstallationSelect(),
                html.Div(
                    [
                        html.Label("Node id"),
                        NodeSelect(),
                        html.Label("Connection statistic"),
                        YAxisSelect(),
                        html.Label("Time range"),
                        TimeRangeSelect(),
                        dcc.DatePickerRange(
                            id="custom-time-range-select",
                            display_format="Do MMM Y",
                            persistence=True,
                            disabled=True,
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
                        html.H3(id="graph-title"),
                    ],
                    className="text-box",
                ),
                dcc.Graph(id="connection-statistics-graph", style={"margin": "0px 20px", "height": "45vh"}),
            ],
            className="eight columns",
        ),
    ],
    "sensors": [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Nav(selected_tab="sensors"),
                html.Label("Installation reference", className="sidebar-content"),
                InstallationSelect(),
                html.Div(
                    [
                        html.Label("Node id"),
                        NodeSelect(),
                        html.Label("Sensor"),
                        SensorSelect(),
                        html.Label("Time range"),
                        TimeRangeSelect(),
                        dcc.DatePickerRange(
                            id="custom-time-range-select",
                            display_format="Do MMM Y",
                            persistence=True,
                            disabled=True,
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
                        html.H3(id="graph-title"),
                        dcc.Markdown(id="data-limit-warning", className="warning"),
                    ],
                    className="text-box",
                ),
                dcc.Graph(id="sensors-graph", style={"margin": "0px 20px", "height": "45vh"}),
            ],
            className="eight columns",
        ),
    ],
    "pressure_profile": [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Nav(selected_tab="pressure_profile"),
                html.Label("Installation reference", className="sidebar-content"),
                InstallationSelect(),
                html.Div(
                    [
                        html.Label("Node id"),
                        NodeSelect(),
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
                        html.H3(id="graph-title"),
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
    [
        dcc.Store(id="click-output"),
        html.Div(
            tabs["connection_statistics"],
            id="app",
        ),
    ],
    className="row flex-display",
    style={"height": "100vh"},
)


@app.callback(
    Output("connection-statistics-graph", "figure"),
    State("installation-select", "value"),
    State("node-select", "value"),
    State("y-axis-select", "value"),
    State("time-range-select", "value"),
    State("custom-time-range-select", "start_date"),
    State("custom-time-range-select", "end_date"),
    Input("refresh-button", "n_clicks"),
)
@cache.memoize(timeout=CACHE_TIMEOUT, args_to_ignore=["refresh"])
def plot_connection_statistics_graph(
    installation_reference,
    node_id,
    y_axis_column,
    time_range,
    custom_start_date,
    custom_end_date,
    refresh,
):
    """Plot a graph of the connection statistics for the given installation, y-axis column, and time range when these
    values are changed or the refresh button is clicked.

    :param str installation_reference:
    :param str y_axis_column:
    :param str time_range:
    :param int refresh:
    :return plotly.graph_objs.Figure:
    """
    if not node_id:
        node_id = None

    return plot_connections_statistics(
        installation_reference,
        node_id,
        y_axis_column,
        time_range,
        custom_start_date,
        custom_end_date,
    )


@app.callback(
    Output("sensors-graph", "figure"),
    Output("data-limit-warning", "children"),
    State("installation-select", "value"),
    State("node-select", "value"),
    State("y-axis-select", "value"),
    State("time-range-select", "value"),
    State("custom-time-range-select", "start_date"),
    State("custom-time-range-select", "end_date"),
    Input("refresh-button", "n_clicks"),
)
@cache.memoize(timeout=CACHE_TIMEOUT, args_to_ignore=["refresh"])
def plot_sensors_graph(
    installation_reference,
    node_id,
    y_axis_column,
    time_range,
    custom_start_date,
    custom_end_date,
    refresh,
):
    """Plot a graph of the sensor data for the given installation, y-axis column, and time range when these values are
    changed or the refresh button is clicked.

    :param str installation_reference:
    :param str y_axis_column:
    :param str time_range:
    :param int refresh:
    :return plotly.graph_objs.Figure:
    """
    if not node_id:
        node_id = None

    figure, data_limit_applied = plot_sensors(
        installation_reference,
        node_id,
        y_axis_column,
        time_range,
        custom_start_date,
        custom_end_date,
    )

    if data_limit_applied:
        return (figure, f"Large amount of data - the query has been limited to the latest {ROW_LIMIT} datapoints.")

    return (figure, "")


@app.callback(
    Output("pressure-profile-graph", "figure"),
    Input("installation-select", "value"),
    Input("node-select", "value"),
    Input("date-select", "date"),
    Input("hour", "value"),
    Input("minute", "value"),
    Input("second", "value"),
)
# @cache.memoize(timeout=CACHE_TIMEOUT)
def plot_pressure_profile_graph(installation_reference, node_id, date, hour, minute, second):
    if not node_id:
        node_id = None

    datetime = dt.datetime.combine(date=dt.date.fromisoformat(date), time=dt.time(hour, minute, second))

    return plot_pressure_bar_chart(installation_reference=installation_reference, node_id=node_id, datetime=datetime)


@app.callback(
    Output("installation-select", "options"),
    Input("installation-check-button", "n_clicks"),
)
def update_installation_selector(refresh):
    """Update the installation selector with any new installations when the refresh button is clicked.

    :param int refresh:
    :return list:
    """
    return BigQuery().get_installations()


@app.callback(
    [
        Output("node-select", "options"),
        Output("node-select", "value"),
    ],
    [
        Input("installation-select", "value"),
    ],
)
@cache.memoize(timeout=CACHE_TIMEOUT)
def update_node_selector(installation_reference):
    """Update the node selector options with the IDs of the nodes available for the given installation.

    :param str installation_reference:
    :return list(str):
    """
    nodes = BigQuery().get_nodes(installation_reference)

    try:
        first_option = nodes[0]
    except IndexError:
        first_option = None

    return nodes, first_option


@app.callback(
    Output("graph-title", "children"),
    Input("y-axis-select", "value"),
)
def update_graph_title(selected_y_axis):
    """Update the graph title with the name of the currently selected y-axis.

    :param str selected_y_axis:
    :return str:
    """
    if not selected_y_axis:
        return ""

    return " ".join(selected_y_axis.split("_")).capitalize()


@app.callback(
    [
        Output("custom-time-range-select", "disabled"),
        Output("custom-time-range-select", "start_date"),
        Output("custom-time-range-select", "end_date"),
    ],
    [
        Input("time-range-select", "value"),
    ],
)
def enable_custom_time_range_select(time_range):
    """Enable the custom time range selection if "Custom" is chosen in the time range selector.

    :param str time_range:
    :return bool:
    """
    return (time_range != "Custom", None, None)


@app.callback(
    Output("app", "children"),
    Input("nav-tabs", "value"),
)
def change_tabs(section_name):
    """Change the buttons shown on the dashboard when a navigation tab is clicked.

    :param str section_name:
    :return list:
    """
    return tabs[section_name]


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
