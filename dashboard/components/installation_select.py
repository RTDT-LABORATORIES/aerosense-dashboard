from dash import dcc

from aerosense_tools.queries import BigQuery


def InstallationSelect(current_installation_reference=None):
    installations = BigQuery().get_installations()

    return dcc.Dropdown(
        options=installations,
        id="installation-select",
        value=current_installation_reference or installations[0]["value"],
    )
