#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 12:13:14 2019

@author: Baichuan Wu #A15608204
"""

import serial
from time import sleep

serial_port = '/dev/cu.usbserial'

# Read from serial ser and return the string that was read
def read_BLE(ser):
  b_available = ser.in_waiting
  return ser.readline(b_available).decode('utf-8')


# Write the string, command, to serial ser; return nothing
def write_BLE(command, ser):
  ser.write(bytes(command, 'utf-8'))
  # Await
  sleep(0.1)


# Open the serial port and when successful, execute the code that follows
with serial.Serial(port=serial_port, baudrate=9600, timeout=1) as ser:
    # Ask for name
    write_BLE('AT+NAME?', ser)
    print(read_BLE(ser))
    
    # Set name
    write_BLE('AT+NAMEA15608204', ser)
    
    # Check results
    print(read_BLE(ser))