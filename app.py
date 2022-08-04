import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from flask_caching import Cache

from dashboard.components import About, InstallationSelect, Logo, Nav, Title
from dashboard.components.node_select import NodeSelect
from dashboard.components.sensor_select import SensorSelect
from dashboard.components.time_range_select import TimeRangeSelect
from dashboard.components.y_axis_select import YAxisSelect
from dashboard.graphs import plot_connections_statistics, plot_sensors
from dashboard.queries import BigQuery


CACHE_TIMEOUT = 3600


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Aerosense Dashboard"

cache = Cache(app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".dashboard_cache"})
app.config.suppress_callback_exceptions = True


graph_section = html.Div(
    [
        html.Div([html.H3(id="graph-title")], className="text-box"),
        dcc.Graph(id="graph", style={"margin": "0px 20px", "height": "45vh"}),
    ],
    className="eight columns",
)

common_page = [
    dcc.Store(id="click-output"),
    html.Div(
        [
            html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
            Nav(selected_tab="connection_statistics"),
            html.Label("Installation reference", className="sidebar-content"),
            InstallationSelect(),
            html.Div(id="buttons-section", className="sidebar-content"),
        ],
        className="four columns sidebar",
    ),
    graph_section,
]

buttons_sections = {
    "connection_statistics": [
        html.Label("Node id"),
        NodeSelect(),
        html.Label("y-axis to plot"),
        YAxisSelect(),
        html.Label("Time range"),
        TimeRangeSelect(),
        html.Br(),
        html.Button("Plot", id="refresh-button", n_clicks=0),
        html.Button("Check for new installations", id="installation-check-button", n_clicks=0),
    ],
    "sensors": [
        html.Label("Node id"),
        NodeSelect(),
        html.Label("Sensor"),
        SensorSelect(),
        html.Label("Time range"),
        TimeRangeSelect(),
        html.Br(),
        html.Button("Plot", id="refresh-button", n_clicks=0),
        html.Button("Check for new installations", id="installation-check-button", n_clicks=0),
    ],
}


app.layout = html.Div(
    common_page,
    className="row flex-display",
    style={"height": "100vh"},
)


@app.callback(
    Output("graph", "figure"),
    State("nav-tabs", "value"),
    State("installation-select", "value"),
    State("node-select", "value"),
    State("y-axis-select", "value"),
    State("time-range-select", "value"),
    Input("refresh-button", "n_clicks"),
)
@cache.memoize(timeout=CACHE_TIMEOUT, args_to_ignore=["refresh"])
def plot_graph(page_name, installation_reference, node_id, y_axis_column, time_range, refresh):
    """Plot a graph of the connection statistics for the given installation, y-axis column, and time range when these
    values are changed or the refresh button is clicked.

    :param str page_name:
    :param str installation_reference:
    :param str y_axis_column:
    :param str time_range:
    :param int refresh:
    :return plotly.graph_objs.Figure:
    """
    if not node_id:
        node_id = None

    if page_name == "connection_statistics":
        return plot_connections_statistics(installation_reference, node_id, y_axis_column, time_range)
    else:
        return plot_sensors(installation_reference, node_id, y_axis_column, time_range)


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
    return " ".join(selected_y_axis.split("_")).capitalize()


@app.callback(
    Output("buttons-section", "children"),
    Input("nav-tabs", "value"),
)
def change_buttons_section(section_name):
    """Change the buttons shown on the dashboard when a navigation tab is clicked.

    :param str section_name:
    :return list:
    """
    return buttons_sections[section_name]


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
