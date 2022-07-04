from dash import dcc


def TimeRangeSelect():
    options = ["Last hour", "Last day", "Last week", "Last month", "Last year", "All time"]

    return dcc.Dropdown(
        options=options,
        id="time_range_select",
        value="All time",
        className="sidebar-content",
    )
