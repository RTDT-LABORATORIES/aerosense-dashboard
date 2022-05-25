import pandas as pd
import numpy as np
import panel as pn

import plotly.express as px
import plotly.graph_objs as go
from board.queries import get_installations, get_connection_statistics_agg
from board.widgets import date_range_picker

installations = get_installations()

installation_selector = pn.widgets.Select(options=list(installations["reference"]))
installation_selector.param.watch(print, "value")
print(installation_selector.value)
constats = get_connection_statistics_agg(installation_selector.value, date_range_picker.value[0])


constats_df_widget = pn.widgets.Tabulator(
    constats,
    show_index=False,
    name="Constats",
    theme="materialize",
    layout="fit_data_fill",
    disabled=True,  # prevents edit
)

app = pn.template.MaterialTemplate(title="Connection Statistics", header_background="#0d8679")

app.sidebar.append(
    pn.pane.Markdown(
        "## Installation\nSelect an installation to show its connection statistics...",
        sizing_mode="stretch_width",
    )
)
app.sidebar.append(
    installation_selector,
)
app.sidebar.append(
    pn.pane.Markdown(
        "## Filters\nRefine the date range...",
        sizing_mode="stretch_width",
    )
)
app.sidebar.append(
    date_range_picker,
)

app.main.append(pn.layout.flex.FlexBox(constats_df_widget, justify_content="center"))
