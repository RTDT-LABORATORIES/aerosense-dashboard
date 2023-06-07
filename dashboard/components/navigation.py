from dash import dcc, html


def Navigation(selected_tab="information_sensors"):
    return html.Div(
        dcc.Tabs(
            id="nav-tabs",
            value=selected_tab,
            children=[
                dcc.Tab(label="Information sensors", value="information_sensors"),
                dcc.Tab(label="Sensors", value="sensors"),
                dcc.Tab(label="Cp plot", value="cp_plot"),
            ],
            persistence=True,
        ),
        className="sidebar-content",
    )
