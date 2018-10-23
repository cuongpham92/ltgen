# -*- coding: utf-8 -*-
# Attention: Please use pysmb 1.1.14

from io import StringIO, BytesIO
from smb.SMBConnection import SMBConnection
from smb import smb_structs
from nmb.NetBIOS import NetBIOS
import os
from socket import gethostname

def getBIOSName(remote_smb_ip, timeout=5):
  try:
    bios = NetBIOS()
    srv_name = bios.queryIPForName(remote_smb_ip, timeout=timeout)
  except:
    print('getBIOSName: timeout too short?')
  finally:
    bios.close()
    #print 'bios name = ' + srv_name[0]
    return srv_name[0]

def getServiceName(username, password, my_name, remote_name, remote_ip):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    shares = conn.listShares()
    for s in shares:
      if s.type == 0:  # 0 = DISK_TREE
        return s.name        
    conn.close()
  else:
    return ''

def getRemoteDir(username, password, my_name, remote_name, remote_ip, path, pattern, service_name):
  print('getRemoteDir() starts...')
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    try:
      files = conn.listPath(service_name, path, pattern=pattern)
      #files = conn.listPath(service_name, path)
      print('returning: {}'.format(files.name))
      return files
    except Exception as e:
      fmt = 'conn.listPath({}, {}, {}) threw {}: {}'
      print(fmt.format(service_name, path, pattern, type(e), e))
      #print(type(e))
    finally:
      conn.close()
  else:
    print('connect() failed!')
  return None

def connect(username, password, my_name, remote_name, remote_ip):
  smb_structs.SUPPORT_SMB2 = True
  conn = SMBConnection(username, password, my_name, remote_name, use_ntlm_v2 = True)
  try:
    conn.connect(remote_ip, 445) #139=NetBIOS / 445=TCP
  except Exception as e:
    print(e)
  return conn

def download(username, password, my_name, remote_name, remote_ip, path, filename, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    print('Download = ' + path + filename)
    attr = conn.getAttributes(service_name, path+filename)
    print('Size = %.1f kB' % (attr.file_size / 1024.0))
    print('start download')
    #file_obj = StringIO()
    file_obj = BytesIO()
    file_attributes, filesize = conn.retrieveFile(service_name, path+filename, file_obj)
    print(file_attributes, filesize)
    fw = open(filename, 'ab')
    file_obj.seek(0)
    for line in file_obj:
      fw.write(line)
    fw.close()
    print('download finished')
    conn.close()

def upload(username, password, my_name, remote_name, remote_ip, path, filename, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    print('Upload = ' + path + filename)
    print('Size = %.1f kB' % (os.path.getsize(filename) / 1024.0))
    print('start upload')
    with open(filename, 'r') as file_obj:
      filesize = conn.storeFile(service_name, path+filename, file_obj)
    print('upload finished')
    conn.close()

def delete_remote_file(username, password, my_name, remote_name, remote_ip, path, filename, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    conn.deleteFiles(service_name, path+filename)
    print('Remotefile ' + path + filename + ' deleted')
    conn.close()

def createRemoteDir(username, password, my_name, remote_name, remote_ip, path, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    try:
      conn.createDirectory(service_name, path)
    except Exception as e:
      fmt = 'conn.listPath({}, {}, {}) threw {}: {}'
      print(fmt.format(service_name, path, pattern, type(e), e))
    finally:
      conn.close()
  else:
    print('connect() failed!')
  return None
  
def removeRemoteDir(username, password, my_name, remote_name, remote_ip, path, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    try:
      conn.deleteDirectory(service_name, path)
    except Exception as e:
      fmt = 'conn.listPath({}, {}, {}) threw {}: {}'
      print(fmt.format(service_name, path, pattern, type(e), e))
    finally:
      conn.close()
  else:
    print('connect() failed!')
  return None

def removeRemoteDir(username, password, my_name, remote_name, remote_ip, old_path, new_path, service_name):
  conn = connect(username, password, my_name, remote_name, remote_ip)
  if conn:
    try:
      conn.rename(service_name, old_path, new_path)
    except Exception as e:
      fmt = 'conn.listPath({}, {}, {}) threw {}: {}'
      print(fmt.format(service_name, path, pattern, type(e), e))
    finally:
      conn.close()
  else:
    print('connect() failed!')
  return None

username = 'smbuser1'
password = 'smbuser1'
#my_name = 'iPad'
my_name = gethostname()
remote_ip = '10.0.1.4'
#remote_name = getBIOSName(remote_ip)
#remote_name = 'tm02'
remote_name = 'smbserver'
filename = 'service.yaml'
#filename = 'smb-example.py'
#new_filename = 'smb-example2.py'

path = '/'
#path = '/share/'

#connect(username, password, my_name, remote_name, remote_ip)

#service_name = getServiceName(username, password, my_name, remote_name, remote_ip)
#print(service_name)

#remoteDirs = getRemoteDir(username, password, my_name, remote_name, remote_ip, path, "group0", service_name)

#removeRemoteDir(username, password, my_name, remote_name, remote_ip, path + filename, path + new_filename, service_name)

#removeRemoteDir(username, password, my_name, remote_name, remote_ip, path, service_name)

#createRemoteDir(username, password, my_name, remote_name, remote_ip, path, service_name)

#download(username, password, my_name, remote_name, remote_ip, path, "service.yaml", "group0")

upload(username, password, my_name, remote_name, remote_ip, path, "users.txt", "group0")

#delete_remote_file(username, password, my_name, remote_name, remote_ip, path, filename, service_name)
"""
files = getRemoteDir(username, password, my_name, remote_name, remote_ip, path, "group0", "group0")
if files:
  for file in files:
    print(file.filename)
"""
