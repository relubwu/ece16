#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 12:13:14 2019

@author: Baichuan Wu #A15608204
"""

# 1. Create a string containing your first name.
name = "Baichuan"

# 2. Encode the string to a byte array
byte_name = name.encode("utf-8")

# 3. Append a non-utf-8 character
byte_name_bad = byte_name + b'\xef'

# 4. Try decode bad byte name
byte_name_bad.decode()

# Got: UnicodeDecodeError

# 5. Create a try-except clause for decoding byte types
def decode(buffer):
    try:
        return buffer.decode()
    except UnicodeDecodeError:
        return ""
    
# 6. Unit test
print(decode(byte_name))
print(decode(byte_name_bad))