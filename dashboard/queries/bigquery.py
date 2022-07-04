from datetime import datetime
from google.cloud import bigquery


bqclient = bigquery.Client()


# SCRATCH: MIGHT BE USEFUL, OTHERWISE GET RID:
# ============================================
# AND datetime > DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour HOUR)
# AND datetime < DATE_ADD(PARSE_DATETIME('%Y%m%d', @DS_START_DATE), INTERVAL @hour+1 HOUR)
# AND IS_NAN(sensor_value[ORDINAL(1)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(2)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(3)]) IS FALSE
# AND IS_NAN(sensor_value[ORDINAL(4)]) IS FALSE


connection_statistics_agg_sql = """
SELECT datetime, filtered_rssi,	raw_rssi, tx_power, allocated_heap_memory, installation_reference
FROM `aerosense-twined.greta.connection_statistics_agg`
WHERE datetime BETWEEN DATETIME_SUB(@up_to, INTERVAL 1 DAY) AND @up_to
AND installation_reference = @installation_reference
"""


def get_connection_statistics_agg(installation_reference, up_to=None):
    """Query for minute-wise aggregated connection statistics over a day, by default the day up to now.
    :param [str] installation_reference: The installation reference to query for, e.g. "ost-wt-tests"
    :param Union[datetime.datetime, None] up_to: The point in time, default now(), where results will
    be delivered for the 24 hours prior.
    """
    print("Getting constats_agg", up_to, installation_reference)
    up_to = up_to if up_to is not None else datetime.now()
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("installation_reference", "STRING", installation_reference),
            bigquery.ScalarQueryParameter("up_to", "DATETIME", up_to),
        ]
    )
    return bqclient.query(connection_statistics_agg_sql, job_config=query_config).to_dataframe()


installations_sql = """
SELECT reference, turbine_id, location
FROM `aerosense-twined.greta.installation`
"""


def get_installations():
    """Query for all installations (without sensor coordinate data)"""
    return bqclient.query(installations_sql).to_dataframe()


installation_sql = """
SELECT reference, turbine_id, location
FROM `aerosense-twined.greta.installation`
WHERE installation_reference = @installation_reference
"""


def get_installation(installation_reference):
    """Query for an installation (with sensor coordinate data)
    May return multiple rows if the installation has had upgraded hardware
    :param [str] installation_reference: The installation reference to query for, e.g. "ost-wt-tests"
    """
    query_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("installation_reference", "STRING", installation_reference)]
    )
    return bqclient.query(installation_sql, job_config=query_config).to_dataframe()
