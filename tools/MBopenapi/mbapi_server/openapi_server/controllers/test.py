import connexion
import six
import time
import json
import datetime

from parse_config import parse_conf
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data
from process_data import  process_node_data


start = 1564102552
end = 1564102552 + 24 * 60 * 60
interval = "5m"
value = "max"


# Initialization 
config = parse_conf()
node_list = ['10.101.1.1']
# print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
st = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%SZ')
et = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%SZ')

print(f"Start time: {st}; End time: {et}")

# Check Sanity

all_data = query_data(node_list, influx, st, et, interval, value)

processed_data = process_node_data(node_list, all_data["node_data"], value)

print(json.dumps(processed_data, indent=4))
