import panel as pn
from board.apps.installations import app as installations_app
from board.apps.constats import app as constats_app


pn.extension("plotly")

pn.serve(
    {"installations": installations_app, "connection_statistics": constats_app},
    port=5000,
    autoreload=True,
    show=False,
)
