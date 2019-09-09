import json
import requests
import time
import datetime
import warnings
import multiprocessing

from influxdb import InfluxDBClient
from threading import Thread

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    # List of hard coded IP addresses of iDracs bmc_iplist.txt
    hostList = []
    with open('./scripts/bmc_iplist2.txt', 'r') as bmc_file:
        hostList = json.load(bmc_file)
    # print(hostList)

    # Session object allows to persist certain parameters across requests, it
    # also persists cookies across all requests made from the Session instance
    session = requests.Session()

    # For M number of hosts with N checks/metrics per host will have MxN tasks
    taskList = []

    # The following is the list of high level checks. i.e. some checks will be
    # divided into sub-checks.
    # Also note that 'HPCJob' check is not part of iDRAC rather it uses Univa
    # Grid Engin(UGE) REST API to enquire the job related metrics running in HPC
    checkList = ['BMCHealth', 'SystemHealth', 'HPCJob', 'Thermal', 'Power']

    # Each check is combined with each host. taskList is a list of sublists of
    # host and check
    startTime = time.time()
    for check in checkList:
        # As HPCJob check is not part of iDRAC so it will be considered as
        # single task
        if check == 'HPCJob':
            taskList.append([hostList, check])
            continue
        for host in hostList:
            taskList.append([host, check])

    # print(taskList)
    launch(taskList, session, startTime, hostList)

def launch(taskList, session, startTime, hostList):
    # datetime.timedelta, a duartion expressing the difference between two date,
    # time, or datetime instances to microsecond resolution
    ts = datetime.datetime.now() + datetime.timedelta(seconds=10)
    ts = ts.isoformat()

    # The taskList and session object is passed to the following function which
    # returns list of hosts monitoring data and errors
    objList, errorList = parallelizeTasks(taskList, session)


# The following function accepts taskList as input_data and session objects.
# This function creats a pool of "cores" and divide the workload among cores
# nearly even. In our case, we have 467 iDracs and power check. On 8-core
# machine, first 7 cores will have 58 tasks each and last one will have 61.
def parallelizeTasks(input_data, session):
    # The warnings filter controls whether warnings are ignored, displayed, or
    # turned into errors(raising an exception)
    warnings.filterwarnings('ignore', '.*', UserWarning, 'warnings_filtering', )
    node_error_list = []
    node_json_list = []
    try:
        tasks = len(input_data)
        if( tasks == 0):
            print( "There is no task for monitoring!\n")
            return [], []

        # Initialize pool of cores
        cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(cores)

        if( tasks < cores ):
            cores = tasks

        # Build job list
        jobs = []

        tasks_per_core = tasks // cores
        surplus_tasks = tasks % cores
        # print(f"Tasks per core: {tasks_per_core}")
        # print(f"Surplus task: {surplus_tasks}")

        increment = 1
        for p in range(cores):
            if( surplus_tasks != 0 and p == (cores - 1) ):
                jobs.insert(p, input_data[p * tasks_per_core: ])
            else:
                jobs.insert(p, input_data[p * tasks_per_core: increment * tasks_per_core])
                increment += 1

        # # Print tasks on each core
        # for p in range(cores):
        #     print(jobs[p])

        print(f"Monitoring {tasks} tasks using {cores}cores...")


        # Run parallel jobs across all the cores by calling core_to_threads
        results = [pool.apply_async( core_to_threads, args = (j, session,) ) for j in jobs]

        # Process results
        for result in results:
            (node_data, node_error) = result.get()
            node_json_list += node_data
            node_error_list += node_error
        pool.close()
        pool.join()

        return node_json_list, node_error_list
    except Exception as e:
        node_error_list.append(e)
        return node_json_list, node_error_list

def core_to_threads(input_data, session):
    warning.filterwarnings('ignore', '.*', UserWarning, 'warnings_filtering', )
    try:
        error_list = []
        json_node_list = []
        threads = []
        thread_id = 0

        # input_data is like this [['10.101.1.2', 'Thermal'], ['10.101.1.3', 'Thermal']]
        # host_info is like this ['10.101.1.2', 'Thermal']
        for host_info in input_data:
            host = host_info[0]
            checkType = host_info[1]

            a = Thread(target = getNodesData, args = (host, checkType, json_node_list, error_list, session, ))
            threads.append(a)
            threads[thread_id].start()
            thread_id += 1

        for index in range(0, thread_id):
            threads[index].join()

        return json_node_list, error_list

    except Exception as e:
        return None, None

# getNodesData is called by core_to_threads(). This function performs the following
# three steps:
# 1) get Redfish check/metric according to checkType passed
# 2) Retry THREE times in case of failure
# 3) Build metric(s)
def getNodesData(host, checkType, json_node_list, error_list, session):
    error = ""
    # Based on the experience, iDRAC G13 takes 3 to 5 seconds to process a Redfish API
    # call so in order to monitoring more responsive, initial timeout is set to 6 seconds
    conn_time_out = 15
    read_time_out = 40
    # Total retry times is retry_time + 1
    retry_times = 2

    # Fetch the monitoring data based on check type

    ##############################
    # Process "Power" check type #
    ##############################
    if checkType == "Power":
        # Starting time of check processing
        start_time = time.time()
        # retry = 0 indicates first time call
        retry = 0
        # Get power usage by passing host, timeout, and session objects
        power_usage, pwr_thresholds, error = get_powerusage(host, conn_time_out, read_time_out, session)
        # Total processing time
        tot_time = time.time() - start_time

        while (error != "None") and (retry < retry_times):
            power_usage, pwr_thresholds, error = get_powerusage(host, conn_time_out, read_time_out, session)
            tot_time = time.time() - start_time
            retry += 1

        if error != "None":
            retry = None

        # Power usage metric is built and result is returned into a dictionary
        mon_data_dict = build_power_usage_metric(power_usage, tot_time, host, pwr_thresholds, retry, error)
        # Monitored data(in dictionary) is appended into global list passed by core_to_threads()
        json_node_list.append(mon_data_dict)
        # error('None' in this case) with host and checktype is appended to  global error list
        error_list.append([host, checkType, error])

    ################################
    # Process "Thermal" check type #
    ################################
    elif checkType == "Thermal":
        start_time = time.time()
        retry = 0

        cpu_temperature, inlet_temp, fan_speed, fan_health, cpu_temp_thresholds, fan_speed_thresholds, inlet_temp_thresholds, inlet_health, error = get_thermal(host, conn_time_out, read_time_out, session)
        tot_time = time.time() - start_time

        while (error != "None") and (retry < retry_times):
            cpu_temperature, inlet_temp, fan_speed, fan_health, cpu_temp_thresholds, fan_speed_thresholds, inlet_temp_thresholds, inlet_health, error = get_thermal(host, conn_time_out, read_time_out, session)
            tot_time = time.time() - start_time
            retry += 1

        if error != "None":
            retry = None

        mon_data_dict = build_cpu_temperature_metric(cpu_temperature, tot_time, host, cpu_temp_thresholds, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_inlet_temperature_metric(inlet_temp, tot_time, host, inlet_temp_thresholds, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_inlethealth_metric(inlet_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_fanspeed_metric(fan_speed, tot_time, host, fan_speed_thresholds, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_fanhealth_metric(fan_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

    ##############################################
    # Process "Host", "CPU", and "Memory" checks #
    ##############################################
    elif checkType == "SystemHealth":
        start_time = time.time()
        retry = 0

        host_health, cpu_health, mem_health, host_led_indicator, host_power_state, error = get_system_health(host, conn_time_out, read_time_out, session)
        tot_time = time.time() - start_time

        while (error != "None") and (retry < retry_times):
            host_health, cpu_health, mem_health, host_led_indicator, host_power_state, error = get_system_health(host, conn_time_out, read_time_out, session)
            tot_time = time.time() - start_time
            retry += 1

        if error != "None":
            retry = None

        mon_data_dict = build_host_health_metric(host_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_cpu_health_metric(cpu_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_mem_health_metric(mem_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_led_indicator_metric(host_led_indicator, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

        mon_data_dict = build_power_state_metric(host_power_state, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

    ##############################################
    # Process "BMC" health check #
    ##############################################
    elif checkType == "BMCHealth":
        start_time = time.time()
        retry = 0

        bmc_health, error = get_bmc_health(host, conn_time_out, read_time_out, session)
        tot_time = time.time() - start_time

        while(error != "None") and (retry < retry_times):
            bmc_health, error = get_bmc_health(host, conn_time_out, read_time_out, session)
            tot_time = time.time() - start_time
            retry += 1

        if error != "None":
            retry = None

        mon_data_dict = build_bmc_health_metric(bmc_health, tot_time, host, retry, error)
        json_node_list.append(mon_data_dict)
        error_list.append([host, checkType, error])

    #######################################################################
    # Process "HPCJob" check type, This metric is not available via iDRAC #
    #######################################################################
    elif checkType == "HPCJob":
        job_data, error = get_hpcjob_data(conn_time_out, read_time_out, session)
        if error == "None":
            timeStamp = datetime.datetime.now().isoformat()
            build_jobs_metric(job_data, error, json_node_list, error_list, checkType, timeStamp)

############################
# Get Power Usage function #
############################
def get_powerusage(host, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Power/"

        # Disable SSL certificate verfication by setting verify = False
        response = session.get(url, verify = False, auth = ('root', 'nivipnut'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()

        data = response.json()

        pwr_thresholds = {}

        pwr_thresholds.update({'PowerCapacityWatts': data['PowerControl'][0]['PowerCapacityWatts']})
        pwr_thresholds.update({'PowerRequestedWatts': data['PowerControl'][0]['PowerRequestedWatts']})
        pwr_thresholds.update({'PowerAvailableWatts': data['PowerControl'][0]['PowerAvailableWatts']})

        return data['PowerControl'][0]['PowerConsumedWatts'], pwr_thresholds, str(None)
    except requests.exceptions.RequestException as e:
        return None, None, str(e)

########################
# Get Thermal function #
########################
def get_thermal(host, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Thermal/"

        response = session.get(url, verify = False, auth = ('root', 'niviput'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        cpu_temp = {}
        inlet_temp = {}
        fan_speed = {}
        fan_health = {}

        cpu_temp_thresholds = {}
        fan_speed_thresholds = {}
        inlet_temp_thresholds = {}
        temps = data['Temperatures@odata.count']
        if temps > 2:
            temps -= 1
        for in range(temps):
            cpu_temp.update({data['Temperatures'][i]['Name']: data['Temperatures'][i]['ReadingCelsius']})

        if any('LowerThresholdCritical' in d for d in data['Temperatures']):
            cpu_temp_thresholds.update({'cpuLowerThresholdCritical': data['Temperatures'][0]['LowerThresholdCritical']})
        else:
            cpu_temp_thresholds.update({'cpuLowerThresholdCritical': None})

        if any('LowerThresholdNonCritical' in d for d in data['Temperatures']):
            cpu_temp_thresholds.update({'cpuLowerThresholdNonCritical': data['Temperatures'][0]['LowerThresholdNonCritical']})
        else:
            cpu_temp_thresholds.update({'cpuLowerThresholdNonCritical': None})

        if any('UpperThresholdCritical' in d for d in data['Temperatures']):
            cpu_temp_thresholds.update({'cpuUpperThresholdCritical': data['Temperatures'][0]['UpperThresholdCritical']})
        else:
            cpu_temp_thresholds.update({'cpuUpperThresholdCritical': None})

        if any('UpperThresholdNonCritical' in d for d in data['Temperatures']):
            cpu_temp_thresholds.update({'cpuUpperThresholdNonCritical': data['Temperatures'][0]['UpperThresholdNonCritical']})
        else:
            cpu_temp_thresholds.update({'cpuUpperThresholdNonCritical': None})

        if (data['Temperatures@odata.count'] > 2):
            inlet_temp.update({data['Temperature'][data['Temperatures@odata.count'] - 1]['Name']: data['Temperatures'][data['Temperatures@odata.count'] - 1]['ReadingCelsius']})
        else:
            inlet_temp.update({'Inlet Temp': None})

        if (data['Temperatures@odata.count'] > 2):
            inlet_health = data['Temperatures'][data['Temperatures@odata.count'] - 1]['Status']['Health']
            inlet_temp_thresholds.update({'inletLowerThresholdCritical': data['Temperatures'][2]['LowerThresholdCritical']})
            inlet_temp_thresholds.update({'inletLowerThresholdNonCritical': data['Temperatures'][2]['LowerThresholdNonCritical']})
            inlet_temp_thresholds.update({'inletUpperThresholdCritical': data['Temperatures'][2]['UpperThresholdCritical']})
            inlet_temp_thresholds.update({'inletUpperThresholdNonCritical': data['Temperatures'][2]['UpperThresholdNonCritical']})
        else:
            inlet_health = None
            inlet_temp_thresholds.update({'inletLowerThresholdCritical': None})
            inlet_temp_thresholds.update({'inletLowerThresholdNonCritical': None})
            inlet_temp_thresholds.update({'inletUpperThresholdCritical': None})
            inlet_temp_thresholds.update({'inletUpperThresholdNonCritical': None})

        for i in range(data['Fans@odata.count']):
            fan_speed.update({data['Fans'][i]['FanName']: data['Fans'][i]['Reading']})
            fan_health.update({data['Fans'][i]['FanName']: data['Fans'][i]['Status']['Health']})

        if any('LowerThresholdCritical' in d for d in data['Fans']):
            fan_speed_thresholds.update({'fanLowerThresholdCritical': data['Fans'][0]['LowerThresholdCritical']})
        else:
            fan_speed_thresholds.update({'fanLowerThresholdCritical': None})

        if any('LowerThresholdNonCritical' in d for d in data['Fans']):
            fan_speed_thresholds.update({'fanLowerThresholdNonCritical': data['Fans'][0]['LowerThresholdNonCritical']})
        else:
            fan_speed_thresholds.update({'fanLowerThresholdNonCritical': None})

        if any('UpperThresholdCritical' in d for d in data['Fans']):
            fan_speed_thresholds.update({'fanUpperThresholdCritical': data['Fans'][0]['UpperThresholdCritical']})
        else:
            fan_speed_thresholds.update({'fanUpperThresholdCritical': None})

        if any('UpperThresholdNonCritical' in d for d in data['Fans']):
            fan_speed_thresholds.update({'fanUpperThresholdNonCritical': data['Fans'][0]['UpperThresholdNonCritical']})
        else:
            fan_speed_thresholds.update({'fanUpperThresholdNonCritical': None})

        return cpu_temp, inlet_temp, fan_speed, fan_health, cpu_temp_thresholds, fan_speed_thresholds, inlet_temp_thresholds, inlet_health, str(None)
    except requests.exceptions.RequestException as e:
        return None, None, None, None, None, None, None, None, str(e)

##############################
# Get System Health function #
##############################
def get_system_health(host, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/System/System.Embedded.1"

        response = session.get(url, verify = False, auth = ('root', 'niviput'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        host_health = data['Status']['HealthRollup']
        host_led_indicator = data['IndicatorLED']
        host_power_state = data['PowerState']
        cpu_health = data['ProcessorSummary']['Status']['Health']
        memory_health = data['MemorySummary']['Status']['HealthRollup']

        return host_health, cpu_health, memory_health, host_led_indicator, host_power_state, str(None)
    except requests.exceptions.RequestException as e:
        return None, None, None, None, None, str(e)

###########################
# Get BMC Health function #
###########################
def get_bmc_health(host, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/Managers/iDRAC.Embedded.1"

        response = session.get(url, verify = False, auth = ('root', 'niviput'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        health = data['Status']['Health']
        return health, str(None)
    except requests.exception.RequestException as e:
        return None, str(e)

##############################
# Get Job Scheduler function #
##############################
def get_hpcjob_data(conn_time_out, read_time_out, session):
    try:
        url = "http://129.118.104.35:8182/hostsummary/1/500"

        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        return data, str(None)
    except requests.exceptions.RequestException as e:
        return None, str(e)

############################
# Build Power Usage Metric #
############################
def build_power_usage_metric(power_usage, tot_time, host, pwr_thresholds, retry, error):
    mon_data_dict = {'measurement': 'Node_Power_Usage', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['powerusage_watts'] = power_usage
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()

    if pwr_thresholds != None:
        mon_data_dict['fields']['PowerRequestedWatts'] = pwr_thresholds['PowerRequestedWatts']
        mon_data_dict['fields']['PowerCapacityWatts'] = pwr_thresholds['PowerCapacityWatts']
        mon_data_dict['fields']['PowerAvailableWatts'] = pwr_thresholds['PowerAvailableWatts']

    return mon_data_dict

################################
# Build CPU Temperature Metric #
################################
def build_cpu_temperature_metric(cpu_temperature, tot_time, host, cpu_temp_thresholds, retry, error):
    mon_data_dict = {'measurement': 'CPU_Temperature', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()

    if cpu_temperature != None:
        cpukeys = cpu_temperature.keys()
        cpuvals = cpu_temperature.values()
        for (k, v) in zip(cpukeys, cpuvals):
            mon_data_dict['fields'][k] = v
    else:
        mon_data_dict['fields']['CPUTemp'] = None

    if cpu_temp_thresholds != None:
        mon_data_dict['fields']['cpuLowerThresholdCritical'] = cpu_temp_thresholds['cpuLowerThresholdCritical']
        mon_data_dict['fields']['cpuLowerThresholdNonCritical'] = cpu_temp_thresholds['cpuLowerThresholdNonCritical']
        mon_data_dict['fields']['cpuUpperThresholdCritical'] = cpu_temp_thresholds['cpuUpperThresholdCritical']
        mon_data_dict['fields']['cpuUpperThresholdNonCritical'] = cpu_temp_thresholds['cpuUpperThresholdNonCritical']

    return mon_data_dict

##################################
# Build Inlet Temperature Metric #
##################################
def build_inlet_temperature_metric(inlet_temp, tot_time, host, inlet_temp_thresholds, retry, error):
    mon_data_dict = {'measurement': 'Inlet_Temperature', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()

    if inlet_temp != None:
        inletkeys = inlet_temp.keys()
        inletvals = inlet_temp.values()
        for (k, v) in zip(inletkeys, inletvals):
            mon_data_dict['fields'][k] = v
    else:
        mon_data_dict['fields']['InletTemp'] = None

    if inlet_temp_thresholds != None:
        mon_data_dict['fields']['inletLowerThresholdCritical'] = inlet_temp_thresholds['inletLowerThresholdCritical']
        mon_data_dict['fields']['inletLowerThresholdNonCritical'] = inlet_temp_thresholds['inletLowerThresholdNonCritical']
        mon_data_dict['fields']['inletUpperThresholdCritical'] = inlet_temp_thresholds['inletUpperThresholdCritical']
        mon_data_dict['fields']['inletUpperThresholdNonCritical'] = inlet_temp_thresholds['inletUpperThresholdNonCritical']

    return mon_data_dict

#############################
# Build Inlet Health Metric #
#############################
def build_inlethealth_metric(inlet_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Inlet_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['inlet_health_status'] = inlet_health
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

##########################
# Build Fan Speed Metric #
##########################
def build_fanspeed_metric(fan_speed, tot_time, host, fan_speed_thresholds, retry, error):
    mon_data_dict = {'measurement': 'Fan_Speed', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()

    if fan_speed != None:
        fankeys = fan_speed.keys()
        fanvals = fan_speed.values()
        for (k, v) in zip(fankeys, fanvals):
            mon_data_dict['fields'][k] = v
    else:
        mon_data_dict['fields']['FanTemp'] = None

    if fan_speed_thresholds != None:
        mon_data_dict['fields']['fanLowerThresholdCritical'] = fan_speed_thresholds['fanLowerThresholdCritical']
        mon_data_dict['fields']['fanLowerThresholdNonCritical'] = fan_speed_thresholds['fanLowerThresholdNonCritical']
        mon_data_dict['fields']['fanUpperThresholdCritical'] = fan_speed_thresholds['fanUpperThresholdCritical']
        mon_data_dict['fields']['fanUpperThresholdNonCritical'] = fan_speed_thresholds['fanUpperThresholdNonCritical']

    return mon_data_dict

###########################
# Build Fan Health Metric #
###########################
def build_fanhealth_metric(fan_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Fan_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()

    if fan_health != None:
        fankeys = fan_health.keys()
        fanvals = fan_health.values()
        for (k, v) in zip(fankeys, fanvals):
            mon_data_dict['fields'][k] = v

    return mon_data_dict

############################
# Build Host Health Metric #
############################
def build_host_health_metric(host_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Node_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['host_health_status'] = host_health
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

############################
# Build CPU Health Metric #
############################
def build_cpu_health_metric(cpu_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'CPU_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['cpu_health_status'] = host_health
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

##############################
# Build Memory Health Metric #
##############################
def build_mem_health_metric(mem_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Memory_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['memory_health_status'] = mem_health
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

###################################
# Build host LED Indicator Metric #
###################################
def build_led_indicator_metric(host_led_indicator, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Node_LED_Indicator', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['led_indicator'] = host_led_indicator
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

#################################
# Build host Power State Metric #
#################################
def build_power_state_metric(host_power_state, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'Node_Power_State', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['power_state'] = host_power_state
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

###########################
# Build BMC Health Metric #
###########################
def build_bmc_health_metric(bmc_health, tot_time, host, retry, error):
    mon_data_dict = {'measurement': 'BMC_Health', 'tags': {'cluster': 'quanah', 'host': host, 'location': 'ESB'}, 'time': None, 'fields': {}}
    mon_data_dict['fields']['GET_processing_time'] = round(tot_time, 2)
    mon_data_dict['fields']['power_state'] = bmc_health
    mon_data_dict['fields']['retry'] = retry
    mon_data_dict['fields']['error'] = error
    mon_data_dict['time'] = datetime.datetime.now().isoformat()
    return mon_data_dict

#####################
# Build JOBS Metric #
#####################
def build_jobs_metric(job_data, error, json_node_list, error_list, checkType, timeStamp):
    jsonJobList = []
    userNames = []
    jobsID = []
    # what are they?
    jl = {}
    nr = []

    for hostinfo in job_data:
        node = get_hostip(hostinfo['hostname'].split('.')[0])
        jobLoad( hostinfo, node, json_node_list, error_list, error_list, checkType, timeStamp)
        for j in hostinfo['jobList']:
            if(j['masterQueue'] == 'MASTER'):
                continue
            jID = 'qu_' + str(j['id'])
            if 'taskId' in j:
                jID = jID + 'A' + j['taskId']
            jobItem = next((job for job in jsonJobList if job["measurement"] == jID), None)
            if jobItem == None:
                jsonJobList.append({'measurement': jID, 'time': timeStamp, 'fields':{'total_nodes': 1, 'app_name': j['name'], 'id': j['id'], 'error': 'None', 'submitTime': j['submitTime'], 'nodes_address': [node + '-1'], 'user': j['user'], 'state': j['state'], 'startTime': j['startTime'], 'CPUCores': 1},'tags': {'location': 'ESB', 'cluster': 'quanah'}})
            else:
                jobItem['fields']['CPUCores'] += 1
                node_addresses = jobItem['fields']['nodes_address']
                exists = 1
                for n in node_addresses:
                    if node in n:
                        exists = 1
                        node_addresses[node_addresses.index(n)] = node + '-' + str(int(n[n.find('-') + 1:]) + 1)

                if exists == 0:
                    jobItem['fields']['nodes_address'].append(node + '-1')
                    jobItem['fields']['total_nodes'] = len(jobItem['fields']['nodes_address'])

            jl.update({jID: jID})
            if j['state'] != 'r':
                if jID not in nr:
                    nr.append(jID)

            if j['user'] not in userNames:
                userNames.append(j['user'])
            if jID not in jobsID:
                jobsID.append(jID)

    for jj in jsonJobList:
        nl = jj['fields']['nodes_address']
        jj['fields']['nodes_address'] = ','.join(str(n) for n in nl)

    if jsonJobList:
        json_node_list += jsonJobList
        json_node_list += build_node_job_mapping(jsonJobList, timeStamp)

    if userNames:
        mon_data_dict = build_currentusers_metric(userNames, timeStamp)
        json_node_list.append(mon_data_dict)
        error_list.append(['cluster', checkType, 'None'])

    if jobsID:
        mon_data_dict = build_currentjobsid_metric(jobsID, timeStamp)
        json_node_list.append(mon_data_dict)
        error_list.append(['cluster', checkType, 'None'])

    client1 = InfluxDBclient(host = 'localhost', port = 8086)
    client1.switch_database('hpcc_monitoring_db')
    node_total_pwr = calc_currentnode_power(client1)
    job_total_pwr, time = calc_currentnode_power(client1)

    if node_total_pwr and job_total_pwr:
        mon_data_dict = build_currentjobsnodespwrusage_metric(node_total_pwr, job_total_pwr, time)
        json_node_list.append(mon_data_dict)
        error_list.append(['cluster_power_usage', checkType, 'None'])

# def get_hostip():
# def jobLoad():
# def build_node_job_mapping():
# def build_currentusers_metric():
# def calc_currentnode_power():

if __name__=="__main__":
    main()
