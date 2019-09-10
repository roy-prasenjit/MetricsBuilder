import json
import time
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

    # hostList = []
    # with open('/home/bmc_iplist.txt', 'r') as bmc_file:
    #     hostList = json.load(bmc_file)
    host = '10.101.1.1'
    conn_time_out = 15
    read_time_out = 40
    session = requests.Session()

    taskList = []
    checkList = ['BMCHealth', 'SystemHealth', 'Thermal', 'Power']

    # for host in hostList:
    #     for check in checkList:
    #         taskList.append((host, check))

    # Total time for getting BMCHealth status
    # bmc_health_time = serialTasksTime(hostList, checkList[0], session)
    # print("Total time for getting BMCHealth status: "),
    # print(bmc_health_time)

    # # Total time for getting SystemHealth status
    # sys_health_time = serialTasksTime(hostList, checkList[1], session)
    # print("Total time for getting SystemHealth status: "),
    # print(sys_health_time)
    #
    # # Total time for getting Thermal status
    # thermal_time = serialTasksTime(hostList, checkList[2], session)
    # print("Total time for getting Thermal status: "),
    # print(thermal_time)
    #
    # Total time for getting Power status
    # power_time = serialTasksTime(hostList, checkList[3], session)
    # print("Total time for getting Power status: "),
    # print(power_time)

    # bmc_health = get_status(host, 'BMCHealth', conn_time_out, read_time_out, session)
    # with open("BMCHealth.json", "wb") as outfile:
    #         json.dump(bmc_health, outfile, indent = 4)
    # print(json.dumps(bmc_health, indent = 4))

    sys_health = get_status(host, 'SystemHealth', conn_time_out, read_time_out, session)
    with open("SystemHealth.json", "wb") as outfile:
            json.dump(sys_health, outfile, indent = 4)
    # print(json.dumps(sys_health, indent = 4))

    # thermal = get_status(host, 'Thermal', conn_time_out, read_time_out, session)
    # with open("Thermal.json", "wb") as outfile:
    #         json.dump(thermal, outfile, indent = 4)
    # # print(json.dumps(thermal, indent = 4))
    #
    # power = get_status(host, 'Power', conn_time_out, read_time_out, session)
    # with open("Power.json", "wb") as outfile:
    #         json.dump(power, outfile, indent = 4)
    # print(json.dumps(power, indent = 4))
    # print(taskList)

# Serial tasks
# def serialTasksTime(hostList, checkType, session):
#     conn_time_out = 15
#     read_time_out = 40
#     start_time = time.time()
#     for host in hostList:
#         status = get_status(host, checkType, conn_time_out, read_time_out, session)
#         print(json.dumps(status, indent = 4))
#     tot_time = time.time() - start_time
#     return tot_time

def get_status(host, checkType, conn_time_out, read_time_out, session):

    if checkType == 'BMCHealth':
        url = "https://" + host + "/redfish/v1/Managers/iDRAC.Embedded.1"
    elif checkType == 'SystemHealth':
        url = "https://" + host + "/redfish/v1/System/System.Embedded.1"
    elif checkType == 'Thermal':
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Thermal/"
    elif checkType == 'Power':
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Power/"
    else:
        print("Check Type Error")
        return -1
    try:
        response = session.get(url, verify = False, auth = ('root', 'nivipnut'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return str(e)

if __name__ == "__main__":
    main()
