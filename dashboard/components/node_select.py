from dash import dcc


def NodeSelect():
    return dcc.Dropdown(
        options=["0"],
        id="node-select",
        persistence=True,
    )
