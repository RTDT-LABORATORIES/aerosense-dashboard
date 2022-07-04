from dash import dcc, html


def LearnMore():
    return html.Div(
        [
            html.A(
                html.Button("Learn More", className="learn-more-button"),
                href="https://plot.ly/dash/pricing/",
                target="_blank",
            )
        ],
        className="info-button",
    )


def StepSlider():
    return html.Div(
        [
            dcc.Slider(
                min=0,
                max=5,
                value=0,
                marks={i: f"{i+1}" for i in range(6)},
                id="slider",
            ),
        ],
        className="timeline-slider",
    )


def StepButtons():
    return html.Div(
        [
            html.Button(
                "Back",
                id="back",
                style={"display": "inline-block"},
                n_clicks=0,
            ),
            html.Button(
                "Next",
                id="next",
                style={"display": "inline-block", "marginLeft": "10px"},
                n_clicks=0,
            ),
        ],
        className="page-buttons",
    )
