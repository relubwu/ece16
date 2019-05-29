"""
Receive sensor data from the Arduino
Store it and/or plot it
"""

# Import Python builtin libraries
import os
from time import time
import numpy as np

# Import custom libraries
from Libraries.Bt import Bt
from Libraries.ListBuffer import ListBuffer
from Libraries.AnimatedFigure import AnimatedFigure
from Libraries.FilterWrapper import Filter
from Libraries.hr import Hr
from Libraries.pedometer import Pedometer

# Set peripheral MAC as well as HM-10 serial port
peripheral_MAC = "D8A98BB47D89"
serial_port = "/dev/cu.usbserial"

# Define if data should be live-plotted
live_plot = False
# Define if data should be written out to file
write_flag = False
# Define if we should read from BLE or from a file
# If False, we read from BLE; if True, we read from file and will use the sampling_period (in seconds)
read_flag = False
sampling_freq = 20  # [Hz]
sampling_period = 1 / sampling_freq  # [s]
# Define global timer
time_start_bpm = 0.0
time_start_pedometer = 0.0
# Define global steps counter and bpm value
steps = 0
bpm = 0.0
# Define global offset
offset = 100

# Open the files and read and write if necessary
if write_flag:
    write_filename = "pedometer_training_resting.csv"
    # We use this to make sure the file is saved in the script directory and not the dir Python is executing from
    current_dir = os.path.dirname(os.path.abspath(__file__))
    write_file_path = current_dir + "\\" + write_filename
    write_file = open(write_file_path, 'w', buffering=1)
    write_file.write('{0}, {1}, {2} \n'.format("t", "ir", "imu"))  # Write the headers for csv file

if read_flag:
    read_filename = "data_save.csv"
    # We use this to make sure the file is saved in the script directory and not the dir Python is executing from
    current_dir = os.path.dirname(os.path.abspath(__file__))
    read_file_path = current_dir + "\\" + read_filename
    if write_flag:
        assert read_file_path != write_file_path, "You can't read and write to the same file"
    read_file = open(read_file_path, 'r')
    read_file.readline()  # skip first row, which may contain name of variables

# Sample time
start_time = 0  # Start time


# Initialization of buffers
def initialize_buffers():
    global data_buffer
    # Create empty buffers to store data
    buffer_length = 50 * 30  # initial estimate for 30 sec of data at 50Hz, that's probably waaay too long!
    data_buffer = [[]] * 5  # t, imu, ir, ir filtered: 4 total
    data_buffer[0] = ListBuffer([], maxlen=buffer_length)  # time data
    data_buffer[1] = ListBuffer([], maxlen=buffer_length)  # ir data
    data_buffer[2] = ListBuffer([], maxlen=buffer_length)  # ir data filtered
    data_buffer[3] = ListBuffer([], maxlen=buffer_length)  # imu data
    data_buffer[4] = ListBuffer([], maxlen=buffer_length)  # imu data filtered


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
    write_file.write('{0:.5f}, {1:.5f}, {2:.5f}\n'.format(data[0], data[1], data[2]))


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
        data_string = read_from_file()  # Comma separated
    # Collect the data from BLE
    else:
        data_string = bt.ble_read_line(';')  # Comma separated

    # Convert to a list with floating point numbers
    try:
        t, ir, imu = data_string.split(',')  # Split at ,
        data = [float(t.strip()), float(ir.strip()), float(imu.strip())]  # Strip spaces
    except:
        pass

    return data


# The main data processing function
# It is called repeatedly
def update_data():
    global data_buffer
    global time_start_bpm
    global time_start_pedometer
    global steps
    global offset
    global bpm

    data = None
    while not data:  # Keep looping until valid data is captured
        data = get_data()

    # Write it to file if we need to
    if write_flag:
        write_to_file(data)

    # ****************************************************************************
    # * Filter the data
    # * The process_data() function takes a in a list of elements to be filtered
    # ****************************************************************************
    unfiltered_ir = [data[1]]  # The sample is [time, sensordata]; extract the sensordata part
    lowpass_ir = [lowpass_filt.process_data(unfiltered_ir)]  # Filter the sample
    bandpass_ir = highpass_filt.process_data(lowpass_ir)  # Filter the sample

    data = data + [bandpass_ir]
    
    # ****************************************************************************
    # * Filter the data
    # * The process_data() function takes a in a list of elements to be filtered
    # ****************************************************************************
    # print(data[2])
    # data[2] = abs(data[2]) - 49152
    unfiltered_imu = data[2]  # The sample is [time, sensordata]; extract the sensordata part
    lowpass_imu = [lowpass_filt.process_data(unfiltered_imu)]  # Filter the sample
    bandpass_imu = highpass_filt.process_data(lowpass_imu)  # Filter the sample
    
    data = data + [bandpass_imu]

    # Add this new data to circular data buffers
    data_buffer[0].add(data[0])  # t data
    data_buffer[1].add(data[1])  # ir data
    data_buffer[2].add(data[2])  # imu data
    data_buffer[3].add(data[3])  # filtered ir data
    data_buffer[4].add(data[4])  # filtered imu data
    
    # Time-elapsed BPM calculation
    time_end_bpm = time()
    if (time_end_bpm - time_start_bpm >= 1):
        time_start_bpm = time()
        bpm_result = hr_calc.process(data_buffer[0], data_buffer[1])
        if (bpm_result[1] is not None):
            bpm = bpm_result[1]
            print("BPM: %.2f" % bpm)

    # Time-elapsed pedometer
    time_end_pedometer = time()
    if (time_end_pedometer - time_start_pedometer >= 5):
        time_start_pedometer = time()
        
        f = np.array(data_buffer[0][-offset:]).reshape(-1, 1)
        g = np.array(data_buffer[2][-offset:]).reshape(-1, 1)
        
        pedo_calc.process(f, g)
        offset += 100
        print("Steps:", pedo_calc.steps)
        steps = pedo_calc.steps
        
        bt.ble_write("HR:" + str(bpm) + "," + "Steps:" + str(steps) + ";" )
            
    
    return [(data_buffer[0], data_buffer[2])]  # Plot t, imu data
    # This format [(x1, y1), (x2, y2), (x3, y3)] is expected by the animation module


def cleanup():
    """
    Close files and BLE connection.
    """
    if write_flag and write_file:
        write_file.close()
    if read_flag and read_file:
        read_file.close()
    else:
        bt.ble_close()  # Try to close the BLE connection cleanly (may fail)
    print("Ran cleanup")


"""
This is where the main code starts
"""
while True:
    try:
        # Take care of some initializations
        initialize_buffers()
        initialize_ble()

        # Instantiate filters
        lowpass_filt = Filter(sampling_frequency=sampling_freq, filter_frequency=4, filter_type='low')
        highpass_filt = Filter(sampling_frequency=sampling_freq, filter_frequency=0.5, filter_type='high')
        
        # Instantiate Hr class
        hr_calc = Hr(train_file="../../Common/ir_data_train.csv", plot=False)
        
        # Instantiate pedometer class
        pedo_calc = Pedometer("pedometer_training_active.csv", "pedometer_training_resting.csv")

        # If we are plotting our data
        # Call the animation with our update_data() function
        # This will call our function repeatedly and plot the results
        if live_plot:
            # create animation object
            # Plot about 1/5 of the data in the buffer
            an = AnimatedFigure(update_data, plot_samples=200, debug=False)
            axes = an.axes
            axes[0].set_title('Data')
            axes[0].set_xlabel('Time (s)')
            axes[0].set_ylabel('IMU Value (au)')

            an.animate()  # only call this after configuring your figure

        # If we don't want to plot at the same time, call the update_data() function repeatedly
        else:
            while True:
                update_data()

    except (KeyboardInterrupt):
        # Exits from ctrl+c in terminal, "stop" button in Spyder or closing the figure (in both)
        cleanup()
        print("Exiting program due to KeyboardInterrupt")
        clean_exit = True
        break
    except (Exception) as e:
        cleanup()
        print(e)
        print("Restarting program due to error:")
        continue
    finally:
        if not clean_exit:
            print("Error during cleanup or restart. Try power cycling Arduino or unplug/replug.")
            break
