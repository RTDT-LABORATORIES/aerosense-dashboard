from dash import dcc

from dashboard.queries import BigQuery


def InstallationSelect():
    installations = BigQuery().get_installations().to_dict(orient="records")

    options = [
        {"label": f"{row['reference']} (Turbine {row['turbine_id']})", "value": row["reference"]}
        for row in installations
    ]

    return dcc.Dropdown(
        options=options,
        id="installation_select",
        value=installations[0]["reference"],
        className="sidebar-content",
    )
