#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

import time
from time import sleep
import random
import urllib
import urllib.request as driver
#import functions

import file_operations as fifo

DOCKER_MODE = 1

# Function for pick randomly an event
def get_website():
    if DOCKER_MODE == 1:
        website_list = fifo.read_file("/src/websites.txt")
    else:
        website_list = fifo.read_file("websites.txt")
    return website_list

def read_event():
    try:
        now = time.time()
        #page = driver.urlopen("http://10.0.1.8/viewcode.html").read()
        #page = driver.urlopen("http://10.0.1.8/union.html").read()
        #page = driver.urlopen("http://10.0.1.8/i.html?a=23\" and \"1\"=\"1\"").read()
        #url = 'http://10.0.1.8/i.html?subcatid=40%20union%20select%20group_concat(column_name)-,2,3,4,5,6%20from%20information_schema.columns%20where%20table_schema=database()—'.encode('ascii', 'ignore').decode('ascii')
        url = 'https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=11&ct=1367693893&rver=6.1.6206.0&wp=MBI&wreply=http:%2F%2Fmail.live.com%2Fdefault.aspx&lc=1033&id=64855&mkt=en-us&cbcxt=mai&snsc=1'.encode('ascii', 'ignore').decode('ascii')
        print(url)
        page = driver.urlopen(url).read()
        #print(page)
        then = time.time()
        print(then - now)
    except urllib.error.HTTPError as err:
        print("Something happened! Error code", err.code)
    except urllib.error.URLError as err:
        print("Some other error happened:", err.reason)
    #except BaseException as err:
    #    print("Some other error happened:", err.reason)


def main():
    for i in range (0, 20):
        print(i)
        time.sleep(3)
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        read_event()
main()
