import connexion
import six

from openapi_server.models.error_message import ErrorMessage  # noqa: E501
from openapi_server.models.unified_metrics import UnifiedMetrics  # noqa: E501
from openapi_server import util

from openapi_server.controllers.parse_config import parse_conf, parse_host
from openapi_server.controllers.read_param import read_host_list, read_metrics
from openapi_server.controllers.build_metrics import build_metrics


def get_unified_metric(start, end, interval, value, compress, metrics, racks=None, computers=None):  # noqa: E501
    """get_unified_metric

    Get **unified metrics** based on speficied start time, end time, time  interval and value type. The **start** and **end** time should follow  date-time Notation as defined by [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6),  e.g. &#x60;2020-02-12T14:00:00Z&#x60;; the time **interval** should follow  **duration literals**, which specify a length of time; the **value**  type should only be &#x60;min&#x60;, &#x60;max&#x60;, &#x60;mean&#x60;, or &#x60;median&#x60;.  A duration literal is an integer literal followed immediately (with no  spaces) by a duration unit, the units include &#x60;s&#x60;(second), &#x60;m&#x60;(minute),  &#x60;h&#x60;(hour), &#x60;d&#x60;(day), &#x60;w&#x60;(week).  Use compress to specify returned data is compressed or not. If query  large range of time with small interval, it would reduce significant  transfering time using compressed data. For Json data compression and  de-compression, please refer to [this](https://medium.com/@busybus/zipjson-3ed15f8ea85d).  For rack and computer fields, please use a comma to seperate each number  such as &#x60;1, 2, 3, 4&#x60; or use a dash to indicate a range of numbers such  as &#x60;1-4&#x60;. Racks range from **1 to 10** and computers range form **1 to 60** in the Quanah cluster  To be noticed, due to we switched database on April 28, 2020 11:40:00 AM  GMT-05:00 DST, currently we do not support requesting data with time   range falls on this time point.  # noqa: E501

    :param start: Start time of time range.
    :type start: str
    :param end: End time of time range.
    :type end: str
    :param interval: Time interval for aggregating the monitoring metrics.
    :type interval: str
    :param value: Value type of the monitoring metrics.
    :type value: str
    :param compress: Return compressed data.
    :type compress: bool
    :param metrics: Monitoring metrics returned.
    :type metrics: List[str]
    :param racks: Racks of the cluster.
    :type racks: str
    :param computers: Computer IDs on each rack.
    :type computers: str

    :rtype: UnifiedMetrics
    """

    # Parse configuration
    config = parse_conf()
    db_host = config["influxdb"]["host"]
    db_port = config["influxdb"]["port"]

    # Parse host pool from hostlist
    host_pool = parse_host()

    # Generate host list and labels from user specified parameters
    host_list = read_host_list(racks, computers, host_pool)
    labels = read_metrics(metrics)

    start = util.deserialize_datetime(start)
    end = util.deserialize_datetime(end)

    # We changed the database at April 28, 2020 11:40:00 AM GMT-05:00 DST. We
    # need to decide which database we use according to user specified time range
    switch_time = 1588092000
    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    if start_epoch >= switch_time:
        db_name = config["influxdb"]["db_monster"]
    elif end_epoch <= switch_time:
        db_name = config["influxdb"]["database"]
    else:
        return ErrorMessage(
            error_code='400 INVALID_PARAMETERS',
            error_message='Due to we switched database on April 28, 2020 \
                11:40:00 AM GMT-05:00 DST, currently we do not support \
                    requesting data with time range falls on this time point.'
        )
    
    # Check Sanity
    if start > end:
        return ErrorMessage(
            error_code='400 INVALID_PARAMETERS',
            error_message='Start time should no larger than end time'
        )
    else:
        # Query influxDB and build unified metrics
        unified_metrics = build_metrics(db_host, db_port, db_name, 
                                        start, end, 
                                        interval, value, compress, 
                                        host_list, labels)
    return unified_metrics
