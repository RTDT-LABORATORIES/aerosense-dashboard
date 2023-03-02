from dash import dcc, html


def Nav(selected_tab="information_sensors"):
    return html.Div(
        dcc.Tabs(
            id="nav-tabs",
            value=selected_tab,
            children=[
                dcc.Tab(label="Information sensors", value="information_sensors"),
                dcc.Tab(label="Sensors", value="sensors"),
                dcc.Tab(label="Pressure profile", value="pressure_profile"),
            ],
            persistence=True,
        ),
        className="sidebar-content",
    )


"""
WHAT YURIY WANTS
He wants with priority
- a dropdown of installations
- dropdown list of sensors available for a given installation
- a button that says "plot last minute of data" (or live view)
The rest
- aerofoil plot component
"""
