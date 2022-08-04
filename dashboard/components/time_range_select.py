from dash import dcc


def TimeRangeSelect():
    return dcc.Dropdown(
        options=["Last minute", "Last hour", "Last day", "Last week", "Last month", "Last year", "All time", "Custom"],
        id="time-range-select",
        value="Last day",
        persistence=True,
    )
