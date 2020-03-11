def process_data(json_data: list, measurement: str) -> list:
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #         "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    result = []
    try:
        for data in json_data:
            if measurement == "CPU_Temperature":
                data_point_1 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "CPU1Temp",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["CPU1 Temp"]
                    }
                }
                data_point_2 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "CPU2Temp",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["CPU2 Temp"]
                    }
                }
                result.append(data_point_1)
                result.append(data_point_2)
            # if measurement == "Inlet_Temperature":
            #     data_point = {
            #         "measurement" : "Thermal",
            #         "time": data,
            #         "tags": {
            #             "Sensor": "InletTemp",
            #             "NodeId": data
            #         }, 
            #         "fields": {
            #             "Reading": data
            #         }
            #     }
            # if measurement == "CPU_Usage":
            #     data_point = {
            #         "measurement" : "UGE",
            #         "time": data,
            #         "tags": {
            #             "Sensor": "CPUUsage",
            #             "NodeId": data
            #         }, 
            #         "fields": {
            #             "Reading": data
            #         }
            #     }
            # if measurement == "Memory_Usage":
            #     data_point = {
            #         "measurement" : "UGE",
            #         "time": data,
            #         "tags": {
            #             "Sensor": "MemUsage",
            #             "NodeId": data
            #         }, 
            #         "fields": {
            #             "Reading": data
            #         }
            #     }
            # if measurement == "Fan_Speed":
            #     data_point = {
            #         "measurement" : "Thermal",
            #         "time": data,
            #         "tags": {
            #             "Sensor": "FAN1",
            #             "NodeId": data
            #         }, 
            #         "fields": {
            #             "Reading": data
            #         }
            #     }
            # if measurement == "Node_Power_Usage":
            #     data_point = {
            #         "measurement" : "Power",
            #         "time": data,
            #         "tags": {
            #             "Sensor": "NodePower",
            #             "NodeId": data
            #         }, 
            #         "fields": {
            #             "Reading": data
            #         }
            #     }
    except Exception as err:
        print(err)
    
    return result

