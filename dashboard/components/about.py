from dash import dcc


def About():
    return dcc.Markdown(
        """
        A dashboard for exploring the Aerosense data lake, comprising ["greta" (a GCP BigQuery instance)]
        (https://console.cloud.google.com/bigquery?project=aerosense-twined&ws=!1m4!1m3!3m2!1saerosense-twined!2sgreta)
        and acoustic datafile stores.

        This dashboard is read-only; you can upload and edit data using the lower-level
        [aerosense-tools](https://github.com/aerosense-ai/aerosense-tools) (for querying and interactive plot
        visualisation) and [data-gateway](https://github.com/aerosense-ai/data-gateway) (for data ingress and
        installation/configuration management.
        """,
        className="subtitle sidebar-content",
    )
