import pathlib
import pandas as pd


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.resolve()


df = pd.read_csv(DATA_PATH.joinpath("yield_curve.csv"))

xlist = list(df["x"].dropna())
ylist = list(df["y"].dropna())

del df["x"]
del df["y"]

zlist = []
for row in df.iterrows():
    index, data = row
    zlist.append(data.tolist())

UPS = {
    0: dict(x=0, y=0, z=1),
    1: dict(x=0, y=0, z=1),
    2: dict(x=0, y=0, z=1),
    3: dict(x=0, y=0, z=1),
    4: dict(x=0, y=0, z=1),
    5: dict(x=0, y=0, z=1),
}

CENTERS = {
    0: dict(x=0.3, y=0.8, z=-0.5),
    1: dict(x=0, y=0, z=-0.37),
    2: dict(x=0, y=1.1, z=-1.3),
    3: dict(x=0, y=-0.7, z=0),
    4: dict(x=0, y=-0.2, z=0),
    5: dict(x=-0.11, y=-0.5, z=0),
}

EYES = {
    0: dict(x=2.7, y=2.7, z=0.3),
    1: dict(x=0.01, y=3.8, z=-0.37),
    2: dict(x=1.3, y=3, z=0),
    3: dict(x=2.6, y=-1.6, z=0),
    4: dict(x=3, y=-0.2, z=0),
    5: dict(x=-0.1, y=-0.5, z=2.66),
}

TEXTS = {
    0: """
    ##### Yield curve 101
    The yield curve shows how much it costs the federal government to borrow
    money for a given amount of time, revealing the relationship between long-
    and short-term interest rates.

    It is, inherently, a forecast for what the economy holds in the future —
    how much inflation there will be, for example, and how healthy growth will
    be over the years ahead — all embodied in the price of money today,
    tomorrow and many years from now.
    """.replace(
        "  ", ""
    ),
    1: """
    ##### Where we stand
    On Wednesday, both short-term and long-term rates were lower than they have
    been for most of history – a reflection of the continuing hangover
    from the financial crisis.

    The yield curve is fairly flat, which is a sign that investors expect
    mediocre growth in the years ahead.
    """.replace(
        "  ", ""
    ),
    2: """
    ##### Deep in the valley
    In response to the last recession, the Federal Reserve has kept short-term
    rates very low — near zero — since 2008. (Lower interest rates stimulate
    the economy, by making it cheaper for people to borrow money, but also
    spark inflation.)

    Now, the Fed is getting ready to raise rates again, possibly as early as
    June.
    """.replace(
        "  ", ""
    ),
    3: """
    ##### Last time, a puzzle
    The last time the Fed started raising rates was in 2004. From 2004 to 2006,
    short-term rates rose steadily.

    But long-term rates didn't rise very much.

    The Federal Reserve chairman called this phenomenon a “conundrum," and it
    raised questions about the ability of the Fed to guide the economy.
    Part of the reason long-term rates failed to rise was because of strong
    foreign demand.
    """.replace(
        "  ", ""
    ),
    4: """
    ##### Long-term rates are low now, too
    Foreign buyers have helped keep long-term rates low recently, too — as have
    new rules encouraging banks to hold government debt and expectations that
    economic growth could be weak for a long time.

    The 10-year Treasury yield was as low as it has ever been in July 2012 and
    has risen only modestly since.
    Some economists refer to the economic pessimism as “the new normal.”
    """.replace(
        "  ", ""
    ),
    5: """
    ##### Long-term rates are low now, too
    Here is the same chart viewed from above.
    """.replace(
        "  ", ""
    ),
}

ANNOTATIONS = {
    0: [],
    1: [
        dict(
            showarrow=False,
            x="1-month",
            y="2015-03-18",
            z=0.046,
            text="Short-term rates basically <br>follow the interest rates set <br>by the Federal Reserve.",
            xref="x",
            yref="y",
            zref="z",
            xanchor="left",
            yanchor="auto",
        )
    ],
    2: [],
    3: [],
    4: [],
    5: [],
}
