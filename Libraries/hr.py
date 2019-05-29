import numpy as np
from Libraries.ListBuffer import ListBuffer
from sklearn.mixture import GaussianMixture as GM
import matplotlib.pyplot as plt
from scipy.stats import norm


class Hr:

    # Added window_length
    def __init__(self, train_file, window_length=100, plot=False):
        self.window_length = window_length
        self.plot = plot
        self.model = None
        self.train(train_file)

    def _normalize(self, data):
        return np.nan_to_num((data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data)))

    def train(self, train_file):
        """
        Loads the training data and learns the GMM. Optionally plots the results.
        :param train_file: filename for training file containing time and pre-processed ir data.
        :return: None
        """
        # Load training data. train_file must be in the same folder as the script implementing this class.
        train_t, train_ir = np.loadtxt(train_file, delimiter=",", skiprows=1, unpack=True)

        # Reshape training data to be a 2D array
        train_ir = train_ir.reshape(len(train_ir), 1)
        train_t = train_t.reshape(len(train_ir), 1)

        # Unit normalize
        train_ir = self._normalize(train_ir)

        # Create GMM object
        #        gmm = GM(n_components=2, means_init=np.array([[0.25], [0.85]]))     # mean guesses for normalized data
        gmm = GM(n_components=2, means_init=np.array([[0.25], [0.85]]))

        # Find parameters for GMM based on training data
        self.model = gmm.fit(train_ir)
        if self.plot:
            histo = self.plot_histo(train_ir)
            histo.axes[0].set_title(f"Histogram for: {train_file}")
            labels = self.plot_labels(train_t, train_ir)
            labels.axes[0].set_title(f"Labels for: {train_file}")
        return

    def plot_histo(self, ir):
        # Create new figure
        f = plt.figure()
        # Retrieve Gaussian parameters
        mu0 = self.model.means_[0]
        mu1 = self.model.means_[1]
        std0 = np.sqrt(np.abs(self.model.covariances_[0][0][0]))
        std1 = np.sqrt(np.abs(self.model.covariances_[1][0][0]))
        w0 = self.model.weights_[0]
        w1 = self.model.weights_[1]
        # Create an "x" vector from which to compute normal distribution curves
        x = np.reshape((np.linspace(np.min(ir), np.max(ir), 1000)), [1000, 1])
        # Compute normal curves
        curve_0 = w0 * norm.pdf(x, loc=mu0, scale=std0)
        curve_1 = w1 * norm.pdf(x, loc=mu1, scale=std1)
        # Plot the histogram
        plt.hist(ir, bins=50, density=True)
        # Plot the curves
        plt.plot(x, curve_0, '-r')
        plt.plot(x, curve_1, '-b')
        # Label the plots
        plt.xlabel("IR data")
        plt.ylabel("Count (#)")
        plt.title("IR Signal Histogram")
        plt.tight_layout()
        plt.show(block=False)
        return f

    def plot_labels(self, t, ir):
        # Create new figure
        f = plt.figure()
        # Calculate the labels
        labels = self.model.predict(ir)
        # Plot data and labels, scaling ltabels to max of data
        plt.plot(t, ir, 'b-')
        plt.plot(t, labels * np.max(ir), 'r-')
        # Label plot
        plt.ylabel('Voltage (V)')
        plt.xlabel('Time (s)')
        plt.title('GMM Labels')
        plt.show(block=False)
        return f

    def process(self, t_data, ir_data):
        """
        Passes new data first to the GM prediction method and then to other heuristics methods.
        :param t_data: iterable (list or 1D numpy array) containing time data.
        :param ir_data: iterable (list or 1D numpy array) containing ir data.
        :return: calculated heart rate, taking into account previously calculated heart rates, along with timestamp.
        """
        # NEW
        # Slice
        t = t_data[-self.window_length:]
        ir = ir_data[-self.window_length:]

        # Convert to numpy arrays, as required by sklearn.mixture.GaussianMixture
        t = np.array(t)
        ir = np.array(ir)

        # Unit normalize (this helps account for different amounts of pressure on the sensors)
        ir = self._normalize(ir)

        # Use GMM to label beats
        labels = self.model.predict(ir.reshape(len(ir), 1)).flatten()

        # Apply beat heuristics
        # You may want to wrap this in a try/except clause to avoid issues like 0 heartbeat giving a divide by zero error
        # Assign placeholders to return if processing fails.
        hr = None
        t_hr = t_data[-1]
        try:
            t_hr, hr = self.hr_heuristics(t, labels)
        except:
            pass

        return t_hr, hr

    def hr_heuristics(self, t, labels):
        """
        Makes sure heart beats detected are well spaced and of normal duration.
        :param t: iterable (list or 1D numpy array) containing timestamps.
        :param labels: iterable (list or 1D numpy array) containing data labels (0/1).
        :return: heart rate extracted from timestamps and labels and timestamp at which it was calculated.
        """
        
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
        if 60 < bpm < 180:
            return t, bpm
        else:
            return bpm
