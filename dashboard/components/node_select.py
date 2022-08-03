from dash import dcc


def NodeSelect():
    return dcc.Dropdown(
        options=["0"],
        id="node-select",
        value="0",
        persistence=True,
    )
