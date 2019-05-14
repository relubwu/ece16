#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:38:19 2019

@author: omid, baichuan
"""

import numpy as np
import Hr_basic as hr

h = hr.Hr("ir_data_train.csv", True)

# ---------- Load training data ---------- #
# Load training data
data_range = 250
data_time_tr, data_ir_tr = np.loadtxt("ir_data_train.csv", delimiter=",", skiprows=1, unpack=True)
h.process(data_time_tr[:data_range], data_ir_tr[:data_range])