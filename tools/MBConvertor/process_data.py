import time
from dateutil import parser


def process_data(data: list, measurement: str) -> list:
    """
    Process data accroding to the schema in measurements
    """
    result = []
    process_dict = {
        "CPU_Temperature": process_CPU_Temperature,
        "CPU_Usage": process_CPU_Usage,
        "Fan_Speed": process_Fan_Speed,
        "Inlet_Temperature": process_Inlet_Temperature,
        "Job_Info": process_Job_Info,
        "Memory_Usage": process_Memory_Usage,
        "Node_Power_Usage": process_Node_Power_Usage,
        "cluster_unified_metrics": process_cluster_unified_metrics,
        "node_job_info": process_node_job_info,
        "system_metrics": process_system_metrics
    }
    if process_dict.get(measurement) and process_dict.get(measurement)(data):
        result.extend(process_dict.get(measurement)(data))
    return result


def process_data_job(data: dict, measurement: str) -> dict:
    """
    Process job info accroding to the schema in measurements
    """
    data_point = None
    try:
        start = int(parser.parse(data["startTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        submit = int(parser.parse(data["submitTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())

        if "i" in measurement:
            nodes = data["nodes"]
            if "," in nodes:
                node_list = nodes.split(",")
            else:
                node_list = [nodes]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": measurement.split("i")[1],
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": node_list,
                    "CPUCores": data["CPUCores"], 
                    "JobName": None,
                    "User": data["user"]
                }
            }
            return data_point
        if "j" in measurement:
            nodes = data["nodes"]
            if "," in nodes:
                node_list = nodes.split(",")
            else:
                node_list = [nodes]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": measurement.split("-")[1],
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": node_list,
                    "CPUCores": data["CPUCores"], 
                    "JobName": None,
                    "User": data["user"]
                }
            }
            return data_point
        if "qu" in measurement:
            job = measurement
            if "A" in job:
                job_id = job.split("_")[1].replace("A", ".")
            else:
                job_id = job.split("_")[1]

            nodes = data["nodes_address"]
            if "," in nodes:
                node_list = [node.split("-")[0] for node in nodes.split(",")]
            else:
                node_list = [nodes.split("-")[0]]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": job_id,
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": node_list,
                    "CPUCores": data["CPUCores"], 
                    "JobName": data["app_name"],
                    "User": data["user"]
                }
            }
            return data_point
    except Exception as err:
        # print(err)
        return data_point

def process_CPU_Temperature(data: dict) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU1Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["CPU1 Temp"]
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU2Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["CPU2 Temp"]
            }
        }
        result = [data_point_1, data_point_2]
    except Exception:
        # print(err)
        pass
    return result


def process_CPU_Usage(data: dict) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host
        
        if data.get("cpuusage") and data["cpuusage"] != 0:
            cpuusage = data["cpuusage"]
        elif data.get("cpuusage(load)") and data["cpuusage(load)"] != 0:
            cpuusage = data["cpuusage(load)"]
        else:
            return result

        data_point = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "CPUUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(cpuusage))
            }
        }
        result = [data_point]
    except Exception:
        # print(err)
        pass
    return result


def process_Fan_Speed(data: dict) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_1",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["FAN_1"]
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_2",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["FAN_2"]
            }
        }
        data_point_3 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_3",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["FAN_3"]
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_4",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["FAN_4"]
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4]
    except Exception:
        # print(err)
        pass
    return result

def process_Inlet_Temperature(data: dict) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "InletTemp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["Inlet Temp"]
            }
        }
        result = [data_point]
    except Exception:
        # print(err)
        pass
    return result

# If the data is from Job_Info measurement, 
# the processed data point should be saved to another measurement
def process_Job_Info(data: dict) -> list:
    result = []
    try:
        start = int(parser.parse(data["startTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        submit = int(parser.parse(data["submitTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        
        # Discard the host inforamtion, 
        # since the data stored in this field are not consistent
        # if data["host"][0] == "[":
        #     hostlist = [host[1:-1] for host in data["host"][0:-1].split(", ")]
        # else:
        #     hostlist = [data["host"]]

        data_point = {
            "measurement": "JobsInfo",
            "time": data["time"],
            "tags": {
                "JobId": data["jobID"],
                "Queue": data["cluster"]
            }, 
            "fields": {
                "StartTime": start,
                "SubmitTime": submit,
                "TotalNodes": None,
                "NodeList": None,
                "CPUCores": None,
                "JobName": None,
                "User": data["user"]
            }

        }
        result = [data_point]
    except Exception:
        # print(err)
        pass
    return result


def process_Memory_Usage(data: dict) -> list: 
    result = []
    try:
        available_memory = float(data["available_memory"].split("G")[0])
        total_memory = float(data["total_memory"].split("G")[0])
        mem_usage = (total_memory - available_memory)/total_memory

        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host
         
        data_point = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "MemUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(mem_usage))
            }
        }
        result = [data_point]
    except Exception:
        # print(err)
        pass
    return result


def process_Node_Power_Usage(data: dict) -> list:
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Sensor": "NodePower",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["powerusage_watts"]
            }
        }
        result = [data_point]
    except Exception:
        # print(err)
        pass
    return result


def process_cluster_unified_metrics(data: dict) -> list:
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU1Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["CPU1_temp"]
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU2Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["CPU2_temp"]
            }
        }
        data_point_3 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "CPUUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["cpuusage"]))
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_1",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["fan1_speed"]
            }
        }
        data_point_5 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_2",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["fan2_speed"]
            }
        }
        data_point_6 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_3",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["fan3_speed"]
            }
        }
        data_point_7 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_4",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["fan4_speed"]
            }
        }
        data_point_8 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "InletTemp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["inlet_temp"]
            }
        }
        data_point_9 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "MemUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["memoryusage"]))
            }
        }
        data_point_10 = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Sensor": "NodePower",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": data["powerusage_watts"]
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4, 
                  data_point_5, data_point_6, data_point_7, data_point_8,
                  data_point_9, data_point_10] 
    except Exception:
        # print(err)
        pass
    return result


def process_node_job_info(data: dict) -> list:
    result = []
    try:
        joblist = [job.split("qu_")[1].replace("A", ".") for job in data["jobID"].split(",")]
        data_point = {
            "measurement": "NodeJobs",
            "time": data["time"],
            "tags": {
                "NodeId": data["host"]
            }, 
            "fields": {
                "JobList": joblist
            }
        }
        result.append(data_point)
    except Exception:
        # print(err)
        pass
    return result


def process_system_metrics(data: dict) -> list:
    result = []
    try:
        joblist = [job.split("qu_")[1].replace("A", ".") for job in data["jobID"].split(",")]
        
        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU1Temp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["CPU1_temp"]
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "CPU2Temp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["CPU2_temp"]
            }
        }
        data_point_3 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "CPUUsage",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["cpuusage"]))
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_1",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["fan1_speed"]
            }
        }
        data_point_5 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_2",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["fan2_speed"]
            }
        }
        data_point_6 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_3",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["fan3_speed"]
            }
        }
        data_point_7 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "FAN_4",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["fan4_speed"]
            }
        }
        data_point_8 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Sensor": "InletTemp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["inlet_temp"]
            }
        }
        data_point_9 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Sensor": "MemUsage",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["memoryusage"]))
            }
        }
        data_point_10 = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Sensor": "NodePower",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": data["powerusage_watts"]
            }
        }
        data_point_11 = {
            "measurement": "NodeJobs",
            "time": data["time"],
            "tags": {
                "NodeId": data["host"]
            }, 
            "fields": {
                "JobList": joblist
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4, 
                  data_point_5, data_point_6, data_point_7, data_point_8,
                  data_point_9, data_point_10, data_point_11] 
    except Exception:
        # print(err)
        pass
    return result
