# Imports
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
import time


class AnimatedFigure:

    def __init__(self, data_function, plot_samples, interval=1, debug=False, blit=True):
        """
        Initializes the live-plots and starts polling for new data.
        If you want to edit the axis titles and such, instantiate the class then acess the self.axes object.
        :param data_function: a generator function which returns the plotting data whenever it is called.
        Remeber, in Python functions are first class!
        :param plot_samples: initial batch of data to be plotted. Refer to update_plots() for info on data format.
        :param interval: interval (in ms) between polling to data_function().
        Increase to reduce resource utilization at the cost of smoothness. Recommend setting to sampling freq of data.
        :param debug: prints FPS at which plot is rendered.
        :param blit: set to True to increase speed at cost of updating x-axis. Set to false to allow x-axis to update.
        :return: animated plot object.
        """
        # counter vars for performance monitoring
        self.counter = 0
        self.timer = 0
        self.debug = debug
        # initialize figure
        self.interval = interval
        self.plot_samples = plot_samples
        self.blit = blit
        self.data_function = data_function
        init_data = self.data_function()
        self.num_plots = len(init_data)
        if self.blit:
            # make copies to avoid overwriting mutable objects
            initial_plot_data = [(np.arange(0, self.plot_samples), np.zeros(self.plot_samples)) for _ in init_data]
            self.xdata = initial_plot_data[0][0]     # persists
        else:
            initial_plot_data = init_data
        self.fig, self.axes = plt.subplots(1, self.num_plots)
        if self.num_plots == 1:
            self.axes = [self.axes]     # we need it to be iterable for zip to work on the next line
        self.live_plot = [axes.plot(t, y)[0] for axes, (t, y) in zip(self.axes, initial_plot_data)]
        plt.tight_layout()
        self.ani = None     # placeholder for animation object

    def update_plots(self, idx):
        """
        Updates the live-plots based on new data collected.
        A maximum of plot_samples data points will be plotted.
        Axis limits are automatically adjusted.
        :param idx: required parameter by FuncAnimation. It is not used.
        :return: list of objects (axis) updated.
        """
        self.fps()

        data = self.data_function()   # data_function must return a tuple containing lists of x,y data

        for (x, y), ax, plot_num in zip(data, self.axes, range(self.num_plots)):
            x = x[-self.plot_samples:]
            y = y[-self.plot_samples:]
            if self.blit:
                len_dif = self.plot_samples - len(y)
                if len_dif > 0:
                    y_blit = [np.nan] * len_dif + y
                else:
                    y_blit = y
                self.live_plot[plot_num].set_ydata(y_blit)
                # ax.set_animated(False)
            else:
                ax.set_xlim(x[0], x[-1])
                self.live_plot[plot_num].set_data(x, y)
            if np.mod(idx, self.plot_samples / 5) == 0:  # only check every couple frames for speed
                # check if data is out of range of axis, if so force y-axis to update
                ymin, ymax = ax.get_ylim()
                data_range = np.max(y) - np.min(y)
                new_max_lim = np.max(y) + data_range * 0.05 + 0.0000001  # ensures if y is constant there is a dif
                new_min_lim = np.min(y) - data_range * 0.05 - 0.0000001  # ensures if y is constant there is a dif
                if not ((.9 < ymax / new_max_lim < 1.1) and (.9 < ymin / new_min_lim < 1.1)) and idx > 10:
                    ax.set_ylim(bottom=new_min_lim, top=new_max_lim)
        return self.live_plot

    def fps(self):
        self.counter += 1
        now = time.time()
        elapsed = now - self.timer
        if now - self.timer >= 1:
            if self.debug:
                print("FPS: %.2f" % (self.counter / elapsed))
            if (self.counter / elapsed) < 1.25 * self.interval:
                print("Warning: animation slowdown.")
            self.counter = 0
            self.timer = now
        return

    def animate(self):
        """
        Starts showing the plotting window. Blocks execution of subsequent code (except calls to self.update_plots())!
        :return: None
        """
        # instantiate animation
        self.ani = animation.FuncAnimation(
            fig=self.axes[0].figure, func=self.update_plots, interval=self.interval, blit=self.blit)
        plt.show()
        return
