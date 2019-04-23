#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 12:51:14 2019

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

# Open the serial port and when successful, execute the code that follows
with serial.Serial(port=serial_port, baudrate=9600, timeout=1) as ser:
    # Ping
    write_BLE('AT', ser)
    sleep(0.1)
    print(read_BLE(ser))
    
    # Set immediate
    write_BLE('AT+IMME1', ser)
    sleep(0.1)
    # Check results
    print(read_BLE(ser))
    
    # Turn on notifications
    write_BLE('AT+NOTI1', ser)
    sleep(0.1)
    # Check results
    print(read_BLE(ser))
    
    # Activate central mode
    write_BLE('AT+ROLE1', ser)
    sleep(0.1)
    # Check results
    print(read_BLE(ser))
    
    # Activate central mode
    write_BLE('AT+ADDR?', ser)
    sleep(0.1)
    # Check results
    print(read_BLE(ser))
    
    connected = False
    
    while (not connected):
        for x in range(1, 3):
            write_BLE('AT+COND8A98BB47D89', ser)
            sleep(1)
        if 'OK+CONNAOK+CONN' in read_BLE(ser):
            connected = True
           
    if connected:
        for x in range(1, 3):
            write_BLE('Connected', ser)
            sleep(1)
    
    counter = 0
    
    while (connected):
        if '*' in read_BLE(ser):
            counter += 1
        write_BLE('Number: ' + str(counter), ser)
        sleep(1)