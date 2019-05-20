#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:35:15 2019

@author: wubaichuan
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

t, ir, imu  = np.loadtxt("data_save.csv", delimiter=",", skiprows=1, unpack=True)

f, Pxx_spec = signal.welch(imu, 20)

plt.figure()
plt.semilogy(f, np.sqrt(Pxx_spec))
plt.xlabel('frequency [Hz]')
plt.ylabel('Linear spectrum [V RMS]')
plt.show()
