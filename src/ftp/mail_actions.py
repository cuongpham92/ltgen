#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

# External libs
import smtplib
import imaplib
import ssl
import random
from numpy import random as random_numpy
import email
import socket
import numpy
from email.mime.text import MIMEText
from email.header import Header
import sys
import math

# Internal imports
from utilities import time_process, file_operations, user_process, rand_funcs

DOMAIN = "tsp.com"

# Function for generating mail destination from list of recipients
def generate_mail_addr(recipients):
	whole_dst = ""
	if type(recipients) is list:
		for i,r in enumerate(recipients):
			username, passwd = user_process.get_username_passwd(r)
			if i != len(recipients)-1:
				whole_dst += "{0}@{1}, ".format(username, DOMAIN)
			else:
				whole_dst += "{0}@{1}".format(username, DOMAIN)
	else:
		username, passwd = user_process.get_username_passwd(recipients)
		whole_dst += "{0}@{1}".format(username, DOMAIN)
	
	return whole_dst

# Function for getting a sender and a list recipients
def get_sender_recipients(user_group_dict, act_type):
    # Get sender
    sender, group = user_process.get_random_user(user_group_dict)
    sender_addr = generate_mail_addr(sender)
    recipients = []
    receiver_addr = ""
    # Action type: one-to-one
    if act_type == "random":
        while True:
            receiver, group = user_process.get_random_user(user_group_dict)
            if receiver != sender:
                recipients.append(receiver)
                break

    # Action type: one-to-group
    if act_type == "group":
        for user1, group1 in user_group_dict.items():
            if group1 == group and user1 != sender:
                recipients.append(user1)

    # Action type: one-to-all
    if act_type == "broadcast":
        for user1, group1 in user_group_dict.items():
            if user1 != sender:
                recipients.append(user1)

    receiver_addr = generate_mail_addr(recipients)
    return sender_addr, receiver_addr

# Function for randomly choosing mail activities among three types
def get_mail_activity():
	mail_act = ["group", "random", "broadcast"]

# Function for generating the time - num of sessions timetable
def get_time_session(session_file):
	timetable = file_operations.read_file(session_file)
	time_numsession_dict = {}
	for line in timetable:
		time = line.split(" ")[0]
		numsession = line.split(" ")[-1]
		time_numsession_dict[time] = numsession
	return time_numsession_dict

# Function for getting the time interval from a certain time as input
def get_time_interval(certain_time, time_numsession_dict):
	# Iterate through the time - num of sessions dictionary
	for time_interval, numsession in time_numsession_dict.items():
		# Check to get the coressponding time interval with the current time
		if time_process.compare_interval(certain_time, time_interval):
			return time_interval, numsession

def create_random_message(messages, n):
    mail = ""
    i = 0
    while i<n:
        #j = random.randrange(0,len(messages))
        mail = messages[i]
        i+=1
    return mail

def email_template(sender_addr, receiver_addr, messages):
    subject = MIMEText(create_random_message(messages, 1).encode('utf-8'), 'plain', 'utf-8')
    content = MIMEText(create_random_message(messages, 5).encode('utf-8'), 'plain', 'utf-8')

    message = """From: {0}
To: {1}
Subject: {2}

{3}
    """.format(sender_addr, receiver_addr, subject, content)

    return message

def send_email(smtp_server, message, sender_addr, sender_passwd, receiver_addr):
    try:
        sender_addr = sender_addr.strip()
        receiver_addr = receiver_addr.strip()
        print(sender_addr)
        print(sender_passwd)
        print(receiver_addr)
        s = smtplib.SMTP("{0}:587".format(smtp_server))
        s.starttls()
        s.login(sender_addr, sender_passwd)
        s.sendmail(sender_addr, receiver_addr, message)
        print("Message sent successfully")
        s.quit()
    except smtplib.SMTPException:
            print(smtplib.SMTPException)
            print("Failed to send message")

# Function for sending email
def smtp_gen(smtp_server, messages, users, send_type, group_size):
    user_group_dict = user_process.divide_users(users, group_size)
    sender_addr, receiver_addr = get_sender_recipients(user_group_dict, send_type)
    sender_passwd = user_process.get_passwd_user(sender_addr, users)
    message = email_template(sender_addr, receiver_addr, messages)

    send_email(smtp_server, message, sender_addr, sender_passwd, receiver_addr)

    if send_type != "random":
        reci_addr_list = receiver_addr.split(",")
        res_addr_list = random.sample(reci_addr_list, rand_funcs.float_to_int(len(reci_addr_list)/3))
        for addr in res_addr_list:
            passwd = user_process.get_passwd_user(addr, users)
            send_email(smtp_server, message, addr, passwd, sender_addr)

# Get the first text block of an email body
def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()

# Logging in and reading the lastest email
def read_email(group_size, imap_server, imap_port, smtp_server, users, username, password, messages, num_read_next_mail, num_response):
    # Login mail box
    usrname = ""
    passwd = ""
    # Break signal. If it is correct username and password, then
    # user login and logout
    usrname = ""
    passwd = ""
    for i in range(0, 3):
        login_val = rand_funcs.gen_val_by_prob([0.95, 0.05])
        if login_val != 0:
            usrname = rand_funcs.gen_rand_str(5)
            passwd = rand_funcs.gen_rand_str(10)
        else:
            usrname = username
            passwd = password
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(user_process.get_emailaddr_user(usrname, DOMAIN), passwd)
            mail.list()
            # Connect to inbox
            mail.select("inbox") 
            # Out: list of "folders" aka labels in gmail
            result, data = mail.search(None, "ALL")
             
            ids = data[0] # data is a list
            id_list = ids.split() # ids is a space separated string
            
            # Quit session if num_read_next_mail = 0
            if num_read_next_mail == 0:
                mail.logout()
                break
            
            else:
                # Reading next email and respond
                res_index_list = []
                if num_response > num_read_next_mail:
                    print("Cannot have number of responses bigger than number of mail read")
                    return
                if num_response != 0:
                    res_index_list = random.sample(list(range(0, num_read_next_mail)), num_response)

                for j in range(0, num_read_next_mail):
                    mail_id = 1
                    try:
                        latest_email_id = id_list[-mail_id]
                        # Fetch the email body (RFC822) for the given ID
                        result, data = mail.fetch(latest_email_id, "(RFC822)") 
                        # Here's the body, which is raw text of the whole email,
                        # including headers and alternate payloads
                        raw_email = data[0][1].decode('utf-8') 
                        email_message = email.message_from_string(raw_email)
                        receiver = email_message['From']
                        
                        # Responding.
                        if j in res_index_list:
                            sender_addr = user_process.get_emailaddr_user(usrname, DOMAIN)
                            sender_passwd = user_process.get_passwd_user(sender_addr, users)
                            receiver_addr = receiver
                            print(sender_addr, sender_passwd, receiver_addr)
                            send_email(smtp_server, email_template(sender_addr, receiver_addr, messages), sender_addr, sender_passwd, receiver_addr)
                    except IndexError:
                        print("no email inbox")

                # Logout
                mail.logout()
                del mail
                break

        except socket.error:
            print(socket.error)
        except imaplib.IMAP4.error:
            print("Login failed. Try again.")


