import pandas as pd
import numpy as np
import panel as pn

import plotly.express as px
import plotly.graph_objs as go
from board.queries import get_installations


installations = get_installations()

installations_df_widget = pn.widgets.Tabulator(
    installations,
    show_index=False,
    header_filters={
        "reference": True,
        "turbine_id": True,
        "blade_id": True,
        "hardware_version": True,
    },
    name="Installations",
    theme="materialize",
    layout="fit_data_fill",
    disabled=True,  # prevents edit
)

app = pn.template.MaterialTemplate(title="Installations", header_background="#fe4536")

app.sidebar.append(
    pn.pane.Markdown(
        'An "installation" refers to the use of a particular hardware version on a particular turbine and blade. Each installation has its own gateway.\n\nYou can learn more in the [data-gateway docs](https://data-gateway.readthedocs.io).',
        sizing_mode="stretch_width",
    ),
)

app.main.append(pn.layout.flex.FlexBox(installations_df_widget, justify_content="center"))
