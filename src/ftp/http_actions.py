#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

import time
from time import sleep
import random
try:
    import urllib.request as driver
except ImportError:
    from urllib2 import urlopen as driver
import os
import ssl

#import functions

#import file_operations as fifo
"""
# Function for pick randomly an event
def get_website(link_file):
    website_list = fifo.read_file(link_file)
    return website_list
"""
"""
def read_event(protocol, http_list, https_list):
    num = int(random.gauss(1514, 900))
    k = random.randint(0, 1)
    site = get_link(http_list, https_list, protocol, k)
    if protocol == "https":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        page = driver.urlopen(site, context=ctx).read()
        print(page)
    else:
        try:
            page = driver.urlopen(site).read()
            print(page)
        except urllib.error.HTTPError as err:
            print("Something happened! Error code", err.code)
        except urllib.error.URLError as err:
            print("Some other error happened:", err.reason)
"""

def read_event(ip_server, protocol):
    #site = random.choice(site_list)
    then = time.time() 
    num = int(random.gauss(1514, 900))
    if protocol == "https":
        site = "https://{0}:8081/vip?name={1}".format(ip_server, num)
        print(site)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        page = driver.urlopen(site, context=ctx).read()
    else:
        site = "http://{0}:8080/vip?name={1}".format(ip_server, num)
        print(site)
        page = driver.urlopen(site).read()
    now = time.time()
    print(str(now - then))

def live_stream(site_list, tapas_dir):
    site = random.choice(site_list)
    cmd = "{0}/run_livestr.sh {0}/tapas {1}".format(tapas_dir, site)
    print(cmd)
    os.system(cmd)

"""
def get_link(http_list, https_list, protocol, k):
    site = ""
    num = int(random.gauss(1514, 900))
    if k == 0:
        if protocol == "http":
            site = "http://10.0.1.12:8080/vip?name={0}".format(num)
        if protocol == "https":
            site = "https://10.0.1.12:8081/vip?name={0}".format(num)
    else:
        if protocol == "http":
            site = random.choice(http_list)
        if protocol == "https":
            site = random.choice(https_list)

    print(site)
    return site
"""
