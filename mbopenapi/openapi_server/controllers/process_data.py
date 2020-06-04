import time
import json
import logging
import multiprocessing


def process_node_data(node: str, node_data: dict, value: str, 
                      time_list: list, labels: dict) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    # UGE
    memory_usage = []
    cpu_usage = []
    # Power
    power_usage = []
    # Temperature
    cpu_1_temp = []
    cpu_2_temp = []
    inlet_temp = []
    cpu_inl_temp = []
    # Fan speed
    fan_1 = []
    fan_2 = []
    fan_3 = []
    fan_4 = []
    fan_speed = []
    # Job list
    job_list_dict = {}
    job_list_temp = []
    job_list = []
    job_set = []
    db_time_list = []

    thermal_labels = labels["thermal_labels"]
    uge_labels = labels["uge_labels"]
    power_labels = labels["power_labels"]

    try:
        if "MemUsage" in uge_labels and node_data["MemUsage"]:
            memory_usage = [item[value] for item in node_data["MemUsage"]]

        if "CPUUsage" in uge_labels and node_data["CPUUsage"]:
            cpu_usage = [item[value] for item in node_data["CPUUsage"]]
        
        if "NodePower" in power_labels and node_data["NodePower"]:
            power_usage = [item[value] for item in node_data["NodePower"]]
        
        if "CPU1Temp" in thermal_labels: 
            if node_data["CPU1Temp"]:
                cpu_1_temp = [item[value] for item in node_data["CPU1Temp"]]
            if node_data["CPU2Temp"]:
                cpu_2_temp = [item[value] for item in node_data["CPU2Temp"]]
        if "InletTemp" in thermal_labels:
            if node_data["InletTemp"]:
                inlet_temp = [item[value] for item in node_data["InletTemp"]]
        
        if "CPU1Temp" in thermal_labels or "InletTemp" in thermal_labels:
            if cpu_1_temp:
                temp = cpu_1_temp
            elif cpu_2_temp:
                temp = cpu_2_temp
            elif inlet_temp:
                temp = inlet_temp
            else:
                temp = []

            for index, item in enumerate(temp):
                cpu_inl_temp.append([])
                try:
                    cpu_inl_temp[index].append(cpu_1_temp[index])
                except:
                    cpu_inl_temp[index].append(None)
                try:
                    cpu_inl_temp[index].append(cpu_2_temp[index])
                except:
                    cpu_inl_temp[index].append(None)
                try:
                    cpu_inl_temp[index].append(inlet_temp[index])
                except:
                    cpu_inl_temp[index].append(None)

        if "FAN_1" in thermal_labels:
            if node_data["FAN_1"]:
                fan_1 = [item[value] for item in node_data["FAN_1"]]
            if node_data["FAN_2"]:
                fan_2 = [item[value] for item in node_data["FAN_2"]]
            if node_data["FAN_3"]:
                fan_3 = [item[value] for item in node_data["FAN_3"]]
            if node_data["FAN_4"]:
                fan_4 = [item[value] for item in node_data["FAN_4"]]

            if fan_1:
                fan = fan_1
            elif fan_2:
                fan = fan_2
            elif fan_3:
                fan = fan_3
            elif fan_4:
                fan = fan_4
            else:
                fan = []

            for index, item in enumerate(fan):
                fan_speed.append([])
                try:
                    fan_speed[index].append(fan_1[index])
                except:
                    fan_speed[index].append(None)
                try:
                    fan_speed[index].append(fan_2[index])
                except:
                    fan_speed[index].append(None)
                try:
                    fan_speed[index].append(fan_3[index])
                except:
                    fan_speed[index].append(None)
                try:
                    fan_speed[index].append(fan_4[index])
                except:
                    fan_speed[index].append(None)

        if node_data["JobList"]:
            for item in node_data["JobList"]:
                # Aggregate the value with the same time
                this_job_list = [jobstr[1:-1] for jobstr in item["distinct"][1:-1].split(", ")]
                job_list_temp += this_job_list
                if item["time"] not in db_time_list:
                    db_time_list.append(item["time"])
                    job_list_dict[item["time"]] = this_job_list
                else:
                    for job in this_job_list:
                        if job and job not in job_list_dict[item["time"]]:
                            job_list_dict[item["time"]].append(job)
        
        # Interpolate
        for i, t in enumerate(time_list):
            if i == 0:
                if t not in job_list_dict:
                    this_job_list = []
                else:
                    this_job_list = job_list_dict[t]
            else:
                if t in job_list_dict:
                    this_job_list = job_list_dict[t]
                else:
                    this_job_list = job_list[i-1]
            job_list.append(this_job_list)

        job_set = list(set(job_list_temp))
        
        json_data = {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "cpu_inl_temp": cpu_inl_temp,
            "job_list": job_list,
            "job_set": job_set
        }

    except:
        logging.error(f"Failed to process data of node: {node}")
    return json_data