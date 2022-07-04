import numpy as np

from example.old import CENTERS, EYES, TEXTS, UPS, xlist, ylist, zlist


def make_graph(value):
    """Make 3d graph"""

    if value is None:
        value = 0

    if value in [0, 2, 3]:
        z_secondary_beginning = [z[1] for z in zlist if z[0] == "None"]
        z_secondary_end = [z[0] for z in zlist if z[0] != "None"]
        z_secondary = z_secondary_beginning + z_secondary_end
        x_secondary = ["3-month"] * len(z_secondary_beginning) + ["1-month"] * len(z_secondary_end)
        y_secondary = ylist
        opacity = 0.7

    elif value == 1:
        x_secondary = xlist
        y_secondary = [ylist[-1] for i in xlist]
        z_secondary = zlist[-1]
        opacity = 0.7

    elif value == 4:
        z_secondary = [z[8] for z in zlist]
        x_secondary = ["10-year" for i in z_secondary]
        y_secondary = ylist
        opacity = 0.25

    if value in range(0, 5):

        trace1 = dict(
            type="surface",
            x=xlist,
            y=ylist,
            z=zlist,
            hoverinfo="x+y+z",
            lighting={
                "ambient": 0.95,
                "diffuse": 0.99,
                "fresnel": 0.01,
                "roughness": 0.01,
                "specular": 0.01,
            },
            colorscale=[
                [0, "rgb(230,245,254)"],
                [0.4, "rgb(123,171,203)"],
                [0.8, "rgb(40,119,174)"],
                [1, "rgb(37,61,81)"],
            ],
            opacity=opacity,
            showscale=False,
            zmax=9.18,
            zmin=0,
            scene="scene",
        )

        trace2 = dict(
            type="scatter3d",
            mode="lines",
            x=x_secondary,
            y=y_secondary,
            z=z_secondary,
            hoverinfo="x+y+z",
            line=dict(color="#444444"),
        )

        data = [trace1, trace2]

    else:

        trace1 = dict(
            type="contour",
            x=ylist,
            y=xlist,
            z=np.array(zlist).T,
            colorscale=[
                [0, "rgb(230,245,254)"],
                [0.4, "rgb(123,171,203)"],
                [0.8, "rgb(40,119,174)"],
                [1, "rgb(37,61,81)"],
            ],
            showscale=False,
            zmax=9.18,
            zmin=0,
            line=dict(smoothing=1, color="rgba(40,40,40,0.15)"),
            contours=dict(coloring="heatmap"),
        )

        data = [trace1]

    layout = dict(
        autosize=True,
        font=dict(size=12, color="#CCCCCC"),
        margin=dict(t=5, l=5, b=5, r=5),
        showlegend=False,
        hovermode="closest",
        scene=dict(
            aspectmode="manual",
            aspectratio=dict(x=2, y=5, z=1.5),
            camera=dict(up=UPS[value], center=CENTERS[value], eye=EYES[value]),
            annotations=[
                dict(
                    showarrow=False,
                    y="2015-03-18",
                    x="1-month",
                    z=0.046,
                    text="Point 1",
                    xanchor="left",
                    xshift=10,
                    opacity=0.7,
                ),
                dict(
                    y="2015-03-18",
                    x="3-month",
                    z=0.048,
                    text="Point 2",
                    textangle=0,
                    ax=0,
                    ay=-75,
                    font=dict(color="black", size=12),
                    arrowcolor="black",
                    arrowsize=3,
                    arrowwidth=1,
                    arrowhead=1,
                ),
            ],
            xaxis={
                "showgrid": True,
                "title": "",
                "type": "category",
                "zeroline": False,
                "categoryorder": "array",
                "categoryarray": list(reversed(xlist)),
            },
            yaxis={"showgrid": True, "title": "", "type": "date", "zeroline": False},
        ),
    )

    figure = dict(data=data, layout=layout)
    return figure


def make_text(value):
    """Make annotations"""
    if value is None:
        value = 0

    return TEXTS[value]


def advance_slider(back, nxt, slider, last_history):
    """Button controls"""
    try:
        if back > last_history["back"]:
            last_history["back"] = back
            return max(0, slider - 1), last_history

        if nxt > last_history["next"]:
            last_history["next"] = nxt
            return min(5, slider + 1), last_history

    # if last_history store is None
    except Exception:
        last_history = {"back": 0, "next": 0}
        return slider, last_history
