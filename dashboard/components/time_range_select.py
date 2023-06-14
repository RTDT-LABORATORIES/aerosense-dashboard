from dash import dcc

from dashboard.utils import TIME_RANGE_OPTIONS


def TimeRangeSelect():
    return dcc.Dropdown(
        options=list(TIME_RANGE_OPTIONS.keys()) + ["All time", "Measurement session"],
        id="time-range-select",
        value="Last day",
        persistence=True,
    )
