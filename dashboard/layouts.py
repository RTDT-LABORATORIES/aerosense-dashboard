import datetime

import dash_daq
from dash import dcc, html

from dashboard.components import About, InstallationSelect, Logo, Navigation, Title
from dashboard.components.node_select import NodeSelect
from dashboard.components.sensor_coordinates_select import SensorCoordinatesSelect
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
                        html.Label("Node ID"),
                        NodeSelect(),
                        html.Br(),
                        html.Label(html.B("Sensor")),
                        SensorSelect(sensor_names),
                        html.Br(),
                        html.Label(html.B("Time range")),
                        TimeRangeSelect(),
                        html.Br(),
                        html.Label(html.B("Measurement sessions")),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Start datetime"),
                                        dcc.DatePickerSingle(
                                            id="start-date",
                                            date=datetime.datetime.now().date().isoformat(),
                                            display_format="Do MMM Y",
                                            persistence=True,
                                            disabled=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Hour"),
                                        dash_daq.NumericInput(
                                            id="start-hour", value=0, min=0, max=23, persistence=True
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Minute"),
                                        dash_daq.NumericInput(
                                            id="start-minute", value=0, min=0, max=59, persistence=True
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Second"),
                                        dash_daq.NumericInput(
                                            id="start-second", value=0, min=0, max=59, persistence=True
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                            ],
                            style={"margin": "10px 0"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("End datetime"),
                                        dcc.DatePickerSingle(
                                            id="end-date",
                                            display_format="Do MMM Y",
                                            persistence=True,
                                            disabled=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Hour"),
                                        dash_daq.NumericInput(id="end-hour", value=0, min=0, max=23, persistence=True),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Minute"),
                                        dash_daq.NumericInput(
                                            id="end-minute", value=0, min=0, max=59, persistence=True
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Second"),
                                        dash_daq.NumericInput(
                                            id="end-second", value=0, min=0, max=59, persistence=True
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                            ],
                            style={"margin": "10px 0"},
                        ),
                        html.Button("Get measurement sessions", id="measurement-session-check-button", n_clicks=0),
                        html.Br(),
                        html.Br(),
                        html.Label("Measurement session"),
                        dcc.Dropdown(id="measurement-session-select", persistence=True),
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
                dcc.Loading(
                    [
                        dcc.Graph(id=graph_id, style={"margin": "0px 20px", "height": "45vh"}),
                    ],
                ),
            ],
            className="eight columns",
        ),
    ]


def create_cp_plot_tab_layout(app):
    """Create the layout corresponding to the Cp plot tab.

    :param dash.Dash app:
    :return list:
    """
    return [
        html.Div(
            [
                html.Div([Logo(app.get_asset_url("logo.png")), Title(), About()]),
                Navigation(selected_tab="cp_plot"),
                html.Br(),
                html.Div(
                    [
                        html.Label(html.B("Installation")),
                        html.Label("Installation reference"),
                        InstallationSelect(),
                        html.Label("Node ID"),
                        NodeSelect(),
                        html.Label("Sensor coordinates reference"),
                        SensorCoordinatesSelect(),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Air density"),
                                        dash_daq.NumericInput(
                                            id="air-density-input",
                                            value=1.225,
                                            min=0,
                                            max=1e9,
                                            size=120,
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("u"),
                                        dash_daq.NumericInput(
                                            id="u-input",
                                            value=10,
                                            min=0,
                                            max=1e9,
                                            size=120,
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("p_inf"),
                                        dash_daq.NumericInput(
                                            id="p-inf-input",
                                            value=1e5,
                                            min=0,
                                            max=1e12,
                                            size=120,
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Cp minimum"),
                                        dash_daq.NumericInput(
                                            id="cp-minimum-input",
                                            value=-10,
                                            min=-1000,
                                            max=1000,
                                            size=120,
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Cp maximum"),
                                        dash_daq.NumericInput(
                                            id="cp-maximum-input",
                                            value=3,
                                            min=-1000,
                                            max=1000,
                                            size=120,
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                            ],
                            style={"margin": "10px 0"},
                        ),
                        html.Br(),
                        html.Label(html.B("Start date/time")),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Date"),
                                        dcc.DatePickerSingle(
                                            id="date-select",
                                            date=datetime.datetime.now().date().isoformat(),
                                            display_format="Do MMM Y",
                                            persistence=True,
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Hour"),
                                        dash_daq.NumericInput(id="hour", value=0, min=0, max=23, persistence=True),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Minute"),
                                        dash_daq.NumericInput(id="minute", value=0, min=0, max=59, persistence=True),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Second"),
                                        dash_daq.NumericInput(id="second", value=0, min=0, max=59, persistence=True),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                            ],
                            style={"margin": "10px 0"},
                        ),
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
                        html.Button(
                            "Check for new sensor coordinates",
                            id="sensor-coordinates-check-button",
                            n_clicks=0,
                        ),
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
                        html.H3("Cp plot", id="graph-title"),
                    ],
                    className="text-box",
                ),
                dcc.Loading(
                    [
                        dcc.Graph(id="pressure-profile-graph", style={"margin": "0px 20px", "height": "45vh"}),
                    ],
                ),
            ],
            className="eight columns",
        ),
    ]
