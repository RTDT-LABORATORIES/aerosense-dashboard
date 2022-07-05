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

        if all_time:
            start = datetime.datetime.min
            finish = datetime.datetime.now()
        else:
            finish = finish if finish else datetime.datetime.now()
            start = start if start else finish - datetime.timedelta(days=1)

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
