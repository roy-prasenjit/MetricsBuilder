import json
import zlib
import base64
import logging
import multiprocessing

from itertools import repeat
from influxdb import InfluxDBClient

from openapi_server.models.unified_metrics import UnifiedMetrics

from openapi_server.controllers.gen_timestamp import gen_timestamp
from openapi_server.controllers.gen_timestamp import gen_epoch_timestamp
from openapi_server.controllers.query_db import query_process_data
from openapi_server.controllers.query_db import query_job_data

ZIPJSON_KEY = 'base64(zip(o))'


def build_metrics(db_host: str, db_port: str, db_name: str, 
                  start: str, end: str, 
                  interval: str, value: str, compress: bool, 
                  host_list: list, labels: dict) -> object:
    
    unified_metrics = UnifiedMetrics()
    results = []
    node_data = {}
    job_data = {}
    all_jobs_list = []
    # Get cpu count
    cpu_count = multiprocessing.cpu_count()
    # Initialize influxDB client
    client = InfluxDBClient(host=db_host, port=db_port, database=db_name)
    # Time string used in query_data
    st_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    et_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Get time stamp
    time_list = gen_timestamp(start, end, interval)
    epoch_time_list = gen_epoch_timestamp(start, end, interval)
    if compress:
        unified_metrics.time_stamp = json_zip(epoch_time_list)
    else:
        unified_metrics.time_stamp = epoch_time_list

    # Get all nodes detail
    query_process_data_args = zip(host_list, repeat(client), 
                                  repeat(st_str), repeat(et_str), 
                                  repeat(interval), repeat(value), 
                                  repeat(time_list), repeat(labels))

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(query_process_data, query_process_data_args)
    
    # Attach data to node ip addr
    for index, node in enumerate(host_list):
        if results[index]:
            node_data[node] = {
                "memory_usage": results[index]["memory_usage"],
                "cpu_usage": results[index]["cpu_usage"],
                "power_usage": results[index]["power_usage"],
                "fan_speed": results[index]["fan_speed"],
                "cpu_inl_temp": results[index]["cpu_inl_temp"],
                "job_id": results[index]["job_list"]
            }
            if results[index]["job_set"]:
                all_jobs_list.extend(results[index]["job_set"])

    if compress:
        unified_metrics.nodes_info = json_zip(node_data)
    else:
        unified_metrics.nodes_info = node_data

    # Get all jobs ID
    all_jobs_id = list(set(all_jobs_list))
    query_job_data_args = zip(repeat(client), all_jobs_id)
    # Get all jobs detail
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(query_job_data, query_job_data_args)
    for index, job in enumerate(all_jobs_id):
        if results[index]:
            job_array = False
            if "." in results[index]["JobId"]:
                job_array = True
            if "FinishTime" in results[index]:
                finish_time = results[index]["FinishTime"]
            else:
                finish_time = None

            if "NodeList" in results[index]:
                node_list = results[index]["NodeList"]
                pro_nodelist = process_nodelist(node_list)
            else:
                node_list = None

            job_data[job] = {
                "start_time": results[index]["StartTime"],
                "submit_time": results[index]["SubmitTime"],
                "finish_time": finish_time,
                "job_name": results[index]["JobName"],
                "user_name": results[index]["User"],
                "node_list": pro_nodelist,
                "total_nodes": results[index]["TotalNodes"],
                "cpu_cores": results[index]["CPUCores"],
                "job_array": job_array
            }
    if compress:
        unified_metrics.jobs_info = json_zip(job_data)
    else:
        unified_metrics.jobs_info = job_data
    return unified_metrics


def process_nodelist(nodelist: str) -> list:
    try:
        nodelist_arr = nodelist[1:-1].split(", ")
        process_nodelist = [node[1:-1].split("-")[0] for node in nodelist_arr]
        return process_nodelist
    except:
        logging.error(f"Failed to process NodeList of node")
        return None


def json_zip(j):
    j = {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii')
    }
    return j