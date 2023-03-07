from dash import dcc, html

from dashboard.components import About, InstallationSelect, Logo, Navigation, Title
from dashboard.components.node_select import NodeSelect
from dashboard.components.sensor_select import SensorSelect
from dashboard.components.time_range_select import TimeRangeSelect


def create_sensors_tab_layout(app, tab_name, sensor_names, graph_id, data_limit_warning_id):
    """Create the layout corresponding to a sensors tab.

    :param dash.Dash app:
    :param str tab_name:
    :param iter(str) sensor_names:
    :param str graph_id:
    :param str data_limit_warning_id:
    :return list:
    """
    return [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Navigation(selected_tab=tab_name),
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
                        SensorSelect(sensor_names),
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
                        dcc.Markdown(id=data_limit_warning_id, className="warning"),
                    ],
                    className="text-box",
                ),
                dcc.Graph(id=graph_id, style={"margin": "0px 20px", "height": "45vh"}),
            ],
            className="eight columns",
        ),
    ]
