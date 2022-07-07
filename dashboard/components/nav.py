from dash import dcc, html


def Nav(default_page="about"):
    return html.Div(
        dcc.Tabs(
            id="nav-tabs",
            value=default_page,
            children=[
                dcc.Tab(label="About", value="about"),
                dcc.Tab(label="Connection Stats", value="connection_statistics"),
                dcc.Tab(label="Sensors", value="sensors"),
            ],
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
