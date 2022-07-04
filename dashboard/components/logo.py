from dash import html


def Logo(src):
    return html.Div(
        [
            html.Img(
                src=src,
                className="plotly-logo",
            )
        ]
    )
