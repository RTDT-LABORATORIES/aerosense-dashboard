from dash import dcc


def YAxisSelect():
    return dcc.Dropdown(
        options=["filtered_rssi", "raw_rssi", "tx_power", "allocated_heap_memory", "battery_info"],
        id="y-axis-select",
        value="tx_power",
        persistence=True,
    )
