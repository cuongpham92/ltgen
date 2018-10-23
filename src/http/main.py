#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External import
import threading
import random
from time import sleep
import sys

# Internal import
import file_operations, time_process, timetable_process, user_process, http_actions

# Global variables
global messages, users, livestr_site_list, intranet_http_site_list, intranet_https_site_list, tapas_dir
HOME_DIR = "/home/client/trf-gen-s2"
INTRANET_TIMETABLE_FILE = ""
LIVESTR_TIMETABLE_FILE = ""
NUM_CXN = 0
ACT_TYPE = ""
RATIO_HTTPS = 0.25   # The percentage of HTTPS connection over total of HTTPS+HTTP

# Parse input arguments
DOCKER_MODE = int(sys.argv[1])
ACT_TYPE = sys.argv[2]
try:
    NUM_CXN = int(sys.argv[3])
except ValueError:
    if ACT_TYPE == "intranet":
        INTRANET_TIMETABLE_FILE = sys.argv[3]
    if ACT_TYPE == "livestream":
        LIVESTR_TIMETABLE_FILE = sys.argv[3]

def init():
    read_configuration()
    print("Simulation configured")
    return

def read_configuration():
    global messages, users, livestr_site_list, intranet_http_site_list, intranet_https_site_list, tapas_dir
    if DOCKER_MODE == 1:
        intranet_http_site_list = file_operations.read_file("/src/http_websites.txt")
        intranet_https_site_list = file_operations.read_file("/src/https_websites.txt")
        livestr_site_list = file_operations.read_file("/src/livestr.txt")
        tapas_dir = "/src"
    else:
        intranet_http_site_list = file_operations.read_file("{0}/src/http/http_websites.txt".format(HOME_DIR))
        intranet_https_site_list = file_operations.read_file("{0}/src/http/https_websites.txt".format(HOME_DIR))
        livestr_site_list = file_operations.read_file("{0}/src/http/livestr.txt".format(HOME_DIR))
        tapas_dir = "{0}/src/http".format(HOME_DIR)
    return

# Call generate_random_running_time function from time_process
def get_running_time(timetable):
    # List of running time
    running_time_list = []
    running_time_list_random = []
    # Get the current time
    current_time = time_process.get_current_time()
    print(current_time)
    # Get the corresponding time_interval and numsession from the mail_timetable file
    interval_numsession_dict = timetable_process.get_time_interval(current_time, timetable)
    if interval_numsession_dict == None:
        return
    else:
        running_time_list = time_process.generate_ordered_running_time(interval_numsession_dict)
        running_time_list_random = time_process.generate_random_running_time(interval_numsession_dict)

    return running_time_list, running_time_list_random

# Call http function
def intranet():
    count = 0
    count_https = 0
    tmp = ""
    if INTRANET_TIMETABLE_FILE != "":
        running_time_list, running_time_list_random = get_running_time(INTRANET_TIMETABLE_FILE)
        print(running_time_list)
        if (len(running_time_list) == 0):
            print("no time interval matched current time")
            return

        # Calculate http and https connection
        total_cnx = len(running_time_list)
        https_cnx = int(total_cnx * RATIO_HTTPS)
        
        current_time = time_process.get_current_time()
        # If current time is earlier than the interval
        while (not time_process.compare_t2t(current_time, running_time_list[0])):
            sleep(1)
            current_time = time_process.get_current_time()
        
        # If current time is in the interval already, then only excuse connections
        # which are later than the current time
        while True:
            # Get current time
            current_time = time_process.get_current_time()
            #print("current_time:" + current_time)
            # If the current time is out of interval, break
            if (time_process.compare_t2t(current_time, running_time_list[-1])):
                break
            # If current time is in the running_time_list, run
            if current_time in running_time_list and current_time != tmp:
                tmp = current_time
                count += 1
                # Get http or https connection randomly
                if count_https < https_cnx:
                    k = random.randint(0, 1)
                    if k == 0: # HTTP connection
                        #http_actions.read_event("http", intranet_http_site_list, intranet_https_site_list)
                        #http_actions.read_event("http", intranet_http_site_list, intranet_https_site_list)
                        http_actions.read_event("http")
                        http_actions.read_event("http")
                    else: # HTTPS connection
                        http_actions.read_event("https")
                        http_actions.read_event("https")
                        count_https += 1
                else:
                    http_actions.read_event("http")
                    http_actions.read_event("http")
            # If not, sleep one sec and check again
            else:
                sleep(1)
        print(count)
    else:
        for i in range(0, NUM_CXN):
            http_actions.read_event("https")

def livestream():
    count = 0
    tmp = ""
    if LIVESTR_TIMETABLE_FILE != "":
        running_time_list, running_time_list_random = get_running_time(LIVESTR_TIMETABLE_FILE)
        if (len(running_time_list) == 0):
            print("no time interval matched current time")
            return
        
        current_time = time_process.get_current_time()
        # If current time is earlier than the interval
        while (not time_process.compare_t2t(current_time, running_time_list[0])):
            sleep(1)
            current_time = time_process.get_current_time()
        
        # If current time is in the interval already, then only excuse connections
        # which are later than the current time
        while True:
            # Get current time
            current_time = time_process.get_current_time()
            #print("current_time:" + current_time)
            # If the current time is out of interval, break
            if (time_process.compare_t2t(current_time, running_time_list[-1])):
                break
            # If current time is in the running_time_list, run
            if current_time in running_time_list and current_time != tmp:
                tmp = current_time
                count += 1
                http_actions.live_stream(livestr_site_list, tapas_dir)
            # If not, sleep one sec and check again
            else:
                sleep(1)
        print(count)
    else:
        for i in range(0, NUM_CXN):
            http_actions.live_stream(livestr_site_list, tapas_dir)

def main():
    init()
    if ACT_TYPE == "intranet":
        intranet()
    if ACT_TYPE == "livestream":
        livestream()

main()
