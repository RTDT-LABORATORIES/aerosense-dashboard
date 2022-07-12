from dash import dcc

from dashboard.queries import BigQuery


def InstallationSelect(current_installation_reference=None):
    installations = BigQuery().get_installations()

    return dcc.Dropdown(
        options=installations,
        id="installation_select",
        value=current_installation_reference or installations[0]["value"],
        className="sidebar-content",
    )
