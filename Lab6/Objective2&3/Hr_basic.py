#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

# from Libraries.ListBuffer import ListBuffer

from sklearn.mixture import GaussianMixture as GM
import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib.mlab as mlab


class Hr:

    def __init__(self, train_file, plot=False):
        self.plot = plot
        self.model = None
        self.train(train_file)

    def _normalize(self, data):
        return np.nan_to_num((data - np.nanmin(data))
                             / (np.nanmax(data) - np.nanmin(data)))

    def train(self, train_file):

        # Load training data. train_file must be in the same folder as the script implementing this class.

        (train_t, train_ir) = np.loadtxt(train_file, delimiter=',',
                skiprows=1, unpack=True)

        # Reshape training data to be a 2D array

        train_ir = np.array([train_ir]).reshape(-1, 1)
        train_t = np.array([train_t]).reshape(-1, 1)

        # Unit normalize

        train_ir = self._normalize(train_ir)

        # Create GMM object

        gmm = GM(n_components=2)

        # Find parameters for GMM based on training data

        self.model = gmm.fit(train_ir)

        if self.plot:
            self.plot_histo(train_ir)
            self.plot_labels(train_t, train_ir)

    def plot_histo(self, ir):

        # Retrieve Gaussian parameters

        mu0 = self.model.means_[0]
        sig0 = np.sqrt(self.model.covariances_[0])
        w0 = self.model.weights_[0]

        mu1 = self.model.means_[1]
        sig1 = np.sqrt(self.model.covariances_[1])
        w1 = self.model.weights_[1]

        # Create an "x" vector from which to compute normal distribution curves

        x = np.reshape(np.linspace(np.min(ir), np.max(ir), 1000),
                       [1000, 1])

        # Compute normal curves

        # Plot histograms and sum of curves

        plt.figure()
        plt.hist(ir, bins=50, density=True)
        plt.xlabel('IR reading')
        plt.ylabel('Voltage (V)')
        plt.title('IR Signal Histogram + two Gaussians')
        plt.plot(x, w0 * mlab.normpdf(x, mu0, sig0))
        plt.plot(x, w1 * mlab.normpdf(x, mu1, sig1))
        plt.show()

    def plot_labels(self, t, ir):
        labels = self.model.predict(ir)

        # Plot t, ir and labels

        plt.figure()
        plt.plot(t, labels)
        plt.plot(t, ir)
        plt.xlabel('IR reading')
        plt.ylabel('Label')
        plt.title('Labeled Training')
        plt.show()

    # Process the IR data to get a heart rate estimate
    # t_data: numpy array with timestamps
    # ir_data: numpy array with IR data
    # returns: heart rate hr estimate in bpm (returns None if not valid) and the time t_hr for that hr estimate

    def process(self, t_data, ir_data):

        # Reshape and normalize your data

        ir_data = np.array([ir_data]).reshape(-1, 1)
        ir_data = self._normalize(ir_data)

        # Use GMM to label beats

        labels = self.model.predict(ir_data)

        # Apply beat heuristics
        # You may want to wrap this in a try/except clause to avoid issues like 0 heartbeat giving a divide by zero error

        

        try:
            (t_hr, hr) = self.hr_heuristics(t_data, labels)
            return (t_hr, hr)
        except:
            return None

    # Process the label data to get a hr estimate
    # t: numpy array with timestamps
    # labels: numpy array with corresponding GMM labels of the data
    # returns: heart rate hr estimate in bpm (returns None if not valid) and the time t_hr for that hr estimate
    def hr_heuristics(self, t, labels):
        # print(labels)
        interval = []
        intervalFlag = False
        counter = 0
        # Count timespan for each pulse
        for sample in labels:
            if sample == 1:
                if not intervalFlag:
                    intervalFlag = True
                counter = counter + 1
            else:
                if intervalFlag:
                    intervalFlag = False
                    interval.append(counter)
                    counter = 0
        # Acquire average interval for a single pulse
        avgInterval = np.average(interval)
        stdInterval = np.std(interval)
        # Eliminate outlier pulse
        for sample in interval:
            if sample < avgInterval - 2 * stdInterval or sample > avgInterval + 2 * stdInterval:
                interval.remove(sample)
        numSamples = len(interval)
        # Timespan of sample in minutes
        timespan = (len(t) * 0.05) / 60
        # Calculate bpm
        bpm = numSamples / timespan
        return t, bpm