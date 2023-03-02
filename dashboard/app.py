import datetime as dt
import logging
import sys

import dash
import dash_daq as daq
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask_caching import Cache

from aerosense_tools.plots import plot_connection_statistic, plot_pressure_bar_chart, plot_sensors
from aerosense_tools.queries import ROW_LIMIT, BigQuery
from aerosense_tools.utils import generate_time_range, get_cleaned_sensor_column_names
from dashboard.components import About, InstallationSelect, Logo, Nav, Title
from dashboard.components.node_select import NodeSelect
from dashboard.components.sensor_select import SensorSelect
from dashboard.components.time_range_select import TimeRangeSelect
from dashboard.components.y_axis_select import YAxisSelect


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = dash.Dash(
    name=__name__,
    assets_folder="../assets",
    title="Aerosense Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.config.suppress_callback_exceptions = True

CACHE_TIMEOUT = 3600
cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".dashboard_cache"})

tabs = {
    "connection_statistics": [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Nav(selected_tab="connection_statistics"),
                html.Br(),
                html.Div(
                    [
                        html.Label(html.B("Installation")),
                        html.Label("Installation reference"),
                        InstallationSelect(),
                        html.Label("Node id"),
                        NodeSelect(),
                        html.Br(),
                        html.Label(html.B("Graph")),
                        html.Label("Connection statistic"),
                        YAxisSelect(),
                        html.Label("Time range"),
                        TimeRangeSelect(),
                        html.Label("Custom date"),
                        dcc.DatePickerRange(
                            id="custom-time-range-select",
                            display_format="Do MMM Y",
                            persistence=True,
                            disabled=True,
                        ),
                        html.Br(),
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
                html.Br(),
                html.Div(
                    [
                        html.Label(html.B("Installation")),
                        html.Label("Installation reference"),
                        InstallationSelect(),
                        html.Label("Node id"),
                        NodeSelect(),
                        html.Br(),
                        html.Label(html.B("Graph")),
                        html.Label("Sensor"),
                        SensorSelect(),
                        html.Label("Time range"),
                        TimeRangeSelect(),
                        html.Label("Custom date"),
                        dcc.DatePickerRange(
                            id="custom-time-range-select",
                            display_format="Do MMM Y",
                            persistence=True,
                            disabled=True,
                        ),
                        html.Br(),
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
    [html.Div(tabs["connection_statistics"], id="app")],
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
    :param datetime.date|None custom_start_date:
    :param datetime.date|None custom_end_date:
    :param int refresh:
    :return plotly.graph_objs.Figure:
    """
    if not node_id:
        node_id = None

    start, finish = generate_time_range(time_range, custom_start_date, custom_end_date)

    df = BigQuery().get_aggregated_connection_statistics(
        installation_reference=installation_reference,
        node_id=node_id,
        start=start,
        finish=finish,
    )

    return plot_connection_statistic(df, y_axis_column)


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
    sensor_name,
    time_range,
    custom_start_date,
    custom_end_date,
    refresh,
):
    """Plot a graph of the sensor data for the given installation, y-axis column, and time range when these values are
    changed or the refresh button is clicked.

    :param str installation_reference:
    :param str sensor_name:
    :param str time_range:
    :param datetime.date|None custom_start_date:
    :param datetime.date|None custom_end_date:
    :param int refresh:
    :return (plotly.graph_objs.Figure, str):
    """
    if not node_id:
        node_id = None

    start, finish = generate_time_range(time_range, custom_start_date, custom_end_date)

    df, data_limit_applied = BigQuery().get_sensor_data(
        installation_reference,
        node_id,
        sensor_name,
        start=start,
        finish=finish,
    )

    figure = plot_sensors(df)

    if data_limit_applied:
        return (figure, f"Large amount of data - the query has been limited to the latest {ROW_LIMIT} datapoints.")

    return (figure, "")


@cache.memoize(timeout=0)
def get_pressure_profiles_for_time_window(installation_reference, node_id, start_datetime, finish_datetime):
    """Get pressure profiles for the given node during the given time window along with the minimum and maximum
    pressures over all the sensors over that window.

    :param str installation_reference:
    :param str node_id:
    :param datetime.datetime start_datetime:
    :param datetime.datetime finish_datetime:
    :return (pandas.DataFrame, float, float): the pressure profiles, minimum pressure, and maximum pressure for the time window
    """
    df, _ = BigQuery().get_sensor_data(
        installation_reference=installation_reference,
        node_id=node_id,
        sensor_type_reference="barometer",
        start=start_datetime,
        finish=finish_datetime,
    )

    logger.info(
        "Downloaded pressure profile %d second time window for start datetime %r and finish datetime %r.",
        (finish_datetime - start_datetime).seconds,
        start_datetime.isoformat(),
        finish_datetime.isoformat(),
    )

    sensor_column_names, _ = get_cleaned_sensor_column_names(df)
    df_with_sensors_only = df[sensor_column_names]
    return (df, df_with_sensors_only.min().min(), df_with_sensors_only.max().max())


@app.callback(
    Output("pressure-profile-graph", "figure"),
    State("installation-select", "value"),
    State("node-select", "value"),
    State("date-select", "date"),
    State("hour", "value"),
    State("minute", "value"),
    State("second", "value"),
    Input("time-slider", "value"),
    Input("refresh-button", "n_clicks"),
)
def plot_pressure_profile_graph(installation_reference, node_id, date, hour, minute, second, time_delta, refresh):
    if not node_id:
        node_id = None

    initial_datetime = dt.datetime.combine(date=dt.date.fromisoformat(date), time=dt.time(hour, minute, second))

    df, minimum, maximum = get_pressure_profiles_for_time_window(
        installation_reference=installation_reference,
        node_id=node_id,
        start_datetime=initial_datetime,
        finish_datetime=initial_datetime + dt.timedelta(seconds=60),
    )

    slider_datetime = initial_datetime + dt.timedelta(seconds=time_delta)

    df = df[
        (df["datetime"] >= slider_datetime - dt.timedelta(seconds=0.5))
        & (df["datetime"] < slider_datetime + dt.timedelta(seconds=0.5))
    ]

    logger.debug("Filtered pressure profile time window for single datetime.")
    return plot_pressure_bar_chart(df, minimum, maximum)


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
