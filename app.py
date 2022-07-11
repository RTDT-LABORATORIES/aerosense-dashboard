import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from dashboard.components import About, InstallationSelect, Logo, Nav, Title
from dashboard.components.time_range_select import TimeRangeSelect
from dashboard.components.y_axis_select import YAxisSelect
from dashboard.graphs import plot_connections_statistics, plot_sensors


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Aerosense Dashboard"
server = app.server


graph_section = html.Div(
    [
        html.Div([dcc.Markdown(id="text")], className="text-box"),
        dcc.Graph(id="graph", style={"margin": "0px 20px", "height": "45vh"}),
    ],
    id="page",
    className="eight columns",
)

connection_stats_page = [
    dcc.Store(id="click-output"),
    html.Div(
        [
            html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
            Nav(selected_tab="connection_statistics"),
            html.Label("Installation reference"),
            html.Div([InstallationSelect()], id="installation-selection-section"),
            html.Label("Y-axis to plot"),
            YAxisSelect(),
            html.Label("Time range"),
            TimeRangeSelect(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Button("Get latest data", id="refresh-button", n_clicks=0),
        ],
        className="four columns sidebar",
    ),
    graph_section,
]

sensors_page = [
    dcc.Store(id="click-output"),
    html.Div(
        [
            html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
            Nav(selected_tab="sensors"),
            html.Label("Installation reference"),
            html.Div([InstallationSelect()], id="installation-selection-section"),
            html.Label("Node id"),
            dcc.Textarea(id="node-select", value="0"),
            html.Label("Y-axis to plot"),
            YAxisSelect(),
            html.Label("Time range"),
            TimeRangeSelect(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Button("Get latest data", id="refresh-button", n_clicks=0),
        ],
        className="four columns sidebar",
    ),
    graph_section,
]


app.layout = html.Div(
    connection_stats_page,
    id="main-page",
    className="row flex-display",
    style={"height": "100vh"},
)


@app.callback(
    Output("graph", "figure"),
    Input("nav-tabs", "value"),
    Input("installation_select", "value"),
    Input("node-select", "value"),
    Input("y_axis_select", "value"),
    Input("time_range_select", "value"),
    Input("refresh-button", "n_clicks"),
)
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
    if page_name == "connection_statistics":
        return plot_connections_statistics(installation_reference, y_axis_column, time_range)
    else:
        return plot_sensors(installation_reference, node_id, y_axis_column, time_range)


@app.callback(
    Output("installation-selection-section", "children"),
    Input("refresh-button", "n_clicks"),
)
def update_installation_selector(refresh):
    """Update the installation selector with any new installations when the refresh button is clicked.

    :param int refresh:
    :return list:
    """
    return [InstallationSelect()]


@app.callback(
    Output("main-page", "children"),
    Input("nav-tabs", "value"),
)
def change_page(page_name):
    """Change the page shown on the dashboard when a navigation tab is clicked.

    :param str page_name:
    :return list:
    """
    pages = {"sensors": sensors_page, "connection_statistics": connection_stats_page}
    return pages[page_name]


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
