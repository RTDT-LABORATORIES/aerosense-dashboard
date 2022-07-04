from dash import dcc


def Subtitle():
    return dcc.Markdown(
        """
        A dashboard for exploring the Aerosense data lake, comprising ["gretaDB" (a GCP BigQuery instance)](https://link.com) and acoustic datafile stores.

        This dashboard is read-only; you can upload and edit data using the lower-level [aerosense-tools](https://link.com) (for querying and interactive plot visualisation) and [data-gateway](https://link.com) (for data ingress and installation/configuration management.
        """,
        className="subtitle sidebar-content",
    )
