def read_host_list(racks: str, computers: str, host_pool: list) -> list:
    """
    Read parameters specified by user; generate host IPs; return hosts only in 
    the host pool 
    """
    host_list = []
    rack_list = []
    comp_list = []
    try:
        # Parse racks
        if "-" in racks:
            st_rack = int(racks.split("-")[0])
            ed_rack = int(racks.split("-")[1]) + 1
            for i in range(st_rack, ed_rack):
                rack_list.append(i)
        else:
            raw_racks = racks.split(",")
            for i in raw_racks:
                try:
                    rack_list.append(int(i))
                except:
                    pass
        # Parse computers
        if "-" in computers:
            st_comp = int(computers.split("-")[0])
            ed_comp = int(computers.split("-")[1]) + 1
            for i in range(st_comp, ed_comp):
                comp_list.append(i)
        else:
            raw_comps = computers.split(",")
            for i in raw_comps:
                try:
                    comp_list.append(int(i))
                except:
                    pass
        # Generate IP addr and append it if in host pool
        for r in rack_list:
            for c in comp_list:
                ip = "10.101." + str(r) + "." + str(c)
                if ip not in host_list and ip in host_pool:
                    host_list.append(ip)
    except Exception as err:
        print(err)
    return host_list


def read_metrics(metrics: list) -> dict:
    """
    Map metrics specified by user to labels in influxDB
    """
    labels = {
        "thermal_labels":[],
        "uge_labels": [],
        "power_labels": []
    }
    mapping = {
        "CPU temperature": ["CPU1Temp", "CPU2Temp"],
        "Inlet temperature": ["InletTemp"],
        "Fans speed": ["FAN_1", "FAN_2", "FAN_3", "FAN_4"],
        "Memory usage": ["MemUsage"],
        "CPU usage": ["CPUUsage"],
        "Node Power": ["NodePower"]
    }
    thermal_labels = []
    uge_labels = []
    power_labels = []
    
    try:
        for metric in metrics:
            if metric == "CPU temperature" or metric == "Inlet temperature" \
            or metric == "Fans speed":
                thermal_labels += mapping[metric]
            elif metric == "Memory usage" or metric == "CPUUsage":
                uge_labels += mapping[metric]
            else:
                power_labels += mapping[metric]
        labels.update({
            "thermal_lables":thermal_labels,
            "uge_labels": uge_labels,
            "power_labels": power_labels
        })
    except Exception as err:
        print(err)
    return labels