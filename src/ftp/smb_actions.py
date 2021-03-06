#! usr/bin/python
# -*- coding: ISO-8859-1 -*-
import sys
import os
import random
import shutil
import time
from smb.SMBConnection import SMBConnection
from smb import smb_structs
from io import BytesIO

from utilities import rand_funcs

PATH = "/"
PATTERN = "*"

login_status = 0

def connect(server_addr, username, password):
    smb_structs.SUPPORT_SMB2 = True
    remote_name = "smbserver"
    conn = SMBConnection(username, password, username, remote_name, use_ntlm_v2 = True)
    try:
        conn.connect(server_addr, 445) #139=NetBIOS / 445=TCP
    except Exception as e:
        print(e)

    return conn

def login_normal(server_addr, username, password):
    conn = connect(server_addr, username, password)

# Connect to SMB server
def login(server_addr, username, password):
    global login_status
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

        conn = connect(server_addr, usr, pwd)
    
        if usr == username and pwd == password:
            login_status = 1
            break
        else:
            login_status = 0
        
    print("login: ", login_status)
    return login_status

# Get all remote directories and files from a shared disk, with option
def getRemoteDir(service_name, server_addr, username, password):
    print('getRemoteDir() starts...')
    try:
        conn = connect(server_addr, username, password)
        files = conn.listPath(service_name, PATH, pattern=PATTERN)
        # For printing out file infos
        for f in files:
            print('returning: {}'.format(f.filename))
        return files

    except Exception as e:
        fmt = 'conn.listPath({}, {}, {}) threw {}: {}'
        print(fmt.format(service_name, PATH, pattern, type(e), e))
        #print(type(e))
    finally:
        conn.close()

    return None

# Download one remote file
def download(filename, service_name, server_addr, username, password):
    if login_status == 1:
        conn = connect(server_addr, username, password)
        print('Download = ' + PATH + filename)
        attr = conn.getAttributes(service_name, PATH+filename)
        file_obj = BytesIO()
        file_attributes, filesize = conn.retrieveFile(service_name, PATH+filename, file_obj)
        print(file_attributes, filesize)
        fw = open(filename, 'ab')
        file_obj.seek(0)
        for line in file_obj:
            fw.write(line)
        fw.close()
        conn.close()

# Download remote file
def downloadFiles(service_name, server_addr, username, password, dst):
    conn = connect(server_addr, username, password)
    files = getRemoteDir(service_name, server_addr, username, password)
    print(files)
    files.pop(0)
    files.pop(0)
    for f in files:
        print(f.filename)

    get_all = 0
    rand_num = random.uniform(0, 1)
    if rand_num*rand_num < 0.6:
        get_all = 1
    print(rand_num*rand_num)
    print("get all", get_all)
    if get_all == 0:
        f = random.choice(files)
        filename = f.filename
        print("-------", filename)
        if conn:
            print('Download = ' + PATH + filename)
            attr = conn.getAttributes(service_name, PATH+filename)
            file_obj = BytesIO()
            file_attributes, filesize = conn.retrieveFile(service_name, PATH+filename, file_obj)
            print(file_attributes, filesize)
            fw = open(dst + "/" + filename, 'ab')
            file_obj.seek(0)
            for line in file_obj:
                fw.write(line)
            fw.close()
            conn.close()
       
    else:
        if conn:
            for f in files:
                #download(conn, f.filename, service_name)
                print('Download = ' + PATH + f.filename)
                attr = conn.getAttributes(service_name, PATH+f.filename)
                file_obj = BytesIO()
                file_attributes, filesize = conn.retrieveFile(service_name, PATH+f.filename, file_obj)
                print(file_attributes, filesize)
                fw = open(dst + "/" + f.filename, 'ab')
                file_obj.seek(0)
                for line in file_obj:
                    fw.write(line)
                fw.close()

        print('Download finished')
        conn.close()

# Upload a file
def uploadFile(filename, service_name, server_addr, username, password):
    if login_status == 1:
        conn = connect(server_addr, username, password)
        print('Upload = ' + PATH + filename)
        print('Size = %.1f kB' % (os.path.getsize(filename) / 1024.0))
        print('Start upload')
        with open(filename, 'rb') as file_obj:
          filesize = conn.storeFile(service_name, PATH+filename, file_obj)
        print('Upload finished')
        conn.close()

# Delete remote file
def deleteFile(filename, service_name, server_addr, username, password):
    if login_status == 1:
        conn = connect(server_addr, username, password)
        conn.deleteFiles(service_name, PATH+filename)
        print('Remotefile ' + PATH + filename + ' deleted')
        conn.close()

#getRemoteDir("group9", "10.0.1.4", "smbuser100", "smbuser100")
#download("service.yaml", "group0")
"""
start = int(sys.argv[1])
for i in range(start, 101):
    username = "{0}{1}".format("smbuser", i)
    passwd = username
    group = "{0}{1}".format("group",int(i/10))
    if i%10 == 0:
        group = "{0}{1}".format("group", int(i/10)-1)

    print(username, passwd, group)
    #abc = connect("10.0.1.4", username, passwd)
    downloadFiles(group, "10.0.1.4", username, passwd, "download")
    time.sleep(2)
"""
#uploadFile("smb_timetable.txt", "group0")
#deleteFile("smb_timetable.txt", "group0")

