import json
import requests
from  threading import Thread

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    node_pwr_list = {}

    # Get exec hosts and fetch corresponding power usuage
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    if exec_hosts != None:
        # Power Redfish request
        core_to_threads(exec_hosts, node_pwr_list, session)
        print(node_pwr_list)
    else:
        print("No Executing Host")
        return


    # # Get job list, exechosts, host summary
    # job_list, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    # host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")
    #
    # if job_list != None and host_summary != None:
    #     job_set = get_job_set(job_list)
    #     exechost_list = get_exechosts_ip(exec_hosts)
    #     job_node_match = match_job_node(job_set, host_summary)
    #
    #     # with open("jobnode.json", "wb") as outfile:
    #     #         json.dump(job_node_match, outfile, indent = 4)
    #     # print(job_node_match)
    #     print(len(exechost_list))
    # else:
    #     print(err_info)

# Get exec hosts list of ip addresses
def get_exechosts_ip(exechosts):
    exechost_list = []
    for exechost in exechosts:
        host_ip = get_hostip(exechost.split('.')[0])
        if host_ip != None:
            exechost_list.append(host_ip)
    return exechost_list

# Get job set
def get_job_set(joblist):
    jobset = []
    for job in joblist:
        jobId = job.split('.')[0]
        if jobId not in jobset:
            jobset.append(jobId)

    return jobset

# Build job-node matches
def match_job_node(jobset, exechosts):
    job_node_match = []
    for jobId in jobset:
        jobId_int = int(jobId)
        job_node_dict = {'jobId': jobId_int, 'user': None, 'exechosts':[]}
        for host in exechosts:
            if host['jobList'] and jobId_int == host['jobList'][0]['id']:
                job_node_dict.update({'user': host['jobList'][0]['user']})
                host_ip = get_hostip(host['hostname'].split('.')[0])
                job_node_dict['exechosts'].append(host_ip)
        if len(job_node_dict['exechosts']) != 0:
            job_node_match.append(job_node_dict)
    return job_node_match

# Convert host name to ip address
def get_hostip(hostname):
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None

# Get UGE information
def get_uge_info(conn_time_out, read_time_out, session, type):

    rootUrl = "http://129.118.104.35:8182/"
    if type == "jobs" or type == "users" or type == "exechosts":
        url = rootUrl + type
    elif type == "hostsummary":
        url = rootUrl + "hostsummary/1/500"
    else:
        return None, "UGE API ERROR"

    try:
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()
        return data, str(None)

    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

# Get Power Usuage
def get_powerusage(host, node_pwr_list, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Power/"
        response = session.get(url, verify = False, auth = ('root', 'nivipnut'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        node_pwr_list.update({host: data['PowerControl'][0]['PowerConsumedWatts']})

    except requests.exceptions.RequestException as e:
        print("Request Power Usage Error")
        node_pwr_list.update({host: None})

# Use multi-thread to fetch Power Usuage from each exec host
def core_to_threads(exec_hosts, node_pwr_list, session):
    warnings.filterwarnings('ignore', '.*', UserWarning,'warnings_filtering',)
    try:
        threads = []
        for host in exec_hosts:
            a = Thread(target = get_powerusage, args = (host, node_pwr_list, conn_time_out, read_time_out, session, ))
            threads.append(a)
            a.start()
        for index, thread in enumerate(threads):
            thread.join()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()