from dash import dcc

from dashboard.utils import TIME_RANGE_OPTIONS


def TimeRangeSelect():
    return dcc.Dropdown(
        options=["All time", "Custom"] + list(TIME_RANGE_OPTIONS.keys()),
        id="time-range-select",
        value="Last day",
        persistence=True,
    )
