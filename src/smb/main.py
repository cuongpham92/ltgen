#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External import
import random
from time import sleep
import sys
import time

# Internal import
import file_operations, time_process, timetable_process, ftp_actions, user_process

# Global variables
global messages, users

FTP_TIMETABLE_FILE = ""
NUM_CON = 0
FTP_SERVER = "10.0.0.12"

DOCKER_MODE = int(sys.argv[1])
download_dir = sys.argv[2]
try:
    NUM_CON = int(sys.argv[3])
except ValueError:
    FTP_TIMETABLE_FILE = sys.argv[3]

def init():
    read_configuration()
    print("Simulation configured")
    return

def read_configuration():
    global messages, users, dwld_dir
    if DOCKER_MODE == 1:
    	users = file_operations.read_file("/src/users.txt")
    else:
    	users = file_operations.read_file("users.txt")
    return

# Call generate_random_running_time function from time_process
def get_random_running_time(timetable):
    # List of running time
    running_time_list = []
    # Get the current time
    current_time = time_process.get_current_time()
    print(current_time)
    # Get the corresponding time_interval and numsession from the mail_timetable file
    interval_numsession_dict = timetable_process.get_time_interval(current_time, timetable)
    if interval_numsession_dict == None:
        return
    else:
        running_time_list = time_process.generate_random_running_time(interval_numsession_dict)

    return running_time_list

# Choose a random user, and get username and password
def get_random_user(user_list):
    user = random.choice(user_list)
    username, passwd = user_process.get_username_passwd(user)
    return username, passwd

# Call ftp function
def ftp():
    if FTP_TIMETABLE_FILE != "":
        running_time_list = get_random_running_time(FTP_TIMETABLE_FILE)
        if running_time_list == None:
            print("no time interval matched current time")
            return
        
        print(running_time_list)
        for running_time in running_time_list:
            # Get the current time
            current_time = time_process.get_current_time()
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()

            # Get a random  from the first three ones in users list
            # The new created users (for some reason) cannot login ftp server yet
            username, passwd = get_random_user(users)
            print(username, passwd)
            if ftp_actions.connect(FTP_SERVER, username, passwd) == 0:
                ftp_actions.get_file(download_dir)
                ftp_actions.clean_download_dir(download_dir)
                ftp_actions.quit_session()
    else:
        for i in range(0, NUM_CON):
            now = time.time()
            username, passwd = get_random_user(users)
            if ftp_actions.connect(FTP_SERVER, username, passwd) == 0:
                ftp_actions.get_file(download_dir)
                ftp_actions.clean_download_dir(download_dir)
                ftp_actions.quit_session()
            then = time.time()
            print(then - now)

# Main function
def main():
    init()
    ftp()
    
main()
