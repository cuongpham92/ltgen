#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External import
import random
from time import sleep
import sys
import os
import math

import utilize.time_process as time_process, utilize.timetable_process as timetable_process, utilize.file_operations as fifo, utilize.rand_funcs as rand_funcs

HTTP_INTRANET_CXN = 12000
HTTP_LIVESTR_CXN = 249457388
SMTP_CXN = 48880
IMAP_CXN = 50000
FTP_CXN = 6700

PRJ_PATH = "/home/client/trf-gen-s2"
RATE_TIMETABLE = "{0}/src/rate_timetable.txt".format(PRJ_PATH)
PTC_WEIGHT = "{0}/src/protocol_weight.txt".format(PRJ_PATH)

DOCKER_WORKERS = "10.0.2.6;10.0.2.15;10.0.2.3"

current_time = time_process.get_current_time()

'''
if len(sys.argv) > 3:
    rate = int(sys.argv[2])
    itv_start = time_process.get_next_time(current_time, 3)
    itv_end = time_process.get_next_time(itv_start, int(sys.argv[1]))
    fifo.write_file(RATE_TIMETABLE, "w+", "{0}-{1} {2}".format(itv_start, itv_end, rate))
'''

#################################################################
# PREPARE INPUTS FOR PROTOCOL AGENTS
#################################################################
'''
# Interval rate file
itv_rate_file = sys.argv[1]
# Traffic partition/percentage file
trf_par_file = sys.argv[2]
'''

# Read protocol weights
weights = fifo.read_file(PTC_WEIGHT)[0].split(" ")

HTTP_WEIGHT = float(weights[0])
IMAP_WEIGHT = float(weights[1])
SMTP_WEIGHT = float(weights[2])
FTP_WEIGHT = float(weights[3])

# Get traffic rate in time interval
def get_trf_rate():
    current_time = time_process.get_current_time()
    interval, rate = timetable_process.get_interval_rate(current_time, RATE_TIMETABLE)
    return interval, rate

# Get number of http connections
# Http traffic are generated from either intranet and livestream activities.
# In the current version, we assume that the number of intranet session is as 
# double as the number of livestream
def get_numcxn_http(http_trf):
    num_livestr_cxn = rand_funcs.float_to_int(http_trf/(5000*HTTP_INTRANET_CXN + HTTP_LIVESTR_CXN))
    num_intranet_cxn = 5000*num_livestr_cxn
    return num_livestr_cxn, num_intranet_cxn


# Get numbers of imap and smtp connections
def get_numcxn_imap(imap_trf):
    # Get number of imap connections, the mean value for number of reading next email, 
    # and the mean value for number of response 
    # Probability of reading next email is 0.5 
    # Probability of sending reply is 0.3 
    # The equation is under the form a*(login_byte) + (a/2)*(read_1email_byte) = imap_trf
    num_conn = rand_funcs.float_to_int(imap_trf/IMAP_CXN)
    return num_conn

def get_numcxn_smtp(smtp_trf, imap_num_conn):
    # Get numbers of each type in sending email: 
    # 60% are discussion group 
    # 30% are random 
    # 10% are broadcast 
    # Each send has size of SMTP_CXN bytes 
    # At the current setting, there has always one reply for broadcast and 
    # discussion group emails 
    # Equation: (0.6*2 + 0.3*1.5 + 0.1*2)*a*10000 = smtp_trf 
    # 80% are discussion, 10% are random and 10% are broadcast
    print("imap_num_conn: " + str(imap_num_conn))
    print(rand_funcs.float_to_int(smtp_trf/(SMTP_CXN*1.85)))
    num_conn = rand_funcs.float_to_int(smtp_trf/(SMTP_CXN*1.85)) - rand_funcs.float_to_int(imap_num_conn*0.15)
    if num_conn < 0:
        num_conn = 0
    return num_conn

# Get number of http connections
def get_numcxn_ftp(ftp_trf):
    num_conn = rand_funcs.float_to_int(ftp_trf/FTP_CXN)
    print("ftp connection: ", str(num_conn))
    return num_conn

# Get number of connection for each agent instance
imap_num_conn = 0
def get_max_num_cxn_ins(agent, itv_sec, total_trf, ptc_weight):
    max_num_cxn_ins = 0
    total_num_cxn = 0
    ptc_trf = int(total_trf*ptc_weight)
    global imap_num_conn 

    if (agent == "imap"):
        total_num_cxn = get_numcxn_imap(ptc_trf)
        imap_num_conn = total_num_cxn
        max_num_cxn_ins = int(itv_sec/4)
    if (agent == "smtp"):
        # Get the correct total number of connections for all instances, 
        # and compare with the maximum connections per instance, in order to calculate
        # the number of instaces needed
        total_num_cxn = get_numcxn_smtp(ptc_trf, imap_num_conn)
        max_num_cxn_ins = int(itv_sec/2)
    if (agent == "ftp"):
        total_num_cxn = get_numcxn_ftp(ptc_trf)
        max_num_cxn_ins = int(itv_sec/12)
    # HTTP traffic are generated from both intranet and livestream activities.
    if (agent == "http-intranet"):
        livestr_num_cxn, intranet_num_cxn = get_numcxn_http(ptc_trf)
        total_num_cxn = intranet_num_cxn   
        max_num_cxn_ins = int(itv_sec/2)
    if (agent == "http-livestr"):
        livestr_num_cxn, intranet_num_cxn = get_numcxn_http(ptc_trf)
        total_num_cxn = livestr_num_cxn   
        max_num_cxn_ins = int(itv_sec/35)

    return total_num_cxn + 1, max_num_cxn_ins

# Calculate number of instances, and number of connections for each instance,
# then write to schedule files
def cal_write_schedule(agent, rate, ptc_weight, interval):
    itv_sec = time_process.interval_to_seconds(interval)
    # Get amount of traffic for the protocol
    total_trf = float(rate) * itv_sec
    # Get the total number of connections and max number of connections per instance
    total_num_cxn, max_num_cxn_ins = get_max_num_cxn_ins(agent, itv_sec, total_trf, ptc_weight)
    print("########{0}#########".format(agent))
    print("total_num_cxn:" + str(total_num_cxn))
    print("max_num_cxn_ins:" + str(max_num_cxn_ins))
    # Calculate the correct number of connections per instance
    if agent == "http-intranet":
        max_num_ins = 1000
        num_ins = int(total_num_cxn / max_num_cxn_ins) + 1
        if (num_ins > max_num_ins):
            num_ins = max_num_ins
        num_cxn_ins = int(total_num_cxn / num_ins)
        if (num_cxn_ins > max_num_cxn_ins):
            num_cxn_ins = max_num_cxn_ins
    else:
        num_ins = int(total_num_cxn / max_num_cxn_ins) + 1
        num_cxn_ins = int(total_num_cxn / num_ins)

    print("num_cxn_ins:" + str(num_cxn_ins))
    print("num_ins: {0}".format(num_ins))

    # Write down the time interval with corresponding number of connections for each agent
    fifo.write_file("{0}/src/input/{1}_timetable.txt".format(PRJ_PATH, agent), "w+", "{0} {1}".format(interval, num_cxn_ins))
    return num_ins

#################################################################
# DEPLOY PROTOCOL AGENTS
#################################################################

def run_cmd(cmd):
    os.system(cmd)

def deploy_agent_cmd(name_agent, num_ins):
    deploy_cmd = ""
    if (num_ins != 0):
        if (name_agent == "http-intranet"):
            deploy_cmd = "docker service create --dns 10.0.1.2 --replicas {0} --mount target=/etc/localtime,source=/etc/localtime,type=bind --mount target=/src/input,source={1}/src/input,type=bind --mount target=/src/main.py,source={1}/src/http/main.py,type=bind --mount target=/src/http_actions.py,source={1}/src/http/http_actions.py,type=bind --name {2}_agent http:v4 python3 /src/main.py 1 intranet /src/input/{2}_timetable.txt".format(num_ins, PRJ_PATH, name_agent)
        if (name_agent == "http-livestr"):
            deploy_cmd = "docker service create --dns 8.8.8.8 --replicas {0} --mount target=/etc/localtime,source=/etc/localtime,type=bind --mount target=/src/livestr.txt,source={1}/src/http/livestr.txt,type=bind --mount target=/src/input,source={1}/src/input,type=bind --name {2}_agent http:v4 python3 /src/main.py 1 livestream /src/input/{2}_timetable.txt".format(num_ins, PRJ_PATH, name_agent)
        if (name_agent == "ftp"):
            deploy_cmd = "docker service create --dns 10.0.1.2 --replicas {0} --mount target=/etc/localtime,source=/etc/localtime,type=bind --mount target=/src/input,source={1}/src/input,type=bind --name {2}_agent {2}:v4 python /src/main.py 1 /src/download /src/input/{2}_timetable.txt".format(num_ins, PRJ_PATH, name_agent)
        if (name_agent == "smtp"):
            deploy_cmd = "docker service create --dns 10.0.1.2 --replicas {0} --mount target=/etc/localtime,source=/etc/localtime,type=bind --mount target=/src/smtp_users.txt,source={1}/src/email/smtp_users.txt,type=bind --mount target=/src/input,source={1}/src/input,type=bind --name {2}_agent email:v2 python /src/main.py 1 smtp /src/input/{2}_timetable.txt".format(num_ins, PRJ_PATH, name_agent)
        if (name_agent == "imap"):
            deploy_cmd = "docker service create --dns 10.0.1.2 --replicas {0} --mount target=/etc/localtime,source=/etc/localtime,type=bind --mount target=/src/imap_users.txt,source={1}/src/email/imap_users.txt,type=bind --mount target=/src/input,source={1}/src/input,type=bind --name {2}_agent email:v2 python /src/main.py 1 imap /src/input/{2}_timetable.txt".format(num_ins, PRJ_PATH, name_agent)
    return deploy_cmd

def rm_agent_cmd(name_agent):
    rm_cmd = "docker service rm {0}_agent".format(name_agent)
    return rm_cmd

def pre_run_agents(interval, rate):
    # Write schedule for agents
    # Http
    http_intranet_num_ins = cal_write_schedule("http-intranet", rate, HTTP_WEIGHT, interval)
    http_livestr_num_ins = cal_write_schedule("http-livestr", rate, HTTP_WEIGHT, interval)
    # Imap
    imap_num_ins = cal_write_schedule("imap", rate, IMAP_WEIGHT, interval)
    # Smtp
    smtp_num_ins = cal_write_schedule("smtp", rate, SMTP_WEIGHT, interval)
    # Ftp
    ftp_num_ins = cal_write_schedule("ftp", rate, FTP_WEIGHT, interval)

    # Copy timetable files to workers
    worker_list = []
    if (DOCKER_WORKERS != ""):
        if (";" in DOCKER_WORKERS):
            worker_list = DOCKER_WORKERS.split(";") 
        else:
            worker_list.append(DOCKER_WORKERS)
    if worker_list:
        for worker in worker_list:
    	    run_cmd("scp {0}/src/input/* {1}:{0}/src/input".format(PRJ_PATH, worker))

    # Run agents
    # Http
    run_cmd(deploy_agent_cmd("http-intranet", http_intranet_num_ins))
    run_cmd(deploy_agent_cmd("http-livestr", http_livestr_num_ins))
    # Imap
    run_cmd(deploy_agent_cmd("imap", imap_num_ins))
    # Smtp
    run_cmd(deploy_agent_cmd("smtp", smtp_num_ins))
    # Ftp
    run_cmd(deploy_agent_cmd("ftp", ftp_num_ins))

def run_agents(interval, rate):
    # Get start time and end time of the interval
    start_time, end_time = time_process.get_start_end_interval(interval)
    print("running agents")
    pre_run_agents(interval, rate)
    # Check when to pass the interval
    while True:
        current_time = time_process.get_current_time()
        # Sleeping to wait for passing the interval
        if (not time_process.compare_t2t(current_time, end_time)):
            sleep(5)
        # If passed, destroy the agents
        else:
            break
    print("killing agents")
    run_cmd(rm_agent_cmd("http-intranet"))
    run_cmd(rm_agent_cmd("http-livestr"))
    run_cmd(rm_agent_cmd("imap"))
    run_cmd(rm_agent_cmd("smtp"))
    run_cmd(rm_agent_cmd("ftp"))

def circle():
    # Get the interval rate dictionary from the RATE_TIMETABLE
    current_time = time_process.get_current_time()
    interval_rate_dict = timetable_process.get_time_interval(current_time, RATE_TIMETABLE)
    print(interval_rate_dict)
    # If there is no match interval, return
    if interval_rate_dict == None:
        return
    # Else, start agents
    for interval, rate in interval_rate_dict.items():
        run_agents(interval, rate)
        # Get start time and end time of the interval
        start_time, end_time = time_process.get_start_end_interval(interval)
        # Get current time
        current_time = time_process.get_current_time()

        # If the current time is in the time interval, then start the agents
        if (time_process.compare_t2t(current_time, start_time) and not time_process.compare_t2t(current_time, end_time)):
            run_agents(interval, rate) 

        # If the current time is not yet in the interval, wait
        if (not time_process.compare_t2t(current_time, start_time)):
            while True:
                sleep(5)
                current_time = time_process.get_current_time()
                # If the current time is in the interval, break the while loop and start the agents
                if time_process.compare_t2t(current_time, start_time):
                    break
            run_agents(interval, rate) 

def main():
    circle()

main()
