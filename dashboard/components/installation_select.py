from dash import dcc

from dashboard.queries import BigQuery


def InstallationSelect(current_installation_reference=None):
    installations = BigQuery().get_installations().to_dict(orient="records")

    options = [
        {"label": f"{row['reference']} (Turbine {row['turbine_id']})", "value": row["reference"]}
        for row in installations
    ]

    return dcc.Dropdown(
        options=options,
        id="installation_select",
        value=current_installation_reference or installations[0]["reference"],
        className="sidebar-content",
    )
