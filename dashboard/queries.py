import datetime

from google.cloud import bigquery


# SCRATCH: MIGHT BE USEFUL, OTHERWISE GET RID:
# ============================================
# AND datetime > DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour HOUR)
# AND datetime < DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour+1 HOUR)
# AND IS_NAN(sensor_value[ORDINAL(1)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(2)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(3)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(4)]) IS FALSE


class BigQuery:
    def __init__(self):
        self.client = bigquery.Client()

    def get_sensor_data(
        self,
        installation_reference,
        node_id,
        sensor_type_reference,
        start=None,
        finish=None,
        all_time=False,
    ):
        """Get sensor data for the given sensor type on the given node of the given installation over the given time
        period. The time period defaults to the last day.

        :param str installation_reference:
        :param str node_id:
        :param str sensor_type_reference:
        :param datetime.datetime|None start:
        :param datetime.datetime|None finish:
        :param bool all_time:
        :return pandas.Dataframe:
        """
        query = """
        SELECT datetime, sensor_value
        FROM `aerosense-twined.greta.sensor_data`
        WHERE datetime BETWEEN @start AND @finish
        AND installation_reference = @installation_reference
        AND node_id = @node_id
        AND sensor_type_reference = @sensor_type_reference
        """

        start, finish = self._get_time_period(start, finish, all_time)

        query_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start", "DATETIME", start),
                bigquery.ScalarQueryParameter("finish", "DATETIME", finish),
                bigquery.ScalarQueryParameter("installation_reference", "STRING", installation_reference),
                bigquery.ScalarQueryParameter("node_id", "STRING", node_id),
                bigquery.ScalarQueryParameter("sensor_type_reference", "STRING", sensor_type_reference),
            ]
        )

        return self.client.query(query, job_config=query_config).to_dataframe()

    def get_aggregated_connection_statistics(self, installation_reference, start=None, finish=None, all_time=False):
        """Query for minute-wise aggregated connection statistics over a day, by default the day up to now.

        :param [str] installation_reference: The installation reference to query for, e.g. "ost-wt-tests"
        :param Union[datetime.datetime, None] up_to: The point in time, default now(), where results will
        be delivered for the 24 hours prior.
        """
        connection_statistics_agg_sql = """
        SELECT datetime, filtered_rssi, raw_rssi, tx_power, allocated_heap_memory
        FROM `aerosense-twined.greta.connection_statistics_agg`
        WHERE datetime BETWEEN @start AND @finish
        AND installation_reference = @installation_reference
        """

        start, finish = self._get_time_period(start, finish, all_time)

        query_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("installation_reference", "STRING", installation_reference),
                bigquery.ScalarQueryParameter("start", "DATETIME", start),
                bigquery.ScalarQueryParameter("finish", "DATETIME", finish),
            ]
        )

        return self.client.query(connection_statistics_agg_sql, job_config=query_config).to_dataframe()

    def get_installations(self):
        """Query for all installations (without sensor coordinate data)"""
        installations_sql = """
        SELECT reference, turbine_id, location
        FROM `aerosense-twined.greta.installation`
        """

        return self.client.query(installations_sql).to_dataframe()

    def get_installation(self, installation_reference):
        """Query for an installation (with sensor coordinate data)
        May return multiple rows if the installation has had upgraded hardware

        :param [str] installation_reference: The installation reference to query for, e.g. "ost-wt-tests"
        """
        installation_sql = """
        SELECT reference, turbine_id, location
        FROM `aerosense-twined.greta.installation`
        WHERE installation_reference = @installation_reference
        """

        query_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("installation_reference", "STRING", installation_reference)]
        )

        return self.client.query(installation_sql, job_config=query_config).to_dataframe()

    def _get_time_period(self, start=None, finish=None, all_time=False):
        """Get the time period for the query. Defaults to the past day.

        :param datetime.datetime|None start:
        :param datetime.datetime|None finish:
        :param bool all_time:
        :return (datetime.datetime, datetime.datetime):
        """
        if all_time:
            start = datetime.datetime.min
            finish = datetime.datetime.now()

        # Default to the last day of data.
        else:
            finish = finish or datetime.datetime.now()
            start = start or finish - datetime.timedelta(days=1)

        return start, finish
