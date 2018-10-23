#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

import time
from datetime import datetime
import random
import math

def get_hour_min(certain_time):
    elements = certain_time.split(":")
    hour = certain_time.split(":")[0]
    minute = certain_time.split(":")[1]
    second = 0
    if len(elements) == 3:
        second = math.ceil(int(float(elements[2])))

    return hour, minute, second

def get_current_time():
    current_time = str(datetime.now().time())
    current_hour, current_min, current_sec = get_hour_min(current_time)
    return "{0}:{1}:{2}".format(current_hour, current_min, current_sec)

def get_current_time_minute():
    current_time = str(datetime.now().time())
    current_hour, current_min, current_sec = get_hour_min(current_time)
    return "{0}:{1}".format(current_hour, current_min)


def hms_to_seconds(t):
    elements = t.split(":")
    h = int(elements[0])
    m = int(elements[1])
    s = 0
    if len(elements) == 3:
        s = math.ceil(int(float(elements[2])))
    return 3600*h + 60*m + s

def compare_t2t(this_time, certain_time):
    if hms_to_seconds(this_time) >= hms_to_seconds(certain_time):
        return True
    return False

def get_time_difference(start_time, end_time):
    return (hms_to_seconds(end_time) - hms_to_seconds(start_time)) 

def compare_interval(this_time, time_interval):
    start_time = time_interval.split("-")[0]
    end_time = time_interval.split("-")[-1]
    if (compare_t2t(this_time, start_time) and not compare_t2t(this_time, end_time)) or (not compare_t2t(this_time, start_time)):
        return True
    return False


def get_start_end_interval(time_interval):     
    start_time = time_interval.split("-")[0]
    end_time = time_interval.split("-")[-1]
    return start_time, end_time  


def interval_to_seconds(time_interval):
    start_time, end_time = get_start_end_interval(time_interval)
    seconds = hms_to_seconds(end_time) - hms_to_seconds(start_time)
    return seconds

def get_next_time_minute(original_time, increment_time):
    original_hour, original_min, original_sec = get_hour_min(original_time)
    new_min = int(original_min) + increment_time
    new_hour = int(original_hour)

    if new_min >= 60:
        while(new_min >= 60):
            new_min -= 60
            new_hour += 1

    new_min_str = str(new_min)
    if new_min == 0:
        new_min_str += "0"
    if new_min < 10:
        new_min_str = "0{0}".format(new_min)

    new_time = "{0}:{1}".format(str(new_hour), new_min_str)

    return new_time


def get_next_time(original_time, increment_time):
    original_hour, original_min, original_sec = get_hour_min(original_time)
    new_sec = int(original_sec) + increment_time
    new_min = int(original_min)
    new_hour = int(original_hour)
    if new_sec >= 60:
        while(new_sec >= 60):
            new_sec -= 60
            new_min += 1

    if new_min >= 60:
        while(new_min >= 60):
            new_min -= 60
            new_hour += 1

    new_sec_str = str(new_sec)
    if new_sec == 0:
        new_sec_str += "0"
    if new_sec < 10:
        new_sec_str = "0{0}".format(new_sec)

    new_min_str = str(new_min)
    if new_min == 0:
        new_min_str += "0"
    if new_min < 10:
        new_min_str = "0{0}".format(new_min)
    new_time = "{0}:{1}:{2}".format(str(new_hour), new_min_str, new_sec_str)
    return new_time

def add_running_time(running_time, running_time_list):
    index = len(running_time_list)
    for i in range(len(running_time_list)):
        if compare_t2t(running_time_list[i], running_time):
            index = i
            break

    running_time_list = running_time_list[:index] + [running_time] + running_time_list[index:]
    return running_time_list

def generate_random_running_time(interval_numsession_dict):
    running_time_list = []
    
    for time_interval, numsession in interval_numsession_dict.items():
        # Get the start time and end time of the interval
        start_hour, start_min, start_sec = get_hour_min(time_interval.split("-")[0])
        end_hour, end_min, end_sec = get_hour_min(time_interval.split("-")[1])
        
        # If the start time and end time are at the same hour,
        # get randomly "numsession" numbers in the interval
        time_difference = get_time_difference(time_interval.split("-")[0], time_interval.split("-")[1])
        rand_time_list = random.sample(range(1, time_difference), int(numsession))
        
        for time in rand_time_list:
            running_time = get_next_time(time_interval.split("-")[0], time)
            running_time_list = add_running_time(running_time, running_time_list)

    return running_time_list
