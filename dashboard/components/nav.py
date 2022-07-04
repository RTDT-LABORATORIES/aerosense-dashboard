from dash import dcc, html


def Nav():
    return html.Div(
        dcc.Tabs(
            id="nav-tabs",
            value="constats",
            children=[
                dcc.Tab(label="About", value="about"),
                dcc.Tab(label="Connection Stats", value="constats"),
                dcc.Tab(label="Pressures", value="pressures"),
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
