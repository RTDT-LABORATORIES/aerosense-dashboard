from dash import dcc


def YAxisSelect():
    return dcc.Dropdown(
        options=["filtered_rssi", "raw_rssi", "tx_power", "allocated_heap_memory"],
        id="y_axis_select",
        value="tx_power",
        persistence=True,
    )
