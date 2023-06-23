import datetime
import datetime as dt
import logging
import threading

import plotly.express as px
import requests
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from aerosense_tools.plots import plot_connection_statistic, plot_cp_curve, plot_sensors
from aerosense_tools.preprocess import RawSignal, SensorMeasurementSession
from aerosense_tools.queries import ROW_LIMIT, BigQuery
from dashboard.utils import generate_time_range


logger = logging.getLogger(__name__)


SESSIONS_EXTRACTION_CLOUD_FUNCTION_URL = (
    "https://europe-west6-aerosense-twined.cloudfunctions.net/data-gateway-sessions"
)


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
        State("measurement-session-select", "value"),
        Input("refresh-button", "n_clicks"),
    )
    @cache.memoize(timeout=cache_timeout, args_to_ignore=["refresh"])
    def plot_information_sensors_graph(
        installation_reference,
        node_id,
        y_axis_column,
        time_range,
        measurement_session,
        refresh,
    ):
        """Plot a graph of the information sensors for the given installation, y-axis column, and time range when these
        values are changed or the refresh button is clicked.

        :param str installation_reference:
        :param str node_id:
        :param str y_axis_column:
        :param str time_range:
        :param str measurement_session:
        :param int refresh:
        :return (plotly.graph_objs.Figure, str):
        """
        if not node_id:
            node_id = None

        start, finish = generate_time_range(time_range, measurement_session)

        if start is None:
            return (px.scatter(), "No measurement session selected.")

        if y_axis_column == "battery_info":
            df, data_limit_applied = BigQuery().get_sensor_data(
                installation_reference,
                node_id,
                y_axis_column,
                start=start,
                finish=finish,
            )

            if df.empty:
                return (px.scatter(), "No data to plot.")

            figure = plot_sensors(df, line_descriptions=sensor_types[y_axis_column]["variable"])

        else:
            df = BigQuery().get_aggregated_connection_statistics(
                installation_reference=installation_reference,
                node_id=node_id,
                start=start,
                finish=finish,
            )

            if df.empty:
                return (px.scatter(), "No data to plot.")

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
        State("measurement-session-select", "value"),
        Input("refresh-button", "n_clicks"),
    )
    @cache.memoize(timeout=cache_timeout, args_to_ignore=["refresh"])
    def plot_sensors_graph(
        installation_reference,
        node_id,
        sensor_name,
        time_range,
        measurement_session,
        refresh,
    ):
        """Plot a graph of the sensor data for the given installation, y-axis column, and time range when these values are
        changed or the refresh button is clicked.

        :param str installation_reference:
        :param str node_id:
        :param str sensor_name:
        :param str time_range:
        :param str measurement_session:
        :param int refresh:
        :return (plotly.graph_objs.Figure, str):
        """
        if not node_id:
            node_id = None

        start, finish = generate_time_range(time_range, measurement_session)

        if start is None:
            return (px.scatter(), "No measurement session selected.")

        df, data_limit_applied = BigQuery().get_sensor_data(
            installation_reference,
            node_id,
            sensor_name,
            start=start,
            finish=finish,
        )

        if df.empty:
            return (px.scatter(), "No data to plot.")

        # Extract only data columns and set index to 'datetime', so that DataFrame is accepted by RawSignal class
        data_columns = df.columns[df.columns.str.startswith("f")].tolist()
        sensor_data = df[["datetime"] + data_columns].set_index("datetime")
        sensor_data.columns = sensor_types[sensor_name]["sensors"]
        # Use pre-process library
        raw_data = RawSignal(sensor_data, sensor_name)
        raw_data.pad_gaps()
        raw_data.measurement_to_variable()
        sensor_session = SensorMeasurementSession(raw_data.dataframe, sensor_name)

        figure = sensor_session.plot(sensor_types)
        figure.update_layout(height=800)

        if data_limit_applied:
            return (figure, f"Large amount of data - the query has been limited to the latest {ROW_LIMIT} datapoints.")

        return (figure, [])

    @cache.memoize(timeout=0)
    def get_pressure_data_for_time_window(installation_reference, node_id, start_datetime, finish_datetime):
        """Get pressure data for the given node during the given time window along with the minimum and maximum
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
            "Downloaded pressure data %d second time window for start datetime %r and finish datetime %r.",
            (finish_datetime - start_datetime).seconds,
            start_datetime.isoformat(),
            finish_datetime.isoformat(),
        )

        return df

    @app.callback(
        Output("pressure-profile-graph", "figure"),
        State("installation-select", "value"),
        State("node-select", "value"),
        State("sensor-coordinates-select", "value"),
        State("air-density-input", "value"),
        State("u-input", "value"),
        State("p-inf-input", "value"),
        State("cp-minimum-input", "value"),
        State("cp-maximum-input", "value"),
        State("date-select", "date"),
        State("hour", "value"),
        State("minute", "value"),
        State("second", "value"),
        Input("time-slider", "value"),
        Input("refresh-button", "n_clicks"),
    )
    @cache.memoize(timeout=cache_timeout, args_to_ignore=["refresh"])
    def plot_cp_graph(
        installation_reference,
        node_id,
        sensor_coordinates_reference,
        air_density,
        u,
        p_inf,
        cp_minimum,
        cp_maximum,
        date,
        hour,
        minute,
        second,
        time_delta,
        refresh,
    ):
        if not node_id:
            node_id = None

        initial_datetime = dt.datetime.combine(date=dt.date.fromisoformat(date), time=dt.time(hour, minute, second))

        df = get_pressure_data_for_time_window(
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

        logger.debug("Filtered pressure data time window for single datetime.")

        return plot_cp_curve(
            df=df,
            sensor_coordinates_reference=sensor_coordinates_reference,
            air_density=air_density,
            u=u,
            p_inf=p_inf,
            cp_minimum=cp_minimum,
            cp_maximum=cp_maximum,
        )

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
        Output("sensor-coordinates-select", "options"),
        Input("sensor-coordinates-check-button", "n_clicks"),
    )
    def update_sensor_coordinates_selector(refresh):
        """Update the sensor coordinates selector with any new ones when the refresh button is clicked.

        :param int refresh:
        :return list:
        """
        return BigQuery().get_sensor_coordinates()["reference"]

    @app.callback(
        Output("graph-title", "children"),
        State("y-axis-select", "value"),
        Input("refresh-button", "n_clicks"),
    )
    def update_graph_title(selected_y_axis, refresh):
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
            Output("measurement-session-select", "disabled"),
            Output("measurement-session-check-button", "disabled"),
        ],
        [
            Input("time-range-select", "value"),
        ],
    )
    def enable_measurement_session_time_range_select(time_range):
        """Enable the measurement session time range selection if "Measurement session" is chosen in the time range
        selector.

        :param str time_range:
        :return bool:
        """
        disabled = time_range != "Measurement session"
        return (
            disabled,
            None,
            disabled,
            disabled,
            disabled,
            disabled,
            None,
            disabled,
            disabled,
            disabled,
            disabled,
            disabled,
        )

    @app.callback(
        Output("measurement-session-select", "options"),
        Output("measurement-session-select", "value"),
        State("measurement-session-select", "disabled"),
        State("installation-select", "value"),
        State("node-select", "value"),
        State("y-axis-select", "value"),
        State("start-date", "date"),
        State("start-hour", "value"),
        State("start-minute", "value"),
        State("start-second", "value"),
        State("end-date", "date"),
        State("end-hour", "value"),
        State("end-minute", "value"),
        State("end-second", "value"),
        Input("measurement-session-check-button", "n_clicks"),
    )
    def update_measurement_session_selector(
        measurement_session_selection_disabled,
        installation_reference,
        node_id,
        y_axis,
        start_date,
        start_hour,
        start_minute,
        start_second,
        end_date,
        end_hour,
        end_minute,
        end_second,
        refresh,
    ):
        if measurement_session_selection_disabled:
            raise PreventUpdate

        start_datetime, finish_datetime = _combine_dates_and_times(
            start_date,
            start_hour,
            start_minute,
            start_second,
            end_date,
            end_hour,
            end_minute,
            end_second,
        )

        # The connection statistics always come together, so they have the same measurement sessions.
        if y_axis in {"filtered_rssi", "filtered_rssi", "tx_power", "allocated_heap_memory"}:
            y_axis = "connection_statistics"

        measurement_sessions = BigQuery().get_measurement_sessions(
            installation_reference=installation_reference,
            node_id=node_id,
            sensor_type_reference=y_axis,
            start=start_datetime,
            finish=finish_datetime,
        )

        measurement_sessions = [
            f"{session[1][0]} to {session[1][1]}"
            for session in measurement_sessions[["start_datetime", "finish_datetime"]].iterrows()
        ]

        if not measurement_sessions:
            return [], None

        return measurement_sessions, measurement_sessions[0]

    @app.callback(
        # Use a dummy output.
        Output("run-session-extraction-output-placeholder", "children"),
        Input("run-session-extraction", "n_clicks"),
        prevent_initial_call=True,
    )
    def run_session_extraction_in_database(refresh):
        """Trigger measurement session extraction in the database.

        :return None:
        """
        threading.Thread(target=requests.post, args=(SESSIONS_EXTRACTION_CLOUD_FUNCTION_URL,), daemon=True).start()
        logger.info("Triggered measurement session extraction cloud function.")

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
