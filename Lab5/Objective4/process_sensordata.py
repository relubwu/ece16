"""
Receive sensor data from the Arduino
Store it and/or plot it
"""

# Import Python builtin libraries
import os
import numpy as np              # Numpy library
from time import time

# Import custom libraries
from Libraries.Bt import Bt
from Libraries.ListBuffer import ListBuffer
from Libraries.AnimatedFigure import AnimatedFigure
from Libraries.FilterWrapperBasic_complete import Filter

# Set peripheral MAC as well as HM-10 serial port
peripheral_MAC = "D8A98BB47D89"
serial_port = "/dev/cu.usbserial"

# Define if data should be live-plotted
live_plot = True
# Define if data should be written out to file
write_flag = True
# Define if we should read from BLE or from a file
# If False, we read from BLE; if True, we read from file and will use the sampling_period (in seconds)
read_flag = False
sampling_freq = 20  # [Hz]
sampling_period = 1 / sampling_freq     # [s]


# Open the files and read and write if necessary
if write_flag:
    write_filename = "Heartrate_HPF.csv"
    # We use this to make sure the file is saved in the script directory and not the dir Python is executing from
    current_dir = os.path.dirname(os.path.abspath(__file__))
    write_file_path = current_dir + "\\" + write_filename
    write_file = open(write_file_path, 'w')
    write_file.write('{0}, {1} \n'.format("t", "reading"))  # Write the headers for csv file

if read_flag:
    read_filename = "data_save.csv"
    # We use this to make sure the file is saved in the script directory and not the dir Python is executing from
    current_dir = os.path.dirname(os.path.abspath(__file__))
    read_file_path = current_dir + "\\" + read_filename
    if write_flag:
        assert read_file_path != write_file_path, "You can't read and write to the same file"
    read_file = open(read_file_path, 'r')
    read_file.readline()                                    # skip first row, which may contain name of variables


# Sample time
start_time = 0                  # Start time


# Initialize buffers
def initialize_buffers():
    
    # Set shared variables to global so we can modify them
    global data_buffer

    # Create empty buffers to store data
    buffer_length = 50 * 10         # Initial estimate for 30 sec of data at 50Hz, that's probably way too long!
    data_buffer = [[]] * 3          # Two sets of data: time and sensor data
    data_buffer[0] = ListBuffer([], maxlen=buffer_length)       # time data
    data_buffer[1] = ListBuffer([], maxlen=buffer_length)       # sensor data
    data_buffer[2] = ListBuffer([], maxlen=buffer_length)       # filtered sensor data


# Initialization of BLE
def initialize_ble():
    global bt
    # Initialize BLE if we need to
    if not read_flag:
        bt = Bt(ble_peripheral_MAC=peripheral_MAC, serial_port=serial_port)
        bt.ble_setup()
        

# Write the data to file
# Open the file if it was not open yet
def write_to_file(data):
    global write_file
    # Check if file was closed, due to an error at some point
    if write_file.closed:
        # Reopen it in append mode
        write_file = open(write_file_path, "a+")
    write_file.write('{0:.5f}, {1:.5f}\n'.format(data[0], data[1]))


# Read the data to file, one data point at a time
# Open the file if it was not open yet
def read_from_file():
    global read_file, start_time
    data = None
    current_time = time()
    if current_time - start_time > sampling_period:
        start_time = current_time
        # Check if file was closed, due to an error at some point
        if read_file.closed:
            # Reopen it in read mode
            read_file = open(read_file_path, "r")
        data = read_file.readline()
    return data


# Get data from file or from the BLE 
def get_data():  
    data = None
    # Read the data from file
    if read_flag:
        data_string = read_from_file()                  # Comma separated
    # Collect the data from BLE
    else:
        data_string = bt.ble_read_line(';')             # Comma separated

    # Convert to a list with floating point numbers
    try:
        t, y = data_string.split(',')                   # Split at ,
        data = [float(t.strip()), float(y.strip())]     # Strip spaces
    except:
        pass

    return data
    

# The main data processing function
# It is called repeatedly
def update_data():
    global data_buffer

    data = None
    while not data:                                 # Keep looping until valid data is captured
        data = get_data()

    # Write it to file if we need to
    if write_flag:
        write_to_file(data)

    # ****************************************************************************
    # * Filter the data
    # * The process_data() function takes a in a list of elements to be filtered
    # ****************************************************************************

    # You need to add some code here to get "sample_in"
    # "sample_in" needs to be an np array of the data samples to be filtered
    # In this case, there is only one sample. So "sample_in" is an array with just one data point.
    sample_filtered = filter.process_data(data_in=[data[1]])    # Filter the sample
    
    
    # Add this new data to circular data buffers
    data_buffer[0].add(data[0])                   # time data
    data_buffer[1].add(data[1])                   # sensor data
    data_buffer[2].add(sample_filtered)           # filtered sensor data


    # Plot two graphs: (sensor data vs time) and (filtered data vs time)
    return [(data_buffer[0], data_buffer[1]),(data_buffer[0], data_buffer[2])]
    # This format [(x1, y1), (x2, y2), (x3, y3)] is expected by the animation module


"""
This is where the main code starts
"""
while True:
    try:
        # Take care of some initializations
        initialize_buffers()
        initialize_ble()

        # ****************************************************************************
        # * Create the filter *
        # ****************************************************************************
        filter = Filter(sampling_frequency=sampling_freq, filter_frequency=0.5, filter_type='high')

        # If we are plotting our data
        # Call the animation with our update_data() function
        # This will call our function repeatedly and plot the results
        if live_plot:
            # create animation object
            # Plot about 1/5 of the data in the buffer
            an = AnimatedFigure(update_data, plot_samples=200, debug=True)
            axes = an.axes
            axes[0].set_title('Data')
            axes[0].set_xlabel('Time (s)')
            axes[0].set_ylabel('Voltage (V)')

            an.animate()  # only call this after configuring your figure

        # If we don't want to plot at the same time, call the update_data() function repeatedly
        else:
            while True:
                update_data()

    # Catch the user pressing Ctlr+C
    except (Exception, KeyboardInterrupt) as e:
        # if any type of exception occurs, it is printed and the loop is re-started
        try:
            if write_flag and write_file:
                write_file.close()
            if read_flag and read_file:
                read_file.close()
            else:
                bt.ble_close()              # Try to close the BLE connection cleanly (may fail)
        except Exception as e2:
            print(e2)
            print("Error during cleanup, you may want to restart/replug everything.")
        if isinstance(e, KeyboardInterrupt):
            print("Exiting program due to KeyboardInterrupt")
            break
        else:
            print("Restarting program due to error:")
            print(e)