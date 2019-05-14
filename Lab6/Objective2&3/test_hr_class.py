#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:38:19 2019

@author: omid, baichuan
"""

import numpy as np
import Hr_basic as hr
import matplotlib.pyplot as plt

h = hr.Hr("ir_data_train.csv", True)

# ---------- Load training data ---------- #
# Load training data
data_range = 500
data_time_tr, data_ir_tr = np.loadtxt("ir_data_train.csv", delimiter=",", skiprows=1, unpack=True)

data_time_tr = data_time_tr[:data_range]
data_ir_tr = data_ir_tr[:data_range]

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

data_time_tr = split(data_time_tr, 5)
data_ir_tr = split(data_ir_tr, 5)

data_time = []
data_ir = []

for i in data_time_tr:
    data_time.append(i)
    
for i in data_ir_tr:
    data_ir.append(i)

result = []

for i in range(4):
    t_hr, hr = h.process(data_time[i], data_ir[i])
    result.append(hr)
plt.figure()
plt.plot(np.linspace(0, 4, 4), result)
plt.xlabel('T(min)')
plt.ylabel('BPM')
plt.title('Average BPM')
plt.show()
# h.process(data_time_tr[:data_range], data_ir_tr[:data_range])