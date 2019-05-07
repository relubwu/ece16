"""
Example of live plotting
"""

# Import custom libraries
from Libraries.ListBuffer import ListBuffer
from Libraries.AnimatedFigure import AnimatedFigure
from FilterWrapperBasic_complete import Filter

# Import time library
from time import time


# This is only needed for our example data we are using
# You can delete this when you are using your actual sensor data
import numpy as np              # Numpy library
current_time = 0                # Current time
start_time = 0                  # Start time
sampling_freq = 50              # [Hz]
sampling_period = 1 / sampling_freq     # [s]

# Sine wave frequency
f0 = 2                          # [Hz]
f1 = 20                         # [Hz]


# Should we plot our data or not
live_plot = True


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


# This is just an example function
# You will want to replace this with the proper function to get data, e.g., from BLE 
def get_data():
    global current_time, start_time
    data = None
    current_time = time()
    if current_time - start_time > sampling_period:
        start_time = current_time
        data = [current_time, np.cos(2*np.pi*f0*current_time) + 0.2*np.cos(2*np.pi*f1*current_time)]
    return data

    
# The main data processing function
# It is called repeatedly
def update_data():
    global data_buffer

    data = None
    while not data:                                 # Keep looping until valid data is captured
        data = get_data()                                                 


    # ****************************************************************************
    # * Filter the data
    # * The process_data() function takes a in a list of elements to be filtered
    # ****************************************************************************

    # You need to add some code here to get "sample_in"
    # "sample_in" needs to be an np array of the data samples to be filtered
    # In this case, there is only one sample. So "sample_in" is an array with just one data point.
    sample_in = np.array([data[1]])
    sample_filtered = filter.process_data(data_in=sample_in)    # Filter the sample
    
    
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
try:
    # Take care of some initializations
    initialize_buffers()

    # ****************************************************************************
    # * Create the filter *
    # ****************************************************************************
    filter = Filter(sampling_frequency=sampling_freq, filter_frequency=f0*5, filter_type='low')
        
    # If we are plotting our data
    # Call the animation with our update_data() function
    # This will call our function repeatedly and plot the results
    if live_plot:
        # Create animation object
        # Plot about 1/5 of the data in the buffer
        an = AnimatedFigure(update_data, plot_samples=100, debug=True)
        axes = an.axes
        axes[0].set_title('Data')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Voltage (V)')

        an.animate()            # Only call this after configuring your figure

    # If we don't want to plot at the same time, call the update_data() function repeatedly
    else:
        while True:
            update_data()
            
# Catch the user pressing Ctlr+C            
except (Exception, KeyboardInterrupt) as e:
    print(e)