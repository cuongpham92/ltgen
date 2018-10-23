#!/usr/python

import numpy
import random
import string

# Generate value with corresponding probability
def gen_val_by_prob(prob_list):
    num = len(prob_list)
    return numpy.random.choice(numpy.arange(0, num), p=prob_list)

# Generate random string with a given length
def gen_rand_str(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Generate random value with mean value and standard deviation value
def gen_val_by_meanstd(mean, std):
    num = random.gauss(mean, std)
    if (num < 0):
        num = 0
    return num

# Round and change float to int number
def float_to_int(val):
    return int(round(val))
