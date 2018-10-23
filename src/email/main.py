#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External import
import random
import time
from time import sleep
import sys

# Internal import
import mail_actions, file_operations, time_process, timetable_process, user_process, rand_funcs

# Global variables
global messages, imap_users, smtp_users

NUM_USER_PER_GROUP = 10
READMAIL_TIMETABLE_FILE = ""
SENDMAIL_TIMETABLE_FILE = ""

ACT_TYPE = ""
IMAP_TRF = 0
SMTP_TRF = 0

IMAP_SERVER = "10.0.1.16"
IMAP_PORT = "993"
SMTP_SERVER = "10.0.1.16"

# Parse input argument
DOCKER_MODE = int(sys.argv[1])
print(DOCKER_MODE)
ACT_TYPE = sys.argv[2]
try:
    NUM_CXN = int(sys.argv[3])
except ValueError:
    if ACT_TYPE == "imap":
        READMAIL_TIMETABLE_FILE = sys.argv[3]
    if ACT_TYPE == "smtp":
        SENDMAIL_TIMETABLE_FILE = sys.argv[3]

def init():
    read_configuration()
    print("Emulation configured")
    return

def read_configuration():
    global messages, imap_users, smtp_users
    if DOCKER_MODE == 1:
        smtp_users = file_operations.read_file("/src/smtp_users.txt")
        imap_users = file_operations.read_file("/src/imap_users.txt")
        messages = file_operations.read_file("/src/messages.txt")
    else:
        smtp_users = file_operations.read_file("smtp_users.txt")
        imap_users = file_operations.read_file("imap_users.txt")
        messages = file_operations.read_file("messages.txt")
    return

# Call generate_random_running_time function from time_process
def get_random_running_time(timetable):
    # List of running time
    running_time_list = []
    # Get the current time
    current_time = time_process.get_current_time()
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
    #return "user1", "user1"


def one_read_email(num_readmail_mean, num_reply_mean):
    username, passwd = get_random_user(imap_users)
    print(username, passwd)
    num_readmail = rand_funcs.float_to_int(rand_funcs.gen_val_by_meanstd(num_readmail_mean, 2))
    num_reply = rand_funcs.float_to_int(rand_funcs.gen_val_by_meanstd(num_reply_mean, 1))
    if num_reply > num_readmail:
        num_reply = num_readmail
    print("num_readmail, num_reply", num_readmail, num_reply)
    mail_actions.read_email(NUM_USER_PER_GROUP, IMAP_SERVER, IMAP_PORT, SMTP_SERVER, imap_users, username, passwd, messages, num_readmail, num_reply)


# Call readmail function
def imap():
    if READMAIL_TIMETABLE_FILE != "":
        running_time_list = get_random_running_time(READMAIL_TIMETABLE_FILE)
        if running_time_list == None:
            print("no time interval matched current time")
            return

        #for running_time in running_time_list:
        #    print(running_time)

        num_cxn = len(running_time_list)
        num_readmail_mean = rand_funcs.float_to_int(num_cxn * 0.5)
        num_reply_mean = rand_funcs.float_to_int(num_readmail_mean * 0.3)

        print("num_conn, num_readmail_mean, num_reply_mean", num_cxn, num_readmail_mean, num_reply_mean)

        for running_time in running_time_list:
            # Get the current time
            current_time = time_process.get_current_time()
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()

            one_read_email(num_readmail_mean, num_reply_mean)
    else:
        num_readmail_mean = rand_funcs.float_to_int(NUM_CXN * 0.5)
        num_reply_mean = rand_funcs.float_to_int(num_readmail_mean * 0.3)

        print("num_conn, num_readmail_mean, num_reply_mean", NUM_CXN, num_readmail_mean, num_reply_mean)
        for i in range(0, NUM_CXN):
            now = time.time()
            one_read_email(num_readmail_mean, num_reply_mean)
            then = time.time()
            print(then - now)


# Function for sending one email
def one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp):
    while True:
        type1 = random.sample(send_type, 1)[0]
        if type1 == "group":
            if num_group_temp > 0:
                num_group_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
        elif type1 == "random":
            if num_rand_temp > 0:
                num_rand_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
        else:
            if num_brc_temp > 0:
                num_brc_temp -= 1
                mail_actions.smtp_gen(SMTP_SERVER, messages, smtp_users, type1, NUM_USER_PER_GROUP)
                break
    return num_group_temp, num_rand_temp, num_brc_temp

# Function of generating smtp traffic by sending a number of emails
def smtp():
    send_type = ["group", "random", "broadcast"]
    if SENDMAIL_TIMETABLE_FILE != "":
        running_time_list = get_random_running_time(SENDMAIL_TIMETABLE_FILE)
        if running_time_list == None:
            print("no time interval matched current time")
            return

        for running_time in running_time_list:
            print(running_time)

        num_cxn = len(running_time_list)

        num_conn_group = rand_funcs.float_to_int(num_cxn*0.6)
        num_conn_rand = rand_funcs.float_to_int(num_cxn*0.3)
        num_conn_brc = rand_funcs.float_to_int(num_cxn*0.1)

        num_group_temp = num_conn_group
        num_rand_temp = num_conn_rand
        num_brc_temp = num_conn_brc

        for running_time in running_time_list:
            # Get the current time
            current_time = time_process.get_current_time()
            while (not time_process.compare_t2t(current_time, running_time)):
                sleep(1)
                current_time = time_process.get_current_time()
            num_group_temp, num_rand_temp, num_brc_temp = one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp)

    else:
        num_conn_group = rand_funcs.float_to_int(NUM_CXN*0.6)
        num_conn_rand = rand_funcs.float_to_int(NUM_CXN*0.3)
        num_conn_brc = rand_funcs.float_to_int(NUM_CXN*0.1)

        num_group_temp = num_conn_group
        num_rand_temp = num_conn_rand
        num_brc_temp = num_conn_brc

        num_try = 0
        for i in range(0, NUM_CXN):
            num_group_temp, num_rand_temp, num_brc_temp = one_send_email(send_type, num_group_temp, num_rand_temp, num_brc_temp)


# Main function
def main():
    init()
    if ACT_TYPE == "imap":
        imap()
    if ACT_TYPE == "smtp":
        smtp()
    
main()
