from dash import dcc


def About():
    return dcc.Markdown(
        """
        This dashboard is read-only; you can upload and edit data using the lower-level [aerosense-tools](https://link.com) (for querying and interactive plot visualisation) and [data-gateway](https://link.com) (for data ingress and installation/configuration management.
        """,
        className="sidebar-content",
    )
