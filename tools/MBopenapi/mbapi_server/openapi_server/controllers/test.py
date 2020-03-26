import connexion
import six
import time
import json
import datetime

import multiprocessing
from itertools import repeat

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_process_data


hours = 1
start = 1564100000
end = 1564100000 + hours * 60 * 60
interval = "5m"
value = "max"

all_data = {}
node_data = {}
# Initialization 
config = parse_conf()
node_list = parse_host()
# node_list = ["10.101.1.1", "10.101.1.2"]
# print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
st = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%SZ')
et = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%SZ')

# print(f"Start time: {st}; End time: {et}")

cpu_count = multiprocessing.cpu_count()
query_start = time.time()

query_process_data_args = zip(node_list, repeat(influx), 
                           repeat(st), repeat(et), 
                           repeat(interval), repeat(value))

with multiprocessing.Pool(processes=cpu_count) as pool:
    results = pool.starmap(query_process_data, query_process_data_args)

print(len(results))
# print(json.dumps(results, indent=4))

all_job_list = []

# for index, node in enumerate(node_list):
#     # node_data[node] = {}
#     # node_data[node].update({
#     #     "memory_usage": results[index]["memory_usage"],
#     #     "cpu_usage": results[index]["cpu_usage"],
#     #     "power_usage": results[index]["power_usage"],
#     #     "fan_speed": results[index]["fan_speed"],
#     #     "cpu_inl_temp": results[index]["cpu_inl_temp"],
#     #     "job_id": results[index]["job_id"]
#     # })

#     all_job_list.extend(results[index]["job_list"])

# print(json.dumps(node_data, indent=4))

# all_jobs = list(set(all_job_list))
# all_jobs = []
# for result in results:
#     for job_list in result["job_id"]:
#         for job_id in job_list:
#             all_jobs.append(job_id)

# print(f"All job list length: {len(all_jobs)}")
# print(f"All job set length: {len(list(set(all_jobs)))}")

# query_elapsed = float("{0:.2f}".format(time.time() - query_start))
# print(f"Time for Quering and Processing {hours} of data : {query_elapsed}")


