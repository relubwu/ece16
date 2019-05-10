from scipy.signal import sosfilt, butter, sosfilt_zi
# from scipy.signal import lfilter, butter, lfilter_zi
import numpy as np
import warnings

# supress scipy warnings
warnings.filterwarnings("ignore")


class Filter:

    def __init__(self, sampling_frequency, filter_frequency, filter_type, filter_order=3):
        """
        Creates a filter object that can filter bulk data or one data point at a time.
        :param sampling_frequency: sampling frequency of the data
        :param filter_frequency: cutoff frequency of the desired filter
        :param filter_type: type of filter, either 'low' (lowpass) or 'high' (highpass).
        :param initial_data: data points with which to initialize the filter
        :param filter_order: order of the desired filter. Default is 3.
        :return: if initial_data contains > 1 data point, initialization returns filter results for subsequent points.
        """
        self.f_s = sampling_frequency
        self.f_filter = filter_frequency
        self.filter_type = filter_type
        self.order = filter_order
        self.sos = butter(N=self.order, Wn=self.f_filter / (0.5 * self.f_s), btype=self.filter_type, output='sos')
        # self.a, self.b = butter(N=self.order, Wn=self.f_filter / (0.5 * self.f_s), btype=self.filter_type, output='ba')
        self.z = None

    def process_data(self, data_in):
        """
        Call this function passing new data to filter data as it comes in.
        :param data_in: single float or iterable.
        :return: np.array with filtered data (or single element if input is single element).
        """
        # Ensure input is a numpy array
        data_in = self.to_iter(data_in)
        # Check if this is the first run
        if self.z is None:
            self.z = sosfilt_zi(sos=self.sos) * data_in[0]
            # self.z = lfilter_zi(a=self.a, b=self.b) * data_in[0]
        # Apply the filter
        data_out, self.z = sosfilt(sos=self.sos, x=data_in, zi=self.z)
        # data_out, self.z = lfilter(a=self.a, b=self.b, x=data_in, zi=self.z)

        return self.to_single(data_out)

    @staticmethod
    def to_iter(data_in):
        """
        Ensures the data is in a numpy array.
        """
        if isinstance(data_in, (float, int)):
            data_in = [data_in]
        return np.array(data_in, dtype=float, ndmin=1)

    @staticmethod
    def to_single(data_in):
        """
        Checks if the data is a single element iterable and expands it, otherwise returns the iterable.
        """
        try:
            length = len(data_in)
            if length > 1:
                return data_in
            else:
                return data_in[0]
        except TypeError:
            return data_in
