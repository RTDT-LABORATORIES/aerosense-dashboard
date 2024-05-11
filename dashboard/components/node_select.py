from dash import dcc


def NodeSelect():
    return dcc.Dropdown(
        options=["0", "1", "2", "3", "4", "5"],
        id="node-select",
        persistence=True,
    )
