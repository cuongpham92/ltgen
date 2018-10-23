#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External import
import random
from time import sleep
import sys
import time
import os
import shutil

# Internal import
#import utilities.file_operations, utilities.time_process, utilities.timetable_process, ftp_actions, utilities.user_process, smb_actions
from utilities import file_operations, time_process, timetable_process, user_process, rand_funcs
import http_actions, ftp_actions, smb_actions, mail_actions

# Global variables
global email_messages, imap_users, smtp_users, ftp_users, smb_users, tapas_dir, livestr_site_list


############## HTTP(S) parameters ############
HTTP_SERVER = "10.0.1.12"
INTRANET_TIMETABLE_FILE = ""
LIVESTR_TIMETABLE_FILE = ""
RATIO_HTTPS = 0.25   # The percentage of HTTPS connection over total of HTTPS+HTTP
TAPAS_DIR_LOCAL = "/home/client/trf-gen-s2/src/ftp"
##########################################


############## IMAP parameters ############
READMAIL_TIMETABLE_FILE = ""
IMAP_SERVER = "10.0.1.9"
IMAP_PORT = "993"
##########################################

############## SMTP parameters ############
NUM_USER_PER_GROUP = 10
SMTP_SERVER = "10.0.1.9"
SENDMAIL_TIMETABLE_FILE = ""
##########################################

############## FTP parameters ############
FTP_TIMETABLE_FILE = ""
FTP_SERVER = "10.0.0.7"
##########################################

############## SMB parameters ############
SMB_TIMETABLE_FILE = ""
SMB_SERVER = "10.0.1.3"
##########################################


############## others parameters ############
DOCKER_MODE = int(sys.argv[1])
ACTION = sys.argv[2]
download_dir = sys.argv[3]

try:
    NUM_CONN = int(sys.argv[4])
except ValueError:
    FTP_TIMETABLE_FILE = sys.argv[4]
    SMB_TIMETABLE_FILE = sys.argv[4]
    READMAIL_TIMETABLE_FILE = sys.argv[4]
    SENDMAIL_TIMETABLE_FILE = sys.argv[4]
    INTRANET_TIMETABLE_FILE = sys.argv[4]
    LIVESTR_TIMETABLE_FILE = sys.argv[4]

def init():
    read_configuration()
    print("Simulation configured")
    return
#############################################

###################################################################################
############# FUNCTIONS FOR CONFIGURATION AND SETTING UP PARAMETERS ###############
def read_configuration():
    global email_messages, imap_users, smtp_users, ftp_users, smb_users, tapas_dir, livestr_site_list
    if DOCKER_MODE == 1:
    	intranet_http_site_list = file_operations.read_file("/src/users/http_websites.txt")
    	intranet_https_site_list = file_operations.read_file("/src/users/https_websites.txt")
    	livestr_site_list = file_operations.read_file("/src/users/livestr.txt")
    	tapas_dir = "/src"
    	imap_users = file_operations.read_file("/src/users/imap_users.txt")
    	smtp_users = file_operations.read_file("/src/users/smtp_users.txt")
    	ftp_users = file_operations.read_file("/src/users/ftp_users.txt")
    	smb_users = file_operations.read_file("/src/users/smb_users.txt")
    	email_messages = file_operations.read_file_2("/src/messages.txt")
    else:
    	intranet_http_site_list = file_operations.read_file("users/http_websites.txt")
    	intranet_https_site_list = file_operations.read_file("users/https_websites.txt")
    	livestr_site_list = file_operations.read_file("users/livestr.txt")
    	tapas_dir = TAPAS_DIR_LOCAL
    	imap_users = file_operations.read_file("users/imap_users.txt")
    	smtp_users = file_operations.read_file("users/smtp_users.txt")
    	ftp_users = file_operations.read_file("users/ftp_users.txt")
    	smb_users = file_operations.read_file("users/smb_users.txt")
    	email_messages = file_operations.read_file_2("messages.txt")

    return

# Call generate_random_running_time function from time_process
def get_running_time(timetable):
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
        running_time_list_random = time_process.generate_random_running_time(interval_numsession_dict)
        running_time_list_ordered = time_process.generate_ordered_running_time(interval_numsession_dict)

    return running_time_list_random, running_time_list_ordered

# Choose a random user, and get username and password
def get_random_user(user_list):
    user = random.choice(user_list)
    if user.count(" ") == 1:
        username, passwd = user_process.get_username_passwd(user)
        return username, passwd
    if user.count(" ") == 2:
        username, passwd, group = user_process.get_username_passwd_group(user)
        return username, passwd, group

# Clean local directory
def clean_dir(dst):
    shutil.rmtree(dst)
    os.makedirs(dst)

# Check if the current time is running time
def check_run_time(run_time):
    # Get the current time
    current_time = time_process.get_current_time()
    while (not time_process.compare_t2t(current_time, run_time)):
        sleep(1)
        current_time = time_process.get_current_time()

###################################################################################
###################################################################################


###################################################################################
############################ FUNCTIONS FOR HTTP(S) AGENT #############################
# Call http function
def intranet():
    count = 0
    count_https = 0
    tmp = ""
    if INTRANET_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list_ordered = get_running_time(INTRANET_TIMETABLE_FILE)
        print(running_time_list_random)
        if (len(running_time_list_ordered) == 0):
            print("no time interval matched current time")
            return

        # Calculate http and https connection
        total_cnx = len(running_time_list_random)
        https_cnx = int(total_cnx * RATIO_HTTPS)

        current_time = time_process.get_current_time()
        # If current time is earlier than the interval
        while (not time_process.compare_t2t(current_time, running_time_list_random[0])):
            sleep(1)
            current_time = time_process.get_current_time()

        # If current time is in the interval already, then only excuse connections
        # which are later than the current time
        while True:
            # Get current time
            current_time = time_process.get_current_time()
            #print("current_time:" + current_time)
            # If the current time is out of interval, break
            if (time_process.compare_t2t(current_time, running_time_list_random[-1])):
                break
            # If current time is in the running_time_list_random, run
            if current_time in running_time_list_random and current_time != tmp:
                tmp = current_time
                count += 1
                # Get http or https connection randomly
                if count_https < https_cnx:
                    k = random.randint(0, 1)
                    if k == 0: # HTTP connection
                        #http_actions.read_event("http", intranet_http_site_list, intranet_https_site_list)
                        #http_actions.read_event("http", intranet_http_site_list, intranet_https_site_list)
                        http_actions.read_event(HTTP_SERVER, "http")
                        http_actions.read_event(HTTP_SERVER, "http")
                    else: # HTTPS connection
                        http_actions.read_event(HTTP_SERVER, "https")
                        http_actions.read_event(HTTP_SERVER, "https")
                        count_https += 1
                else:
                    http_actions.read_event(HTTP_SERVER, "http")
                    http_actions.read_event(HTTP_SERVER, "http")
            # If not, sleep one sec and check again
            else:
                sleep(1)
        print(count)
    else:
        for i in range(0, NUM_CONN):
            http_actions.read_event(HTTP_SERVER, "https")


def livestream():
    count = 0
    tmp = ""
    if LIVESTR_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list = get_running_time(LIVESTR_TIMETABLE_FILE)
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
        for i in range(0, NUM_CONN):
            http_actions.live_stream(livestr_site_list, tapas_dir)


###################################################################################
###################################################################################


###################################################################################
############################ FUNCTIONS FOR IMAP AGENT #############################
def one_read_email(num_readmail_mean, num_reply_mean):
    username, passwd = get_random_user(imap_users)
    print(username, passwd)
    num_readmail = rand_funcs.float_to_int(rand_funcs.gen_val_by_meanstd(num_readmail_mean, 2))
    num_reply = rand_funcs.float_to_int(rand_funcs.gen_val_by_meanstd(num_reply_mean, 1))
    if num_reply > num_readmail:
        num_reply = num_readmail
    print("num_readmail, num_reply", num_readmail, num_reply)
    mail_actions.read_email(NUM_USER_PER_GROUP, IMAP_SERVER, IMAP_PORT, SMTP_SERVER, imap_users, username, passwd, email_messages, num_readmail, num_reply)


# Call readmail function
def imap():
    if READMAIL_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list_ordered = get_running_time(READMAIL_TIMETABLE_FILE)
        if running_time_list_random == None:
            print("no time interval matched current time")
            return

        #for running_time in running_time_list_random:
        #    print(running_time)

        num_cxn = len(running_time_list_random)
        num_readmail_mean = rand_funcs.float_to_int(num_cxn * 0.5)
        num_reply_mean = rand_funcs.float_to_int(num_readmail_mean * 0.3)

        print("num_conn, num_readmail_mean, num_reply_mean", num_cxn, num_readmail_mean, num_reply_mean)

        for running_time in running_time_list_random:
            # Get the current time
            current_time = time_process.get_current_time()
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()

            one_read_email(num_readmail_mean, num_reply_mean)
    else:
        num_readmail_mean = rand_funcs.float_to_int(NUM_CONN * 0.5)
        num_reply_mean = rand_funcs.float_to_int(num_readmail_mean * 0.3)

        print("num_conn, num_readmail_mean, num_reply_mean", NUM_CONN, num_readmail_mean, num_reply_mean)
        for i in range(0, NUM_CONN):
            now = time.time()
            one_read_email(num_readmail_mean, num_reply_mean)
            then = time.time()
            print(then - now)

###################################################################################
###################################################################################


###################################################################################
############################ FUNCTIONS FOR SMTP AGENT #############################
# Function for sending one email
def one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp):
    while True:
        type1 = random.sample(send_type, 1)[0]
        if type1 == "group":
            if num_group_temp > 0:
                num_group_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, email_messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
        elif type1 == "random":
            if num_rand_temp > 0:
                num_rand_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, email_messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
        else:
            if num_brc_temp > 0:
                num_brc_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, email_messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
    return num_group_temp, num_rand_temp, num_brc_temp

# Function of generating smtp traffic by sending a number of emails
def smtp():
    send_type = ["group", "random", "broadcast"]
    if SENDMAIL_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list_ordered = get_running_time(SENDMAIL_TIMETABLE_FILE)
        if running_time_list_random == None:
            print("no time interval matched current time")
            return

        for running_time in running_time_list_random:
            print(running_time)

        num_cxn = len(running_time_list_random)

        num_conn_group = rand_funcs.float_to_int(num_cxn*0.6)
        num_conn_rand = rand_funcs.float_to_int(num_cxn*0.3)
        num_conn_brc = rand_funcs.float_to_int(num_cxn*0.1)

        num_group_temp = num_conn_group
        num_rand_temp = num_conn_rand
        num_brc_temp = num_conn_brc

        for running_time in running_time_list_random:
            # Get the current time
            current_time = time_process.get_current_time()
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()
            num_group_temp, num_rand_temp, num_brc_temp = one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp)

    else:
        num_conn_group = rand_funcs.float_to_int(NUM_CONN*0.6)
        num_conn_rand = rand_funcs.float_to_int(NUM_CONN*0.3)
        num_conn_brc = rand_funcs.float_to_int(NUM_CONN*0.1)

        num_group_temp = num_conn_group
        num_rand_temp = num_conn_rand
        num_brc_temp = num_conn_brc

        num_try = 0
        for i in range(0, NUM_CONN):
            num_group_temp, num_rand_temp, num_brc_temp = one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp)

###################################################################################
###################################################################################


###################################################################################
############################# FUNCTIONS FOR FTP AGENT #############################
# Call ftp function
def ftp():
    if FTP_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list_ordered = get_running_time(FTP_TIMETABLE_FILE)
        if running_time_list_random == None:
            print("no time interval matched current time")
            return
        
        for running_time in running_time_list_random:
            # Get the current time
            current_time = time_process.get_current_time()
            print(current_time, running_time)
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()
            
            # Get a random user from the list
            username, passwd = get_random_user(ftp_users)
            print(username, passwd)
            if ftp_actions.connect(FTP_SERVER, username, passwd) == 0:
                ftp_actions.get_file(download_dir)
                clean_dir(download_dir)
                ftp_actions.quit_session()
    else:
        for i in range(0, NUM_CONN):
            now = time.time()
            username, passwd = get_random_user(ftp_users)
            if ftp_actions.connect(FTP_SERVER, username, passwd) == 0:
                ftp_actions.get_file(download_dir)
                clean_dir(download_dir)
                ftp_actions.quit_session()
            then = time.time()
            print(then - now)

###################################################################################
###################################################################################


###################################################################################
############################# FUNCTIONS FOR SMB AGENT #############################
# Call smb functions
def smb():
    if SMB_TIMETABLE_FILE != "":
        running_time_list_random, running_time_list_ordered = get_running_time(SMB_TIMETABLE_FILE)
        if running_time_list_random == None:
            print("no time interval matched current time")
            return

        print(running_time_list_random)

        for running_time in running_time_list_random:
            check_run_time(running_time)

            # Get a random user from the list
            username, passwd, group = get_random_user(smb_users)
            if smb_actions.login(SMB_SERVER, username, passwd) == 1:
                # Get username, password, and group
                print("start downloading")
                smb_actions.downloadFiles(group, SMB_SERVER, username, passwd, download_dir)
                clean_dir(download_dir)
    else:
        for i in range(0, NUM_CONN):
            username, passwd, group = get_random_user(smb_users)
            print(username, passwd, group)
            if smb_actions.login(SMB_SERVER, username, passwd) == 1:
                # Get username, password, and group
                print("start downloading")
                smb_actions.downloadFiles(group, SMB_SERVER, username, passwd, download_dir)
                clean_dir(download_dir)

###################################################################################
###################################################################################


# Main function
def main():
    init()
    if ACTION == "intranet":
        intranet()
    if ACTION == "livestream":
        livestream()
    if ACTION == "imap":
        imap()
    if ACTION == "smtp":
        smtp()
    if ACTION == "ftp":
        ftp()
    if ACTION == "smb":
        smb()
    
main()
