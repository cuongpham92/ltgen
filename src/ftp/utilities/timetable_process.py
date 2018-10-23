#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

from . import file_operations, time_process

# Function for generating the time - num_sessions dict from a timetable file
def get_time_session(timetable_file):
	timetable = file_operations.read_file(timetable_file)
	time_numsession_dict = {}
	for line in timetable:
		time = line.split(" ")[0]
		numsession = line.split(" ")[-1]
		time_numsession_dict[time] = numsession
	return time_numsession_dict

# Function for getting the time interval from a certain time as input
def get_time_interval(certain_time, timetable_file):
	time_numsession_dict = get_time_session(timetable_file)
	# Iterate through the time - num of sessions dictionary
	interval_numsession = {}
	numsession = ""
	for t, n in time_numsession_dict.items():
		print(t)
		# Check to get the coressponding time interval with the current time
		if time_process.compare_interval(certain_time, t):
			interval_numsession[t] = n
			#time_interval = t
			#numsession = n
	#return time_interval, numsession
	return interval_numsession

