#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:49:48 2019

@author: wubaichuan
"""

import numpy;

# 1. Create a list called "list_1" containing ints 1-10
list_1 = [x for x in range(1, 11)]
print(list_1)

# 2. Create a list "list_2" containing 11-20 as floats
list_2 = [x for x in numpy.arange(11.0, 21.0, 1.0)]
print(list_2)

# 3. Assign the list ["one", "two", "three"] to the first three elements of the
#   list from list_1. Print list_1. It should look like: ['one', 'two', 
#   'three', 4, 5, 6, 7, 8, 9, 10]
list_1[0:3] = ["one", "two", "three"]
print(list_1)

# 4. Create a tuple containing the words "eleven", "twelve" and "thirteen". 
#   Assign it to the first three elements from 2. Print list_2. It should look 
#   like: ['eleven', 'twelve', 'thirteen', 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 
#   20.0]
list_2[0:3] = ["eleven", "twelve", "thirteen"]
print(list_2)

# 5, 6, 7. Join the lists into a new list 2 different ways
print(list_1 + list_2)      # summation operation
list_1.extend(list_2)       # extend keyword
print(list_1)

# 8. Fixed-width list extending with shifting
def list_shift (base_list, new_data):
    return((base_list + new_data)[-len(base_list):])

print(list_shift([1, 2, 3, 4], [5, 6, 7]))