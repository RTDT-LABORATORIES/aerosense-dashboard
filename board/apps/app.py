import pandas as pd
import numpy as np
import panel as pn
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvas

from google.cloud import bigquery

bqclient = bigquery.Client()

# Download query results.
query_string_constats = """
SELECT datetime, filtered_rssi,	raw_rssi, tx_power, allocated_heap_memory, configuration_id, installation_reference
FROM `aerosense-twined.greta.connection_statistics`
LIMIT 10000
"""

# AND datetime > DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour HOUR)
# AND datetime < DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour+1 HOUR)
# AND IS_NAN(sensor_value[ORDINAL(1)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(2)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(3)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(4)]) IS FALSE

query_string_installations = """
SELECT reference, turbine_id, blade_id, hardware_version
FROM `aerosense-twined.greta.installation`
LIMIT 10000
"""


# =====================
# WITH PARAMETERS
# =====================
# from google.cloud import bigquery
# client = bigquery.Client()
# sql = """
#     SELECT name
#     FROM `bigquery-public-data.usa_names.usa_1910_current`
#     WHERE state = @state
#     LIMIT @limit
# """
# query_config = bigquery.QueryJobConfig(
#     query_parameters=[
#         bigquery.ScalarQueryParameter('state', 'STRING', 'TX'),
#         bigquery.ScalarQueryParameter('limit', 'INTEGER', 100)
#     ]
# )
# df = client.query(sql, job_config=query_config).to_dataframe()


constats = bqclient.query(query_string_constats).result().to_dataframe()
print(constats.head())

installations = bqclient.query(query_string_installations).result().to_dataframe()
print(installations.head())


import plotly.express as px
import plotly.graph_objs as go


pn.extension("plotly")

installations_df_widget = pn.widgets.DataFrame(installations, name="Installations", autosize_mode="fit_columns")


xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-((x - 1) ** 2) - y**2) - (x**3 + y**4 - x / 5) * np.exp(-(x**2 + y**2))

surface = go.Surface(z=z)
layout = go.Layout(title="Plotly 3D Plot", autosize=False, width=500, height=500, margin=dict(t=50, b=50, r=50, l=50))
fig = dict(data=[go.Scatter(x=constats.datetime, y=constats.tx_power, marker_color="indianred")], layout=layout)


data = pd.read_csv("https://raw.githubusercontent.com/holoviz/panel/master/examples/assets/occupancy.csv")
data["date"] = data.date.astype("datetime64[ns]")
data = data.set_index("date")

data.tail()


def mpl_plot(avg, highlight):
    fig = Figure()
    FigureCanvas(fig)  # not needed in mpl >= 3.1
    ax = fig.add_subplot()
    avg.plot(ax=ax)
    if len(highlight):
        highlight.plot(style="o", ax=ax)
    return fig


def find_outliers(variable="Temperature", window=30, sigma=10, view_fn=mpl_plot):
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return view_fn(avg, avg[outliers])


find_outliers(variable="Temperature", window=20, sigma=10)

from .constats import app as constats_app


def markdown_app():
    return "# This is a Panel app"


def plotly_app():
    return pn.pane.Plotly(fig)


def constats_app():
    return constats_app


# def json_app():
# return pn.pane.JSON({"abc": 12354})


def interact_app():
    return pn.interact(find_outliers)


pn.serve(
    {"markdown": markdown_app, "plotly": plotly_app, "json": json_app, "interact": interact_app},
    port=5000,
    autoreload=True,
    show=False,
)
