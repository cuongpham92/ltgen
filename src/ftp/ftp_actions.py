#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

import ftplib
from ftplib import FTP
import os
import random
import shutil
import time

from utilities import rand_funcs

global ftp

def connect(server_addr, username, password):
    is_failed = 0
    global ftp
    # Login credentials
    usr = ""
    pwd = ""
    for i in range(0, 2):
        if i == 0:
            login_val = rand_funcs.gen_val_by_prob([0.9, 0.1])
        if i == 1:
            login_val = rand_funcs.gen_val_by_prob([0.99, 0.01])
        if login_val == 0:
            usr = username
            pwd = password
        else:
            usr = rand_funcs.gen_rand_str(5)
            pwd = rand_funcs.gen_rand_str(10)
        try:
            print(usr, pwd)
            ftp = FTP(server_addr)
            ftp.login(usr, pwd)
            is_failed = 0
            break
        except (ftplib.all_errors) as e:
            print(str(e))
            is_failed = 1
    return is_failed

def get_file(dst):
    dir_list = ftp.nlst()
    if len(dir_list) == 0:
        pass
    else:
        get_all = 0
        rand_num = random.uniform(0, 1)
        if rand_num*rand_num < 0.6:
            get_all = 1
        print(rand_num*rand_num)
        print(get_all)
        if get_all == 0:
            f = random.choice(dir_list)
            # Substract the folder name from file name
            file_write = f.split("/")[-1]
            print(f)
            ftp.retrbinary('RETR ' + f, open(dst + "/" + file_write, 'wb').write)
        else:
            print(len(dir_list))
            for f in dir_list:
                # Substract the folder name from file name
                file_write = f.split("/")[-1]
                print(f)
                ftp.retrbinary('RETR ' + f, open(dst + "/" + file_write, 'wb').write)

def clean_download_dir(dst):
    shutil.rmtree(dst)
    os.makedirs(dst)

def quit_session():
    ftp.quit()
    print("session complete.")

def upload_file(username, src_file):
    # Not working at the moment. 
    # The error related to permission denied of uploading files to server.
    # Need to add more code.
    dir_list = ftp
    dir_list = ftp.nlst()
    for dir1 in dir_list:
        if (username in dir1):
            print(ftp.cwd(dir1))
            break

    with open(src_file, 'r') as contents:
        ftp.storlines('STOR %s' % src_file, contents)

#ip = "ftp.adirectory.pegase"
"""
if connect("10.0.0.9", "user28", "user28") == 0:
    get_file("download")
    #clean_download_dir("download")
    quit_session()
"""
