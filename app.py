import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

from dashboard.components import InstallationSelect, Logo, Nav, Subtitle, Title
from example.callbacks import advance_slider, make_graph, make_text
from example.components import LearnMore, StepButtons, StepSlider


# NOTES FOR MARCUS

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Aerosense Dashboard"
server = app.server


app.layout = html.Div(
    [
        dcc.Store(id="click-output"),
        html.Div(
            [
                html.Div(
                    [
                        Logo(app.get_asset_url("logo.png")),
                        Title(),
                        Subtitle(),
                    ]
                ),
                Nav(),
                InstallationSelect(),
                LearnMore(),
                StepSlider(),
                StepButtons(),
            ],
            className="four columns sidebar",
        ),
        html.Div(
            [
                html.Div([dcc.Markdown(id="text")], className="text-box"),
                dcc.Graph(id="graph", style={"margin": "0px 20px", "height": "45vh"}),
            ],
            id="page",
            className="eight columns",
        ),
    ],
    className="row flex-display",
    style={"height": "100vh"},
)


@app.callback(Output("graph", "figure"), [Input("slider", "value")])
def make_graph_callback(value):
    return make_graph(value)


@app.callback(Output("text", "children"), [Input("slider", "value")])
def make_text_callback(value):
    return make_text(value)


@app.callback(
    [Output("slider", "value"), Output("click-output", "data")],
    [Input("back", "n_clicks"), Input("next", "n_clicks")],
    [State("slider", "value"), State("click-output", "data")],
)
def advance_slider_callback(back, nxt, slider, last_history):
    return advance_slider(back, nxt, slider, last_history)


@app.callback(Output("output", "children"), [Input("radios", "value")])
def display_value(value):
    return f"Selected value: {value}"


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
