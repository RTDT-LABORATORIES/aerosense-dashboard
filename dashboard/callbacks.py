import datetime
import datetime as dt
import logging

from dash import Input, Output, State

from aerosense_tools.plots import plot_connection_statistic, plot_pressure_bar_chart, plot_sensors
from aerosense_tools.preprocess import RawSignal
from aerosense_tools.queries import ROW_LIMIT, BigQuery
from aerosense_tools.utils import generate_time_range, get_cleaned_sensor_column_names


logger = logging.getLogger(__name__)


def register_callbacks(app, cache, cache_timeout, tabs, sensor_types):
    """Register the dashboards callbacks with the app.

    :param dash.Dash app:
    :param flask_caching.Cache cache:
    :param int|float cache_timeout:
    :param dict tabs:
    :param dict sensor_types:
    :return None:
    """

    @app.callback(
        Output("information-sensors-graph", "figure"),
        Output("information-sensor-data-limit-warning", "children"),
        State("installation-select", "value"),
        State("node-select", "value"),
        State("y-axis-select", "value"),
        State("time-range-select", "value"),
        State("start-date", "date"),
        State("start-hour", "value"),
        State("start-minute", "value"),
        State("start-second", "value"),
        State("end-date", "date"),
        State("end-hour", "value"),
        State("end-minute", "value"),
        State("end-second", "value"),
        Input("refresh-button", "n_clicks"),
    )
    @cache.memoize(timeout=cache_timeout, args_to_ignore=["refresh"])
    def plot_information_sensors_graph(
        installation_reference,
        node_id,
        y_axis_column,
        time_range,
        custom_start_date,
        custom_start_hour,
        custom_start_minute,
        custom_start_second,
        custom_end_date,
        custom_end_hour,
        custom_end_minute,
        custom_end_second,
        refresh,
    ):
        """Plot a graph of the information sensors for the given installation, y-axis column, and time range when these
        values are changed or the refresh button is clicked.

        :param str installation_reference:
        :param str node_id:
        :param str y_axis_column:
        :param str time_range:
        :param str|None custom_start_date:
        :param int|None custom_start_hour:
        :param int|None custom_start_minute:
        :param int|None custom_start_second:
        :param str|None custom_end_date:
        :param int|None custom_end_hour:
        :param int|None custom_end_minute:
        :param int|None custom_end_second:
        :param int refresh:
        :return (plotly.graph_objs.Figure, str):
        """
        if not node_id:
            node_id = None

        custom_start, custom_end = _combine_dates_and_times(
            custom_start_date,
            custom_start_hour,
            custom_start_minute,
            custom_start_second,
            custom_end_date,
            custom_end_hour,
            custom_end_minute,
            custom_end_second,
        )

        start, finish = generate_time_range(time_range, custom_start, custom_end)

        if y_axis_column == "battery_info":
            df, data_limit_applied = BigQuery().get_sensor_data(
                installation_reference,
                node_id,
                y_axis_column,
                start=start,
                finish=finish,
            )

            figure = plot_sensors(df, line_descriptions=sensor_types[y_axis_column]["variable"])

        else:
            df = BigQuery().get_aggregated_connection_statistics(
                installation_reference=installation_reference,
                node_id=node_id,
                start=start,
                finish=finish,
            )

            data_limit_applied = ""
            figure = plot_connection_statistic(df, y_axis_column)

        if data_limit_applied:
            return (figure, f"Large amount of data - the query has been limited to the latest {ROW_LIMIT} datapoints.")

        return (figure, [])

    @app.callback(
        Output("sensors-graph", "figure"),
        Output("sensor-data-limit-warning", "children"),
        State("installation-select", "value"),
        State("node-select", "value"),
        State("y-axis-select", "value"),
        State("time-range-select", "value"),
        State("start-date", "date"),
        State("start-hour", "value"),
        State("start-minute", "value"),
        State("start-second", "value"),
        State("end-date", "date"),
        State("end-hour", "value"),
        State("end-minute", "value"),
        State("end-second", "value"),
        Input("refresh-button", "n_clicks"),
    )
    @cache.memoize(timeout=cache_timeout, args_to_ignore=["refresh"])
    def plot_sensors_graph(
        installation_reference,
        node_id,
        sensor_name,
        time_range,
        custom_start_date,
        custom_start_hour,
        custom_start_minute,
        custom_start_second,
        custom_end_date,
        custom_end_hour,
        custom_end_minute,
        custom_end_second,
        refresh,
    ):
        """Plot a graph of the sensor data for the given installation, y-axis column, and time range when these values are
        changed or the refresh button is clicked.

        :param str installation_reference:
        :param str node_id:
        :param str sensor_name:
        :param str time_range:
        :param str|None custom_start_date:
        :param int|None custom_start_hour:
        :param int|None custom_start_minute:
        :param int|None custom_start_second:
        :param str|None custom_end_date:
        :param int|None custom_end_hour:
        :param int|None custom_end_minute:
        :param int|None custom_end_second:
        :param int refresh:
        :return (plotly.graph_objs.Figure, str):
        """
        if not node_id:
            node_id = None

        custom_start, custom_end = _combine_dates_and_times(
            custom_start_date,
            custom_start_hour,
            custom_start_minute,
            custom_start_second,
            custom_end_date,
            custom_end_hour,
            custom_end_minute,
            custom_end_second,
        )

        start, finish = generate_time_range(time_range, custom_start, custom_end)

        df, data_limit_applied = BigQuery().get_sensor_data(
            installation_reference,
            node_id,
            sensor_name,
            start=start,
            finish=finish,
        )

        data_columns = df.columns[df.columns.str.startswith("f")].tolist()
        sensor_data = df[["datetime"] + data_columns].set_index("datetime")
        raw_data = RawSignal(sensor_data, sensor_name)
        raw_data.measurement_to_variable()
        plot_df = raw_data.dataframe.reset_index()

        figure = plot_sensors(plot_df, line_descriptions=sensor_types[sensor_name]["variable"])
        figure.update_layout(height=800)

        if data_limit_applied:
            return (figure, f"Large amount of data - the query has been limited to the latest {ROW_LIMIT} datapoints.")

        return (figure, [])

    @cache.memoize(timeout=0)
    def get_pressure_profiles_for_time_window(installation_reference, node_id, start_datetime, finish_datetime):
        """Get pressure profiles for the given node during the given time window along with the minimum and maximum
        pressures over all the sensors over that window.

        :param str installation_reference:
        :param str node_id:
        :param datetime.datetime start_datetime:
        :param datetime.datetime finish_datetime:
        :return (pandas.DataFrame, float, float): the pressure profiles, minimum pressure, and maximum pressure for the time window
        """
        df, _ = BigQuery().get_sensor_data(
            installation_reference=installation_reference,
            node_id=node_id,
            sensor_type_reference="barometer",
            start=start_datetime,
            finish=finish_datetime,
        )

        logger.info(
            "Downloaded pressure profile %d second time window for start datetime %r and finish datetime %r.",
            (finish_datetime - start_datetime).seconds,
            start_datetime.isoformat(),
            finish_datetime.isoformat(),
        )

        sensor_column_names, _ = get_cleaned_sensor_column_names(df)
        df_with_sensors_only = df[sensor_column_names]
        return (df, df_with_sensors_only.min().min(), df_with_sensors_only.max().max())

    @app.callback(
        Output("pressure-profile-graph", "figure"),
        State("installation-select", "value"),
        State("node-select", "value"),
        State("date-select", "date"),
        State("hour", "value"),
        State("minute", "value"),
        State("second", "value"),
        Input("time-slider", "value"),
        Input("refresh-button", "n_clicks"),
    )
    def plot_pressure_profile_graph(installation_reference, node_id, date, hour, minute, second, time_delta, refresh):
        if not node_id:
            node_id = None

        initial_datetime = dt.datetime.combine(date=dt.date.fromisoformat(date), time=dt.time(hour, minute, second))

        df, minimum, maximum = get_pressure_profiles_for_time_window(
            installation_reference=installation_reference,
            node_id=node_id,
            start_datetime=initial_datetime,
            finish_datetime=initial_datetime + dt.timedelta(seconds=60),
        )

        slider_datetime = initial_datetime + dt.timedelta(seconds=time_delta)

        df = df[
            (df["datetime"] >= slider_datetime - dt.timedelta(seconds=0.5))
            & (df["datetime"] < slider_datetime + dt.timedelta(seconds=0.5))
        ]

        logger.debug("Filtered pressure profile time window for single datetime.")
        return plot_pressure_bar_chart(df, minimum, maximum)

    @app.callback(
        Output("installation-select", "options"),
        Input("installation-check-button", "n_clicks"),
    )
    def update_installation_selector(refresh):
        """Update the installation selector with any new installations when the refresh button is clicked.

        :param int refresh:
        :return list:
        """
        return BigQuery().get_installations()

    @app.callback(
        [
            Output("node-select", "options"),
            Output("node-select", "value"),
        ],
        [
            Input("installation-select", "value"),
        ],
    )
    @cache.memoize(timeout=cache_timeout)
    def update_node_selector(installation_reference):
        """Update the node selector options with the IDs of the nodes available for the given installation.

        :param str installation_reference:
        :return list(str):
        """
        nodes = BigQuery().get_nodes(installation_reference)

        try:
            first_option = nodes[0]
        except IndexError:
            first_option = None

        return nodes, first_option

    @app.callback(
        Output("graph-title", "children"),
        Input("y-axis-select", "value"),
    )
    def update_graph_title(selected_y_axis):
        """Update the graph title with the name of the currently selected y-axis.

        :param str selected_y_axis:
        :return str:
        """
        if not selected_y_axis:
            return ""

        return " ".join(selected_y_axis.split("_")).capitalize()

    @app.callback(
        [
            Output("start-date", "disabled"),
            Output("start-date", "date"),
            Output("start-hour", "disabled"),
            Output("start-minute", "disabled"),
            Output("start-second", "disabled"),
            Output("end-date", "disabled"),
            Output("end-date", "date"),
            Output("end-hour", "disabled"),
            Output("end-minute", "disabled"),
            Output("end-second", "disabled"),
        ],
        [
            Input("time-range-select", "value"),
        ],
    )
    def enable_custom_time_range_select(time_range):
        """Enable the custom time range selection if "Custom" is chosen in the time range selector.

        :param str time_range:
        :return bool:
        """
        disabled = time_range != "Custom"
        return (disabled, None, disabled, disabled, disabled, disabled, None, disabled, disabled, disabled)

    @app.callback(
        Output("app", "children"),
        Input("nav-tabs", "value"),
    )
    def change_tabs(section_name):
        """Change the buttons shown on the dashboard when a navigation tab is clicked.

        :param str section_name:
        :return list:
        """
        return tabs[section_name]


def _combine_dates_and_times(
    start_date,
    start_hour,
    start_minute,
    start_second,
    end_date,
    end_hour,
    end_minute,
    end_second,
):
    """If all inputs are given, combine the start inputs into a start datetime and the end inputs into an end datetime;
    otherwise, return `None` as the start and end datetimes.

    :param str|None start_date:
    :param int|None start_hour:
    :param int|None start_minute:
    :param int|None start_second:
    :param str|None end_date:
    :param int|None end_hour:
    :param int|None end_minute:
    :param int|None end_second:
    :return (datetime.datetime, datetime.datetime)|(None, None):
    """
    if all(
        argument is not None
        for argument in (start_date, start_hour, start_minute, start_second, end_date, end_hour, end_minute, end_second)
    ):
        start = datetime.datetime.combine(
            dt.date.fromisoformat(start_date),
            datetime.time(hour=start_hour, minute=start_minute, second=start_second),
        )

        end = datetime.datetime.combine(
            dt.date.fromisoformat(end_date),
            datetime.time(hour=end_hour, minute=end_minute, second=end_second),
        )

        return (start, end)

    return (None, None)
