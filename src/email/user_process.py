#! usr/bin/python
# -*- coding: ISO-8859-1 -*-

import random

# Function for getting username and passwd from user text file
def get_username_passwd(user):
    username = user.split(" ")[0]
    passwd = user.split(" ")[1]
    return username, passwd

# Function for deviding users into groups
def divide_users(users, num_user_per_group):
	# Divide users into groups, NUM_USER_PER_GROUP in each
	user_group_dict = {}
	# Counting variable
	i = 1
	# Group number
	group = 1
	for user in users:
		# Add user to group
		user_group_dict[user] = group
		# If the group has less than NUM_USER_PER_GROUP users, then increase i
		if i < num_user_per_group:
			i += 1
		# Else, increase the group number and reset i
		else:
			group += 1
			i = 1

	return user_group_dict

# Function for getting a random user and its group number from list users
def get_random_user(user_group_dict):
	user, group = random.choice(list(user_group_dict.items()))
	return user, group

# Function for getting the corresponding passwd from a user address
def get_passwd_user(user_addr, users):
    user = user_addr.split("@")[0]
    for u in users:
        if user in u:
            ur, ps = get_username_passwd(u)
            break
    return ps

# Function for getting the corresponding email address form from username
def get_emailaddr_user(user, domain):
    return "{0}@{1}".format(user, domain)
