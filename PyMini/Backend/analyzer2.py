import numpy as np
import os.path
import matplotlib.pyplot as plt
from math import ceil, hypot, isnan, sqrt
from datetime import datetime
from pyabf import abf
from pyabf.abfWriter import writeABF1

from PyMini.config import config

from pandas import DataFrame, Series
import pandas as pd
from scipy.optimize import curve_fit
from time import time  # debugging


##################################################
# Class to store electrophysiology recording data
##################################################

class Recording():
    def __init__(self, filepath):
        self.filepath = filepath
        # initialize metadata
        self.channel = 0
        self.added_sweep_count = 0
        self.sweep_count = 0
        self._open_file(filepath)

    def _open_file(self, filename):
        self.filetype = os.path.splitext(filename)[1]
        _, self.filename = os.path.split(filename)

        if self.filetype == '.abf':
            self.read_abf(filename)
        elif self.filetype == '.csv':
            self.read_csv(filename)

        else:
            # insert support for other filetypes here
            pass
    def read_abf(self, filename):
        data = abf.ABF(filename)
        # sampling rate of the recording
        self.sampling_rate = data.dataRate
        # sampling rate significant digits - used to round calculations
        self.x_sigdig = len(str(self.sampling_rate)) - 1
        # interval between each x-values (inverse of sampling rate)
        self.x_interval = 1 / self.sampling_rate

        # channel metadata
        self.channel_count = data.channelCount
        self.channel_names = data.adcNames
        self.channel_units = data.adcUnits
        self.channel_labels = [""] * self.channel_count
        for c in range(self.channel_count):
            data.setSweep(0, c)
            self.channel_labels[c] = data.sweepLabelY.replace('\x00','')
        # x_value metadata
        self.x_unit = data.sweepUnitsX
        self.x_label = data.sweepLabelX  # in the form of Label (Units)

        # y_value metadata
        self.sweep_count = data.sweepCount
        self.original_sweep_count = self.sweep_count
        self.sweep_points = data.sweepPointCount

        # extract y and x values and store as 3D numpy array (channel, sweep, datapoint)
        self.y_data = np.reshape(data.data, (self.channel_count, self.sweep_count, self.sweep_points))
        self.x_data = np.repeat(np.reshape(data.sweepX, (1, 1, self.sweep_points)), self.sweep_count, axis=1)
        self.x_data = np.repeat(self.x_data, self.channel_count, axis=0)

    def read_csv(self, filename):
        """
        only supports single channel data
        """
        self.channel_count = 1
        self.sweep_count = 0
        self.sweep_points = 0
        self.x_unit = ['sec']
        self.y_unit = ['N/A']
        self.y_label = ['N/A']
        with open(filename, 'r') as f:
            for l in f.readlines():
                l = l.strip()
                if l[0] == '@': #header
                    header_label = l[1:].split('=')[0]
                    header_data = l[1:].split('=')[1]
                    if header_label == 'version':
                        version = header_data
                    elif header_label == 'sweep_count':
                        self.sweep_count = int(header_data)
                        self.original_sweep_count = self.sweep_count
                    elif header_label == 'sweep_points':
                        self.sweep_points = int(header_data)
                    elif header_label == 'sampling_rate':
                        self.sampling_rate = float(header_data)
                        # sampling rate significant digits - used to round calculations
                        self.x_sigdig = len(str(self.sampling_rate)) - 1
                        # interval between each x-values (inverse of sampling rate)
                        self.x_interval = 1 / self.sampling_rate
                    elif header_label == 'channel_unit':
                        self.channel_units=[header_data]
                    elif header_label == 'channel_label':
                        self.channel_labels=[header_data]
                    elif header_label == 'x_unit':
                        self.x_unit = [header_data]
                    elif header_label == 'x_label':
                        self.x_label = [header_data]
                else:
                    if self.y_data.shape[2] > 0:
                        self.y_data = np.append(self.y_data,
                                            np.reshape(np.array([float(i) for i in l.split(',')]), (1, 1, self.sweep_points)),
                                            axis=1)
                    else:
                        ys = [float(i) for i in l.split(',')]
                        if self.sweep_points == 0:
                            self.sweep_points = len(ys)
                        self.y_data = np.reshape(np.array(ys),
                                                 (1, 1, self.sweep_points))
            if self.sweep_count == 0:
                self.sweep_count = self.y_data.shape[1]
            sweepX = np.arange(self.sweep_points)/self.sampling_rate
            self.x_data = np.repeat(np.reshape(np.array(sweepX), (1, 1, self.sweep_points)),
                                    self.sweep_count,
                                    axis=1)

    def save(self, filename, channels=None, suffix=0, handle_error=False):
        if channels is None:
            channels = [i for i in range(self.channel_count)]
        if suffix > 0:
            fname = f'{filename.split(".")[0]}({suffix}).{filename.split(".")[1]}'
        else:
            fname = filename
        if os.path.exists(fname):
            if handle_error:
                self.save(filename, channels, suffix+1, handle_error)
                return
            else:
                raise FileExistsError
        filetype = os.path.splitext(fname)[1]
        if filetype == '.abf':
            self.write_abf(fname)
        elif filetype == '.csv':
            self.write_csv(fname, channels)
    def write_abf(self, filename):
        writeABF1(self.y_data, filename, self.sampling_rate, self.channel_units)

    def write_csv(self, filename, channel=None):
        if channel is None:
            channel = self.channel
        with open(filename, 'x') as f:
            f.write(f'@version={config.version}\n')
            f.write(f'@sweep_count={self.sweep_count}\n')
            f.write(f'@sweep_points={self.sweep_points}\n')
            f.write(f'@channel_unit={self.channel_units[channel]}\n')
            f.write(f'@channel_label={self.channel_labels[channel]}\n')
            f.write(f'@sampling_rate={self.sampling_rate}\n')
            f.write(f'@x_unit={self.x_unit}\n')
            f.write(f'@x_label={self.x_label}\n')
            for s in range(self.sweep_count):
                f.write(','.join([str(i) for i in self.y_data[channel, s, :].tolist()]))
                f.write('\n')




    def set_channel(self, channel):
        self.y_label = self.channel_labels[channel]
        self.y_unit = self.channel_units[channel]

        # if index out of bounds, the above code will raise an error
        # otherwise, store the channel value
        self.channel = channel


    def replace_y_data(self, mode='continuous', channels=None, sweeps=None, new_data=None):
        """
        replaces y-values in specified sweeps and channels with data provided

        mode: string {'continuous', 'overlay'} defaults to 'continuous'
        channels: list of int - if None, defaults to first N channels that match the dimension of the input data
        sweeps: list of int - only used for the 'overlay' plot_mode. If None, defaults to the first N sweeps that match the dimension of the input data
        new_data: new y-values to replace. Must be a 3D float numpy array
        """
        assert len(new_data.shape) == 3, 'Matrix shape mismatch - the input data must be a 3D numpy array'
        if channels is None:
            channels = range(new_data.shape[0])

        if mode == 'continuous':
            assert new_data.shape[
                       2] % self.sweep_points == 0, f'Sweep length mismatch. Each sweep in "continuous" mode must be a multiple of {self.sweep_points} datapoints'
            if sweeps is None:
                sweeps = range(int(new_data.shape[2] / self.sweep_points))

            new_data = np.reshape(new_data, (len(channels), len(sweeps), self.sweep_points))

        elif mode == 'overlay':
            assert new_data.shape[
                       2] == self.sweep_points, f'Sweep length mismatch. Each sweep in "overlay" mode must be {self.sweep_points} datapoints'
            if sweeps is None:
                sweeps = range(new_data.shape[1])
        else:
            print(f'incorrect mode: {mode}')
            return None
        for i, c in enumerate(channels):
            self.y_data[c, sweeps, :] = new_data[i]

    def get_y_matrix(self, mode='continuous', sweeps=None, channels=None, xlim=None):
        """
        returns a slice of the y_data
        mode: string
            'continuous', 'overlay'
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - If None, defaults to all sweeps
        xlim: float tuple [left, right] - If None, defaults to all data points in each sweep
        """
        if channels == None:
            channels = range(self.channel_count)
        if sweeps == None:
            sweeps = [i for i in range(self.sweep_count)]
        if mode == 'continuous':
            if xlim:
                return np.reshape(self.y_data[channels][:, sweeps, :],
                                  (len(channels), 1, len(sweeps) * self.sweep_points))[
                       :, :, max(0, int(xlim[0] / self.x_interval)):min(self.sweep_count * self.sweep_points,
                                                                        ceil(xlim[1] / self.x_interval) + 1)]
            else:
                return np.reshape(self.y_data[channels][:, sweeps, :],
                                  (len(channels), 1, len(sweeps) * self.sweep_points))[
                       :, :, :]
        if mode == 'overlay':
            if xlim:
                return self.y_data[channels][:, sweeps,
                       max(0, int(xlim[0] / self.x_interval)):min(self.sweep_count * self.sweep_points,
                                                                  ceil(xlim[1] / self.x_interval) + 1)]
            return self.y_data[channels][:, sweeps]

    def get_x_matrix(self, mode='continuous', sweeps=None, channels=None, xlim=None):
        """
        returns a slice of the x_data
        mode: string
            'continuous', 'overlay'
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - only used for the 'overlay' plot_mode. If None, defaults to all sweeps
        xlim: float tuple [left, right] - If None, defaults to all data points in each sweep
        """
        if sweeps is None:
            sweeps = range(self.sweep_count)
        if channels == None:
            channels = range(self.channel_count)
        if mode == 'continuous':
            mult = np.arange(0, len(sweeps))
            mult = np.reshape(mult, (1, len(sweeps), 1))
            offset = mult * (self.sweep_points * self.x_interval)
            x_matrix = np.reshape(self.x_data[channels][:, sweeps] + offset,
                                  (len(channels), 1, len(sweeps) * self.sweep_points))
            if xlim:
                start_idx = max(0, int(xlim[0] / self.x_interval))
                end_idx = min(self.sweep_count * self.sweep_points, ceil(xlim[1] / self.x_interval) + 1)
                return x_matrix[:, :, start_idx:end_idx]
            return x_matrix
        if mode == 'overlay':
            if xlim:
                start_idx = max(0, int(xlim[0] / self.x_interval))
                end_idx = min(self.sweep_count * self.sweep_points, ceil(xlim[1] / self.x_interval) + 1)
                return self.x_data[channels][:, sweeps][:, :, start_idx, end_idx]
            return self.x_data[channels][:, sweeps]

    def get_xs(self, mode='continuous', sweep=None, channel=None, xlim=None):
        """
        returns a 1D numpy array representing the x-values in the recording.
        Use this function to get x-values for plotting
        mode: string
            continuous, concatenate, or None
        sweep: int
        channel: int if None, defaults to current channel
        xlim: float tuple - [left, right] If None, defaults to all x-values
        """
        if not channel:
            channel = self.channel
        if mode == 'continuous':
            return self.get_x_matrix(mode='continuous', channels=[channel], xlim=xlim).flatten()
        return self.get_x_matrix(mode='overlay', sweeps=[sweep], channels=[channel], xlim=xlim).flatten()

    def get_ys(self, mode='continuous', sweep=None, channel=None, xlim=None):
        """
        returns a 1D numpy array representing the y-values of the recording.
        Use this functions to get y-values for plotting
        mode: string
            'continuous', 'overlay', or None
            if 'continuous', all sweeps are represented
        sweep: int
        channel: int
            if empty, the current channel in the object is used
        xlim: float tuple - [left, right] If None, defaults to all x-values
        """
        if channel == None:
            channel = self.channel
        if mode == 'continuous':
            return self.get_y_matrix(mode='continuous', channels=[channel], xlim=xlim).flatten()
        return self.get_y_matrix(mode=mode, channels=[channel], sweeps=[sweep], xlim=xlim).flatten()

    def save_y_data(self, filename, channels=None, sweeps=None):
        """
        saves y_data of specified channels and sweeps in a temporary file

        filename: str name of the file
        channels: list of int, defaults to all channels if None
        sweeps: list of int, defaults to all sweeps if None
        """
        if not channels:
            channels = range(self.channel_count)
        if not sweeps:
            sweeps = range(self.sweep_count)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            for c in channels:
                for s in sweeps:
                    f.write(','.join([str(d) for d in self.y_data[c][s]]))
                    f.write('\n')
        return None

    def load_y_data(self, filename, channels=None, sweeps=None):
        if not channels:
            channels = range(self.channel_count)
        if not sweeps:
            sweeps = range(self.sweep_count)
        with open(filename, 'r') as f:
            for c in channels:
                for i in sweeps:
                    self.y_data[c, i] = np.fromstring(f.readline(), dtype=float, sep=',')
        return None

    def append_sweep(self, new_data, channels=None, fill=0):
        """
        appends a new sweep to the end of y_data
        new_data: numpy array - if new_data is a 3D numpy array, it assumes the dimensions match the existing y_data
                if the new_data is a 1D or 2D numpy array, missing data is filled with the value specified in fill argument
        channels: list of int - used if the dimensions of new_data does not match the y_data (axis=0 does not match)
        fill: float - if sweep data for some channels are missing, this argument is used to fill the missing data
        """

        if new_data.shape == (self.channel_count, 1, self.sweep_points):
            # the dimension matches y_data for np.append()
            self.y_data = np.append(self.y_data, new_data, axis=1)

        else:  # the dimension needs to be fixed
            temp_data = np.full((self.channel_count, 1, self.sweep_points), dtype=np.float, fill_value=fill)
            assert new_data.shape[
                       -1] == self.sweep_points, 'dimension mismatch - the sweep length does not match the existing data'
            new_data_reshape = np.reshape(new_data, (len(channels), 1, self.sweep_points))
            temp_data[channels] = new_data_reshape
            self.y_data = np.append(self.y_data, temp_data, axis=1)

        self.x_data = np.append(self.x_data, self.x_data[:, -new_data.shape[1]:, :], axis=1)
        self.sweep_count += 1
        self.added_sweep_count += 1

    def delete_last_sweep(self):
        if self.sweep_count == self.original_sweep_count:
            return None  # cannot delete original data
        self.y_data = self.y_data[:, :-1, :]
        self.x_data = self.x_data[:, :-1, :]
        self.sweep_count -= 1
        self.added_sweep_count -= 1


############################################
# Analyzer functions
############################################

class Analyzer():
    def __init__(self, plot_mode='continuous'):
        self.plot_mode = plot_mode

        # initialize dataframes
        self.mini_df = DataFrame()


    def open_file(self, filename):
        return Recording(filename)

    def clear_mini_df(self):
        self.mini_df = self.mini_df.iloc[0:0]


    def set_plot_mode(self, plot_mode):
        self.plot_mode = plot_mode

    def plot(self, recording, plot_mode=None, channels=None, sweeps=None, xlim=None, ylim=None, color='black', linewidth=2,
             show=True):
        """
        displays a plot of the recording. Use this function to visualize in non-GUI mode

        plot_mode: string {'continuous', 'overlay'} if None, uses previously set plot_mode
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - only used for the 'overlay' plot_mode. If None, defaults to all sweeps
        xlim: float tuple. specify xlim for the plot. Default None
        ylim: float tuple. specify ylim for the plot. Default None
        show: boolean - if True, calls plt.show()
        """
        if not plot_mode:
            plot_mode = self.plot_mode
        x_matrix = recording.get_x_matrix(mode=plot_mode, sweeps=sweeps, channels=channels)  # 2D numpy array
        y_matrix = recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels)  # 3D numpy array
        c_len, s_len, _ = y_matrix.shape
        for c in range(c_len):
            for s in range(s_len):
                plt.plot(x_matrix[c, s, :], y_matrix[c, s, :], color=color, linewidth=linewidth)

        # add scatter plot of mini_df here##

        ######################################

        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        if show:
            plt.show()

    #############################
    # Evoked Recording Analysis #
    #############################

    def calculate_min_sweeps(self, recording, plot_mode=None, channels=None, sweeps=None, xlim=None):
        """
        returns minimum y-value from each sweep in each channel
        if the plot_mode is 'overlay', returns the minimum y-value for each sweep
        if the plot_mode is 'continuous', returns a single minimum y-value

        plot_mode: string {'continuous', 'overlay'} if None, uses previously set plot_mode
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - only used for the 'overlay' plot_mode. If None, defaults to all sweeps
        xlim: float tuple. restrict search for minimum y-value [left, right]
        """
        if not plot_mode:
            plot_mode = self.plot_mode
        if sweeps is None:
            sweeps = range(recording.sweep_count)
        if channels is None:
            channels = range(recording.channel_count)
        y_matrix = recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels,
                                               xlim=xlim)  # 3D numpy array
        mins = np.min(y_matrix, axis=2, keepdims=True)
        mins_std = np.std(mins, axis=1, keepdims=True)
        return mins, mins_std

    def calculate_max_sweeps(self, recording, plot_mode=None, channels=None, sweeps=None, xlim=None):
        """
        returns maximum y-value from each sweep in each channel
        if the plot_mode is 'overlay', returns the minimum y-value for each sweep
        if the plot_mode is 'continuous', returns a single minimum y-value per channel

        plot_mode: string {'continuous', 'overlay'} if None, uses previously set plot_mode
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - only used for the 'overlay' plot_mode. If None, defaults to all sweeps
        xlim: float tuple. restrict search for minimum y-value [left, right]
        """
        if not plot_mode:
            plot_mode = self.plot_mode
        y_matrix = recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels,
                                               xlim=xlim)  # 3D numpy array
        if sweeps is None:
            sweeps = range(recording.sweep_count)
        if channels is None:
            channels = range(recording.channel_count)
        maxs = np.max(y_matrix, axis=2, keepdims=True)
        maxs_std = np.std(maxs, axis=1, keepdims=True)
        return maxs, maxs_std

    ########################
    # Recording Adjustment #
    ########################

    def average_sweeps(self, recording, channels=None, sweeps=None, fill=0):
        """
        returns a 3D numpy array representing the average of specified sweeps in each channel

        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps
        fill: float - y-value to fill channels that will not be assessed. defaults to 0
        """
        # initialize matrix
        result = np.full((recording.channel_count, 1, recording.sweep_points),
                         fill_value=fill,
                         dtype=np.float)
        result[channels] = np.mean(recording.get_y_matrix(mode='overlay', sweeps=sweeps, channels=channels),
                                   axis=1,
                                   keepdims=True)
        return result

    def append_average_sweeps(self, recording, channels=None, sweeps=None, fill=0):
        """
        averages sweeps in each channel and stores the result in the recording attribute

        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps
        fill: float - y-value to fill channels that will not be assessed. defaults to 0
        """

        avg = self.average_sweeps(recording, channels=channels, sweeps=sweeps, fill=fill)
        recording.append_sweep(avg)

        return avg

    def subtract_baseline(self, recording, plot_mode='continuous', channels=None, sweeps=None, xlim=None, fixed_val=None):
        """
        subtracts baseline from each sweep. Baseline can be calculated as the mean of specified data points
        or a single value can be specified as a parameter

        plot_mode: string {'continuous', 'overlay'}
                - if 'continuous', a single baseline value is applied to all sweeps in a given channel
                - if 'overlay', a unique baseline value is applied for each sweep
        channels: list of int
                - if None, defaults to all channels
        sweeps: list of int
                - if None, defaults to all sweeps
        xlim: float tuple [left, right]
                - use this to limit the range of y-values to consider in baseline calculation
        fixed_val: float
                - provide this value if subtracting a fixed value from all specified sweeps and channels

        calculated baseline is subtracted from specified sweeps and channels in the recording attribute

        returns float numpy array baseline
        """
        if fixed_val is not None:
            baseline = fixed_val
        else:
            baseline = np.mean(recording.get_y_matrix(mode=plot_mode,
                                                           channels=channels,
                                                           sweeps=sweeps,
                                                           xlim=xlim),
                               axis=2,
                               keepdims=True)
        result = recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps) - baseline

        recording.replace_y_data(mode=plot_mode, channels=channels, sweeps=sweeps, new_data=result)

        return baseline

    def shift_y_data(self, recording, shift, plot_mode='continuous', channels=None, sweeps=None):
        """
        shifts y_data by specified amount

        shift: float or array. The dimensions must match dimension: (n_channels, n_sweeps, (1))
        plot_mode: string {'continuous', 'overlay'}. If continuous, all specified sweeps are concatenated into a 1D array per channel
        channels: list of int
        sweeps: list of int
        """
        result = recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps) - shift
        recording.replace_y_data(mode=plot_mode, channels=channels, sweeps=sweeps, new_data=result)

        return recording

    def filter_sweeps(self, recording, filter='Boxcar', params=None, channels=None, sweeps=None):
        """
        applies a specified filter to the y-data in specified sweeps and channels

        filter: string {'Boxcar'} (more will be added) - name of filter
        params: dict parameters specific to each filter type. See below for more details
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps

        filter 'Boxcar':
            see astropy.convolution.Box1DKernel for more details
            width: int - number of data points to use for boxcar filter
            if only a subset of sweeps are selected, y-values from selected sweeps are stitched together to form a continuous y-data sequence for the purpose of convolution
            At the edges of each sweep, the y-values from previous/next sweep may be used as if the data were continuous

            The first width/2 data points and last width/2 data points are not convolved to avoid


        """
        if filter == 'Boxcar':
            # https://danielmuellerkomorowska.com/2020/06/02/smoothing-data-by-rolling-average-with-numpy/
            width = int(params['width'])
            kernel = np.ones(width)/width
            for c in channels:
                ys=recording.get_y_matrix(mode='continuous', channels=[c], sweeps=sweeps)
                filtered=np.convolve(ys.flatten(), kernel, mode='same')
                filtered=np.reshape(filtered, (1,1,len(filtered)))
                filtered[:, :, :int(width / 2)] = ys[:, :, :int(width / 2)]
                filtered[:, :, -int(width / 2):] = ys[:, :, -int(width / 2):]
                recording.replace_y_data(mode='continuous', channels=[c], sweeps=sweeps, new_data=filtered)
            # k = convolution.Box1DKernel(width=width)
            # for c in channels:
            #     # apply filter
            #     ys = self.recording.get_y_matrix(mode='continuous',
            #                                      channels=[c],
            #                                      sweeps=sweeps)
        #         filtered = convolve(ys.flatten(), k)
        #
        #         # reshape filtered data to 3D numpy array
        #         filtered = np.reshape(filtered, (1, 1, len(filtered)))
        #
        #         # # even out the edge cases
        #         filtered[:, :, :int(width / 2)] = ys[:, :, :int(width / 2)]
        #         filtered[:, :, -int(width / 2):] = ys[:, :, -int(width / 2):]
        #
        #         self.recording.replace_y_data(mode='continuous', channels=[c], sweeps=sweeps, new_data=filtered)
        # return None
        return recording

    def find_closest_sweep_to_point(self, recording, point, xlim=None, ylim=None, height=1, width=1, radius=np.inf,
                                    channels=None, sweeps=None):
        """
        returns the sweep number that is closest to a given point that satisfies the given radius
        assumes 'overlay' plot mode

        point: float tuple (x, y)
        xlim: float tuple (left, right) - if specified, used to normalize the x-y ratio
        ylim: float tuple (bottom, top) - if specified, used to normalize the x-y ratio
        height: int - pixel height of the display window. Defaults to 1. Used to normalize the x-y ratio
        width: int - pixel width of the display window. Defaults to 1. Used to normalize the x-y ratio
        radius: float - maximum radius (in x-axis units) to search from point
        channels: list of int - channels to apply the search. If None, defaults to all channels
        sweeps: list of int - sweeps to apply the search. If None, defaults to all sweeps

        returns int channel index, int sweep index
        """

        try:
            xy_ratio = (xlim[1] - xlim[0]) / (ylim[1] - ylim[0]) * height / width
        except Exception as e:  # xlim and/or ylim not specified
            xy_ratio = 1
        if channels is None:
            channels = range(recording.channel_count)
        if sweeps is None:
            sweeps = range(recording.sweep_count)
        min_c = None
        min_s = None
        min_i = None
        min_d = np.inf
        for c in channels:
            for s in sweeps:
                d, i, _ = point_line_min_distance(
                    point,
                    recording.get_xs(mode='overlay', sweep=s, channel=c),
                    recording.get_ys(mode='overlay', sweep=s, channel=c),
                    sampling_rate=recording.sampling_rate,
                    radius=radius,
                    xy_ratio=xy_ratio)
                try:
                    if d <= min_d:
                        min_c = c
                        min_s = s
                        min_d = d
                        min_i = i
                except:
                    pass
        if min_c and min_s:
            return min_c, min_s
        return None, None

    #################
    # Mini Analysis #
    #################

    def interrupt(self):
        """
        used to interrupt the while loop in find_mini_auto
        only use when the find_mini_auto is threaded
        """
        self.stop = True

    def find_mini_auto(self,
                       xlim=None,
                       xs=None,
                       ys=None,
                       recording=None,
                       x_sigdig=6,
                       sampling_rate=None,
                       channel=0,
                       sweeps=None,
                       auto_radius=None,
                       kernel=None,
                       stride=None,
                       direction=1,
                       reference_df=True,
                       progress_bar=None,
                       **kwargs
                       ):
        """
        Searches for mini events and populates mini_df attribute within the recording attribute data

        If multiple searches are performed on the same xs and ys data, it is recommended to
        store the xs and ys data outside of the Analyzer and pass them as arguments to speed up
        the search time. If ys and xs are not provided as arguments, continuous sequence of
        xs and ys data are created on the fly from the recording data every function call.


        Args:
            xlim: float tuple representing the search window limits. [left, right] If None, defaults to entire dataset
            xs: float numpy array representing the x-values of the recording sequence.
                If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
            ys: float numpy array representing the y-values of the recording sequence.
                If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
            x_sigdig: int number of significant digit for the x-value. Used to round calculations
            sampling_rate: float - sampling rate of xs
            channel: int indicating the channel number to analyze. Only required if xs and ys are not provided
            sweeps: list of int indicating the sweeps to analyzer. If left None, all sweeps will be considered
            auto_radius: x-axis window to be considered per iteration in ms.
                If left empty, defaults to the values indicated in kernel and stride parameters
            kernel: float representing the x-axis window to consider per iteration.
                The most extreme data point within the kernel will be tested as a candidate mini peak.
                Should be smaller than the shortest interval between two minis within the recording.
                Larger kernel size can speed up the search.
            stride: int representing the number of data points to shift every iteration.
                Recommended to be less than kernel.
                Larger strides can speed up the search.
            direction: int
            reference_df: bool whether to check for duplicates in mini_df and update newly found minis to mini_df
            progress_bar: object pass a progress bar object. The value of the progressbar must be updatable using
                progress_bar['value'] = int
            **kwargs: see list of parameters in analyze_candidate_mini()

        Returns:
            pandas DataFrame containing the information on search parameters and mini characteristics.
            In addition to the search parameters passed as arguments, the following data are included
            in the result:
                #### list columns here
        """
        show_time = False
        self.print_time('start auto', show_time)
        self.stop=False
        if xs is None or ys is None:
            if recording is None:
                return None # cannot analyze
        if xs is None:
            xs = recording.get_x_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        if ys is None:
            ys = recording.get_y_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        else:
            ys = ys.copy()  # make a copy to edit
        try:
            xlim_idx = (search_index(xlim[0], xs, sampling_rate), search_index(xlim[1], xs, sampling_rate))
        except:
            xlim_idx = (0, len(xs))

        if auto_radius is not None:
            if sampling_rate is None:
                sampling_rate = 1/np.mean(xs[1:5]-xs[0:4])
            elif sampling_rate == 'auto':
                try:
                    sampling_rate = recording.sampling_rate
                except:
                    sampling_rate = 1 / np.mean(xs[1:5] - xs[0:4])
            kernel = int(auto_radius/1000*sampling_rate)
        if stride is None:
            stride = int(kernel/2)

        # calculate intervals for progres bar
        increment = (xlim_idx[1] - xlim_idx[0])/20
        pb_idx = 0

        start_idx = xlim_idx[0]
        end_idx = start_idx + kernel
        if progress_bar:
            total = xlim_idx[1] - xlim_idx[0]
            start = start_idx
            progress_bar['value'] = 0
            progress_bar.update()
        hits = []
        prev_peak = None
        while start_idx < xlim_idx[1] and not self.stop:
            peak_idx = self.find_peak_recursive(xs, ys, start=start_idx, end=end_idx, direction=direction)
            self.print_time('find peak', show_time)
            if peak_idx is not None:
                mini = self.analyze_candidate_mini(
                    xs=xs,
                    ys=ys,
                    peak_idx=peak_idx,
                    x_sigdig=x_sigdig,
                    sampling_rate=sampling_rate,
                    channel=channel,
                    direction=direction,
                    reference_df=reference_df,
                    prev_peak = prev_peak,
                    **kwargs
                )
                self.print_time('analyze mini', show_time)
                if mini['success']:
                    self.print_time('pre append', show_time)
                    mini['xlim_idx_L']=start_idx
                    mini['xlim_idx_R']=end_idx
                    hits.append(mini)
                    start_idx = peak_idx + 1
                    prev_peak = mini
                    self.print_time('do append mini', show_time)
                else:
                    if mini['failure'] == 'Mini was previously found':
                        # make sure the failure code matches here
                        prev_peak = mini
                        start_idx = peak_idx + 1
                    else:
                        start_idx += stride
                    self.print_time("don't append mini", show_time)

            else:
                start_idx += stride
                pass
            # start_idx += stride
            end_idx = min(start_idx + kernel, xlim_idx[1])
            try:
                # if start_idx > increment:
                #     progress_bar['value'] = progress_bar['value'] + 5
                #     progress_bar.update()
                #     progress_bar.after(5, None)
                #     increment += increment
                progress_bar['value'] = int((start_idx - start) / total * 100)
                progress_bar.update()
            except:
                pass
            self.print_time('end iter', show_time)
        new_df = DataFrame.from_dict(hits)
        if reference_df:
            if len(self.mini_df.index)>0:
                self.mini_df = pd.concat([self.mini_df,new_df]) # indexing is NOT UNIQUE
            else:
                self.mini_df = new_df
        return new_df


    def find_mini_manual(self,
                         xlim: tuple = None,
                         xlim_idx: tuple = None,
                         xs: np.ndarray = None,
                         ys: np.ndarray = None,
                         recording=None,
                         x_sigdig: int = 6,
                         sampling_rate: float = None,
                         channel=0,
                         sweeps=None,
                         direction=1,
                         reference_df=True,
                         offset: int = 0,
                         **kwargs
                         ):
        """
        Searches for a biggest mini event within xlim

        If ys and xs are not provided as arguments, continuous sequence of
        xs and ys data are created on the fly from the recording data every function call.

        Args:
            xlim: float tuple representing the search window limits. [left, right]
            xs: float numpy array representing the x-values of the recording sequence.
                If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
            ys: float numpy array representing the y-values of the recording sequence.
                If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
            x_sigdig: int number of significant digit for the x-value. Used to round calculations
            sampling_rate: float - sampling rate of xs
            channel: int indicating the channel number to analyze. Only required if xs and ys are not provided
            sweeps: list of int indicating the sweeps to analyzer. If left None, all sweeps will be considered
            direction: int
            reference_df: bool whether to check for duplicates in mini_df and update newly found minis to mini_df
            offset: used to change the indexing of the xs and ys arrays
            **kwargs: see list of parameters in find_single_mini()

        Returns:
            pandas DataFrame containing the information on search parameters and mini characteristics.
            In addition to the search parameters passed as arguments, the following data are included
            in the result:
                #### list columns here
        """
        if xs is None or ys is None:
            if recording is None:
                return None # insufficient data
        if xs is None:
            xs = recording.get_x_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        if ys is None:
            ys = recording.get_y_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        else:
            ys = ys.copy()
        if xlim_idx is None:
            if xlim is None:
                return {'success':False, 'failure':'insufficient info'}
            try:
                xlim_idx = (search_index(xlim[0], xs, sampling_rate), search_index(xlim[1], xs, sampling_rate))
            except:
                return {'success': False, 'failure':'xlim could not be found'}  # limits of the search window cannot be determined

        peak_idx = self.find_peak_recursive(xs, ys, start=xlim_idx[0], end=xlim_idx[1], direction=direction)
        if peak_idx is not None:
            mini = self.analyze_candidate_mini(
                xs=xs,
                ys=ys,
                peak_idx=peak_idx,
                x_sigdig=x_sigdig,
                sampling_rate=sampling_rate,
                channel=channel,
                direction=direction,
                reference_df=reference_df,
                offset=offset,
                **kwargs
            )
            mini['xlim_idx_L'] = xlim_idx[0]
            mini['xlim_idx_R'] = xlim_idx[1]
            if reference_df and mini['success']:
                self.mini_df = self.mini_df.append(Series(mini),
                                                   ignore_index=True,
                                                   sort=False)
                self.mini_df = self.mini_df.sort_values(by='t')
            return mini
        return {'success': False, 'failure':'peak could not be found', 'xlim_idx':xlim_idx}

    def find_peak_recursive(self,
                            xs,
                            ys,
                            start,
                            end,
                            direction=1):
        """
        recursively seeks local extremum within a given index range
        Args:
            xs: float 1D numpy array - x-values
            ys: float 1D numpy array - y-values
            start: int - index within xs,ys to start the search
            end: int - index within xs,ys to end the search
                [start, end)
            direction: int {-1, 1} - direction of the expected peak. -1 for current (local minimum), 1 for potential (local maximum). Default 1
        Returns:
            peak_idx: int where the peak data point is located
            peak_val: value at peak_idx
        """
        FUDGE = 10  # margin at the edge of search window required to be considered peak (used to avoid edge cases)
        if end - start < FUDGE * 2:
            return None  # the search window is too narrow
        try:
            peak_y = max(ys[start:end] * direction)
        except:
            print(ys[start:end] * direction)
            print(ys[start:end])
            print(len(ys))
            print(f'peak search error, start:end: {start, end}')
        peaks = np.where(ys[start:end] * direction == peak_y)[0] + start  # get list of indices where ys is at peak
        peak_idx = peaks[int(len(peaks) / 2)]  # select the middle index of the peak

        # check if the peak is at the edge of the search window
        # if the peak is at the edge, the slope could continue further beyond the window
        # recursively narrow the search window and look for another local extremum within the new window

        if peak_idx < start + FUDGE:  # the local extremum is at the left end of the search window
            return self.find_peak_recursive(xs, ys, start + FUDGE, end, direction)
        if peak_idx > end - FUDGE:  # the local extremum is at the right end of the search window
            return self.find_peak_recursive(xs, ys, start, end - FUDGE, direction)
        return peak_idx

    def find_mini_start(self,
                        peak_idx: int,
                        ys: np.ndarray,
                        lag: int = 100,
                        delta_x: int = 400,
                        direction: int = 1) -> tuple:
        """
        Calculates estimated baseline value and the index of start of a mini event

        Args:
            peak_idx: int representing the index at which the candiate mini peak was found in ys array
            ys: 1D numpy array representing the y-value to seearch for mini
            lag: int representing the number of datapoints averaged to find the trailing average. Default 100
                The result of the trailing average is used to estamate the baseline.
                The point at which the mini data crosses the trailing average is considered the start of the mini.
            delta_x: int representing the number of datapoints before peak to reference as the baseline.
                Baseline y-value is calculated as: mean of [peak_idx - delta_x - lag:peak_idx - delta_x)
            direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
                Default 1
        Returns:
            idx: index where ys data point reaches baseline (start of mini)
            baseline: estimated baseline value. This is the trailing average of lag data points
                    prior to the baseline_idx in ys
        """
        # initialize search at the index previous to the peak
        # left of peak for start of mini
        idx = peak_idx - 1

        # NB: by multiplying the direction, the ys values will always peak in the positive direction
        if idx < lag:
            return None, None  # there are less than lag data points to the left of starting index

        # baseline = np.mean(ys[peak_idx - delta_x -lag: peak_idx - delta_x])  # average sometime before the peak
        #
        # while idx > lag:
        #     if ys[idx] * direction <= baseline * direction:
        #         break
        #     idx -= 1
        # else:
        #     return None, baseline  # couldn't find the corresponding datapoint
        # return idx, baseline

        if delta_x == 0:
            tma = np.mean(ys[idx - lag:idx])*direction # avg lag data points - trailing moving average
            while lag <= idx:
                idx -= 1
                tma = tma + (ys[idx - lag] - ys[idx]) * direction / lag # update trailing avg
                if tma >= ys[idx] * direction:
                    return idx, tma * direction
            else:
                return None, None

        # estimate baseline using avg data points at delta_x before peak
        tma = np.mean(ys[int(peak_idx-delta_x):int(peak_idx - delta_x+lag)])*direction
        while idx > peak_idx - delta_x:
            if tma >= ys[idx] * direction:
                return idx, tma*direction
            idx -= 1
        else:
            return None, None


        # cma = np.mean(ys[idx - int(lag/2):idx] * direction) # central moving average
        #
        # update_tma=True
        # update_cma=True
        #
        # tma_idx = idx
        # cma_idx = idx
        # while lag <= idx:
        #     idx -= 1
        #     if update_cma:
        #         next_cma = cma + (ys[idx - int(lag/2)] + ys[idx+int(lag/2)]) * direction/ (int(lag/2)*2)
        #         if next_cma > cma: # heading backwards in a downwards slope
        #             update_cma = False
        #             cma_idx = idx + 1
        #         else:
        #             cma = next_cma
        #     if update_tma:
        #         tma = tma + (ys[idx - lag] - ys[idx]) * direction / lag # update trailing avg
        #         # equivalent to np.mean(ys[base_idx-lag: base_idx])
        #         if tma >= ys[idx] * direction: # y-value dips below the estimated baseline
        #             update_tma = False
        #             tma_idx = idx + 1
        #     if not update_cma and not update_tma:
        #         break
        # else:
        #     return None, None # could not find baseline until base_idx < lag or base_idx > len(ys) - lag
        # print(f'cma: {cma_idx}, tma: {tma_idx}')
        # return min(cma_idx, tma_idx), min(tma, cma) * direction

    def find_mini_end(self,
                      peak_idx: int,
                      ys: np.ndarray,
                      lag: int = 100,
                      direction: int = 1) -> tuple:
        """
        Calculates the baseline value and estimated end index of a mini event
        Args:
            peak_idx: int representing the index at which the candiate mini peak was found in ys array
            ys: 1D numpy array representing the y-value to seearch for mini
            lag: int representing the number of datapoints averaged to find the trailing average. Default 100
                The result of the trailing average is used to estamate the baseline.
                The point at which the mini data crosses the trailing average is considered the start of the mini.
            direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
                Default 1
        Returns:
            idx: index where ys data point reaches baseline (end of mini)
            baseline: estimated baseline value. This is the trailing average of lag data points
                    ahead of idx in ys

        """
        # initialize search at the index after the peak
        idx = peak_idx + 1

        # NB: by multiplying the direction, the ys values will always peak in the positive direction
        if idx > len(ys) - lag:
            return None, None  # there are less than lag data points to the right of the starting index
        tma = np.mean(ys[idx:idx+lag]) * direction  # avg lag data points - trailing moving average
        while idx <= len(ys) - lag:
            idx += 1
            tma = tma + (ys[idx + lag] - ys[idx]) * direction / lag  # update trailing avg
            if tma >= ys[idx] * direction:
                return idx, tma * direction
        else:
            return None, None

        # tma = np.mean(ys[idx:idx + lag] * direction)  # avg lag data points, trailing moving average
        # cma = np.mean(ys[idx - int(lag / 2): idx + int(lag / 2)])  # central moving average
        #
        # update_tma = True
        # update_cma = True
        #
        # tma_idx = idx
        # cma_idx = idx
        # while lag <= idx <= len(ys) - lag:
        #     if update_cma:
        #         next_cma = cma + (ys[idx + int(lag / 2)] - ys[idx - int(lag / 2)]) * direction / (int(lag / 2) * 2)
        #         if next_cma > cma:  # upward slope
        #             update_cma = False
        #             cma_idx = idx - 1
        #         else:
        #             cma = next_cma
        #     if update_tma:
        #         tma = tma + (ys[idx + lag] - ys[idx]) * direction / lag  # update trailing avg
        #         # equivalent to np.mean(ys[base_idx-lag: base_idx])
        #         if tma >= ys[idx] * direction and next_cma >= cma:  # y-value dips below the estimated baseline
        #             update_tma = False
        #             tma_idx = idx - 1
        #     if not update_cma and not update_tma:
        #         break
        #     idx += 1
        # else:
        #     return None, None  # could not find baseline until base_idx < lag or base_idx > len(ys) - lag
        # return max(cma_idx, tma_idx), min(tma, cma) * direction

    def find_mini_halfwidth(self,
                                 amp: float,
                                 xs: np.ndarray,
                                 ys: np.ndarray,
                                 peak_idx: int,
                                 baseline: float,
                                 direction: int = 1,
                                 prev_mini_t:float=None,
                                 prev_mini_A: float=None,
                                 prev_mini_decay: float=None,
                                prev_mini_decay_baseline:float=None,
                                 prev_mini_baseline: float=None,
                                 ):
        """
        calculates the halfwidth of a mini event

        Args:
            amp: float representing the estimated amplitude of the mini. Used to calculate 50% amplitude
            ys: float numpy array of the y-value data
            xs: float numpy array of the x-value data
            start_idx: int representing the index in xs and ys that marks the start of the mini event
            end_idx: int representing the index in xs and ys that marks the end of the mini event
            peak_idx: int representing the index in xs and ys that marks the peak of the mini event
            baseline: float - the estimated baseline for the mini event
            direction: int {-1, 1}
        Returns:
            halfwidth_start_index: int representing the index at which y-value is 50% of the amplitude
            halfwidth_end_index: int reperesenting the index at which y-value is 50% of the amplitude
            halfwidth: time it takes for the mini to reach 50% of amplitude and return to 50% of amplitude
        """
        if prev_mini_A is not None:
            prev_mini_t_ms = prev_mini_t * 1000
            y_data = ys * direction - single_exponent_constant((xs * 1000 - prev_mini_t_ms), prev_mini_A,
                                                  prev_mini_decay, prev_mini_decay_baseline) - prev_mini_baseline * direction
        else:
            y_data = (ys - baseline) * direction
        left_idx = np.where(y_data[:peak_idx] <= (amp * 0.5) * direction)
        if len(left_idx[0]):
            left_idx = left_idx[0][-1]
        else:
            left_idx = None
        right_idx = np.where(y_data[peak_idx:] <= (amp * 0.5) * direction)
        if len(right_idx[0]):
            right_idx = right_idx[0][0] + peak_idx
        else:
            right_idx = None
        return left_idx, right_idx  # pick the shortest length
    def find_first_point_at_p(self,
                              amp: float,
                              p:float,
                              xs: np.ndarray,
                              ys:np.ndarray,
                              start_idx:int,
                              end_idx: int,
                              percent: float,
                              baseline: float,
                              direction: int=1):
        """
        traverses xs and ys to find first data point after start_idx and before end_idx that reaches p percent of amplitude
        from baseline

        amp: amplitude in float. should be positive float
        """
        forward = True
        pass
    def fit_mini_decay(self,
                       xs: np.ndarray,
                       ys: np.ndarray,
                       sampling_rate:float,
                       end_idx: int,
                       amplitude: float = None,
                       decay_guess: float = None,
                       direction: int=1,
                       baseline: float=0.0,
                       prev_mini_decay: float=None,
                       prev_mini_A: float=None,
                       prev_mini_decay_baseline: float=None,
                       prev_mini_baseline: float=None,
                       prev_mini_t: int=None
                       ):
        """
        decay fitting, takes into account prev mini
        xs: np.ndarray of the data segment to be fitted - start = peak, and end = end of fit
        ys: np.ndarray of the data segment to be fitted -
        sampling_rate: in Hz
        start_idx: int index within xs and ys of the peak
        end_idx: int index within xs and ys of the end of mini
        direction: int {-1, 1}
        prev_mini_const: if compound mini, the decay function constant (tau) of the previous mini
        prev_mini_A: if compound mini, the amplitude (A) of the previous mini
        prev_mini_peak_t: previous peak's t
        num_points: max number of points to fit
        """

        x_data = (xs-xs[0]) * 1000
        # print(x_data)

        if prev_mini_t is not None: # compound mini
            prev_mini_t_ms = prev_mini_t * 1000
            y_data = ys *direction - single_exponent_constant((xs*1000-prev_mini_t_ms), prev_mini_A, prev_mini_decay, prev_mini_decay_baseline) - prev_mini_baseline*direction

        else:
            y_data = (ys - baseline) * direction  # baseline subtract
        y_data[end_idx:] = 0

        p0 =[1]*2
        if amplitude is not None:
            p0[0] = amplitude
        if decay_guess is not None:
            p0[1] = decay_guess

        # initialize weights for gradient descent
        y_weight = np.empty(len(y_data))
        y_weight.fill(10)
        y_weight[0] = 0.001
        # fit
        results = curve_fit(single_exponent,
                            x_data,
                            y_data,
                            p0=p0,
                            sigma=y_weight,
                            absolute_sigma=True,
                            maxfev=15000)
        a = results[0][0]
        t = results[0][1]
        # d = results[0][2]
        d=0
        # print((a, t, d))

        return a, t, d



    def calculate_mini_decay(self,
                             xs: np.ndarray,
                             ys: np.ndarray,
                             sampling_rate: float,
                             start_idx: int,
                             end_idx: int,
                             num_points: int,
                             direction: int = 1,
                             baseline: float = 0.0):
        """
        calculates decay of a mini

        Args:
            xs: float numpy array of the x values
            ys: float numpy array of the y values
            start_idx: int representing the index to start the fit (should be peak of mini)
            end_idx: int reprsenting the index to end the mini
            num_points: int number of datapoints to use for fit
            direction: int {-1, 1}
            baseline: float to subtract from ys

        Returns:
            a, t, d: float, single exponential function parameters
            decay_constant_idx: int representing the index of xs, ys where y-value is e^-1 of max amplitude

        """

        ########## is it better the constrain a? ##############

        x_data = (xs[start_idx:min(start_idx + num_points, len(xs))] - xs[start_idx]) * 1000
        # print(x_data)
        y_data = (ys[start_idx:min(start_idx + num_points, len(xs))] - baseline) * direction
        y_data[end_idx - start_idx:] = 0

        # initialize weights for gradient descent
        y_weight = np.empty(len(y_data))
        y_weight.fill(10)
        y_weight[0] = 0.001

        # fit
        results = curve_fit(single_exponent,
                            x_data,
                            y_data,
                            sigma=y_weight,
                            absolute_sigma=True,
                            maxfev=15000)
        # print(results[0])
        a = results[0][0]
        t = results[0][1]
        # d = results[0][2]
        # print((a, t, d))
        decay_constant_idx = search_index(t, x_data, sampling_rate) + start_idx  # offset to start_idx

        return a, t, decay_constant_idx

    def analyze_candidate_mini(self,
                               xs,
                               ys,
                               peak_idx=None,
                               peak_t=None,
                               x_sigdig=None,
                               sampling_rate=None,
                               channel=0,
                               reference_df=True,
                               reanalyze=False,
                               ## parameters defined in GUI ##
                               direction=1,
                               delta_x_ms=None,
                               delta_x=0,
                               lag_ms=None,
                               lag=100,
                               ## compound parameters defined in GUI ##
                               compound=1,
                               p_valley=50,
                               max_compound_interval=0,
                               min_peak2peak_ms=0,
                               extrapolate_hw=0,
                               ## decay algorithm parameters ##
                               decay_algorithm = '% amplitude',
                               decay_p_amp = 0.37,
                               decay_ss_min = 0.0,
                               decay_ss_max = 10,
                               decay_ss_interval = 0.01,
                               decay_best_guess = 4,
                               decay_max_interval = 40,
                               decay_max_points=None,
                               ## filtering parameters defined in GUI ##
                               min_amp=0.0,
                               max_amp=np.inf,
                               min_rise=0.0,
                               max_rise=np.inf,
                               min_hw=0.0,
                               max_hw=np.inf,
                               min_decay=0.0,
                               max_decay=np.inf,
                               min_drr=0.0,
                               max_drr=np.inf,
                               min_s2n = 0,
                               max_s2n = np.inf,
                               #################################
                               offset=0,
                               y_unit='mV',
                               x_unit='s',
                               ##################################
                               prev_peak_idx=None,
                               prev_peak=None,
                               **kwargs
                               ):
        """
            peak_idx: int - Index within the xs data corresponding to a peak.
            peak_t: float - if provided, takes precedence over peak_idx
            x_sigdig: significant digits in x
            sampling_rate: sampling rate of xs in Hz
            direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
            delta_x_ms: float, prioritized
            delta_x: int
            lag_ms: float representing the x-axis window to be averaged to estimate the baseline and start of the mini.
                If given, this parameter is prioritized over the lag parameter
            lag: int indicating the number of data points used to calculate the baseline.
                See calculate_mini_baseline() for algorithm on baseline estimation.
                If None, lag_ms must be provided
            direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
            min_amp: float indicating the minimum amplitude required in a candidate mini.
            max_amp: float indicating the maximum amplitude accepted in a candidate mini.
            min_rise: float indicating the minimum rise required in a candidate mini.
            max_rise: float indicating the maximum rise accepted in a candidate mini.
            min_hw: float indicating the minimum halfwidth required in a candidate mini.
                See calculate_mini_halfwidth() for algorithm on halfwidth calculation
            max_hw: float indicating the maximum halfwidth accepted in a candidate mini.
                See calculate_mini_halfwidth() for algorithm on halfwidth calculation
            min_decay: float indicating the minimum decay constant required in a candidate mini.
                See calculate_mini_decay() for algorithm on decay constant calculation.
            max_decay: float indicating the maximum decay constant accepted in a candidate mini.
                See calculate_mini_decay() for algorithm on decay constant calculation.
            reference_df: bool indicating whether to compare the results against previously found minis stored in mini_df.
                Must be set to True for compound analysis.
            reanalyze: bool indicating whether the candidate mini is already in mini_df
                Set to True if reanalyzing a previously found mini.
                If set to False, previously found minis will be ignored.

        """

        show_time = False
        # perform conversions
        if sampling_rate == 'auto':
            sampling_rate = 1 / np.mean(xs[1:5] - xs[0:4])
        # convert lag_ms to lag
        if lag_ms is not None:
            lag = int(lag_ms/1000*sampling_rate)
        if decay_max_interval is not None:
            decay_max_points = int(decay_max_interval/1000*sampling_rate)
        if delta_x_ms is not None:
            delta_x = int(delta_x_ms/1000*sampling_rate)
        if peak_t:
            peak_idx = search_index(peak_t, xs, sampling_rate)
        elif peak_idx:
            peak_idx = int(peak_idx) # make sure is int
        if peak_t is None and peak_idx is None:
            return {'success':False, 'failure':'peak idx not provided'}
        min_peak2peak = min_peak2peak_ms/1000*sampling_rate
        if prev_peak:
            try:
                prev_peak_idx = prev_peak['peak_idx']
            except:
                prev_peak = None
        elif prev_peak_idx: # had index provided
            try:
                prev_peak = self.mini_df.loc[(self.mini_df['peak_idx'] == prev_peak_idx) &
                                         (self.mini_df['channel'] == channel)].squeeze().to_dict()
            except:
                prev_peak = None
        # initiate mini data dict
        mini = {'direction': direction, 'lag': lag, 'delta_x': delta_x, 'channel': channel, 'min_amp': min_amp,
                'max_amp': max_amp,
                'min_rise': min_rise, 'max_rise': max_rise, 'min_hw': min_hw, 'max_hw': max_hw, 'min_decay': min_decay,
                'min_s2n': min_s2n, 'max_s2n': max_s2n,
                'max_decay': max_decay, 'decay_max_points': decay_max_points, 'decay_max_interval': decay_max_interval,
                'datetime': datetime.now().strftime('%m-%d-%y %H:%M:%S'), 'failure': None, 'success': True,
                't': xs[peak_idx], 'peak_idx': peak_idx + offset, 'compound': False,
                'baseline_unit': y_unit}
        max_compound_interval_idx = max_compound_interval * sampling_rate/1000
        if x_unit in ['s', 'sec', 'second', 'seconds']:
            mini['decay_unit'] = mini['rise_unit'] = mini['halfwidth_unit'] = 'ms'
        else:
            mini['decay_unit'] = mini['rise_unit'] = mini['halfwidth_unit'] = x_unit + 'E-3'
        mini['amp_unit'] = mini['stdev_unit'] = y_unit


        # extract peak datapoint
        if x_sigdig is not None:
            mini['t'] = round(mini['t'], x_sigdig)  # round the x_value of the peak to indicated number of digits

        # check if the peak is duplicate of existing mini data
        if reference_df and not reanalyze:
            try:
                if mini['t'] in self.mini_df.t.values:
                    mini = self.mini_df.loc[(self.mini_df['t'] == mini['t']) &
                                                 (self.mini_df['channel'] == channel)].squeeze().to_dict()
                    mini['success'] = False
                    mini['failure'] = 'Mini was previously found'
                    return mini
            except Exception as e:  # if df is empty, will throw an error
                pass


        # store peak coordinate
        mini['peak_coord_x'] = xs[peak_idx]
        mini['peak_coord_y'] = ys[peak_idx]

        self.print_time('setup', show_time)
        baseline_idx, mini['baseline'] = self.find_mini_start(peak_idx=peak_idx,
                                                              ys=ys,
                                                              lag=lag,
                                                              delta_x=delta_x,
                                                              direction=direction)

        # check if baseline calculation was successful
        if baseline_idx is None:  # not successful
            mini['success'] = False
            mini['failure'] = 'Baseline could not be found'
            return mini
        if delta_x is None or delta_x == 0:
            base_idx = (baseline_idx - lag, baseline_idx)
        else:
            base_idx = (int(peak_idx - delta_x - lag/2), int(peak_idx - delta_x+lag/2))
        mini['base_idx_L'] = base_idx[0] + offset
        mini['base_idx_R'] = base_idx[1] + offset
        self.print_time('baseline', show_time)
        ####### search baseline #######
        # find baseline/start of event
        mini['start_idx'] = baseline_idx + offset

        if reference_df and len(self.mini_df.index) > 0 or prev_peak is not None:
            # try:
            # find the peak of the previous mini
            # peak x-value must be stored in the column 't'
            # check that the channels are the same
            # try:
            try:
                prev_peak_candidate_idx = self.mini_df.loc[(self.mini_df['channel'] == channel) & (
                                self.mini_df['t'] < mini['t'])].peak_idx
                prev_peak_candidate_idx = max(prev_peak_candidate_idx)
            except:
                prev_peak_candidate_idx = None

            if prev_peak_candidate_idx is not None:
                # check if provided peak is closer
                if (prev_peak_idx is not None and prev_peak_idx < prev_peak_candidate_idx) or prev_peak_idx is None:
                    prev_peak_idx = prev_peak_candidate_idx

                    prev_peak = self.mini_df.loc[(self.mini_df['peak_idx'] == prev_peak_idx) &
                                             (self.mini_df['channel'] == channel)].squeeze().to_dict()
            if prev_peak is not None:
                prev_peak_idx_offset = int(prev_peak['peak_idx']) - offset
                #check if previous peak has decayed sufficiently
                if compound:
                    if prev_peak_idx_offset + max_compound_interval*sampling_rate/1000> peak_idx:
                        # current peak is within set compound interval from the previous peak
                        mini['compound'] = True
                        prev_t = prev_peak['t']
                        mini['prev_t'] = prev_t
                        mini['prev_peak_idx'] = prev_peak['peak_idx']
                        if prev_peak_idx_offset < 0 or prev_peak_idx_offset > len(ys):  # not sufficient datapoints
                            mini['success'] = False
                            mini['failure'] = 'The compound mini could not be analyzed - need more data points'
                        if min((ys[prev_peak_idx_offset:peak_idx]-prev_peak['baseline']) * direction) > prev_peak[
                            'amp'] * direction * p_valley / 100:
                            mini['success'] = False
                            mini['failure'] = 'Minimum peak_to_valley % not reached for the previous mini'
                            return mini
                        mini['prev_baseline'] = prev_peak['baseline']
                        mini['prev_decay_const'] = prev_peak['decay_const']
                        mini['prev_decay_A'] = prev_peak['decay_A']
                        try:
                            mini['prev_decay_baseline'] = prev_peak['decay_baseline']
                        except:
                            mini['prev_decay_baseline'] = prev_peak['baseline']

                        # extrapolate start from previous decay
                        y_decay = single_exponent((xs[prev_peak_idx_offset:peak_idx+1]-xs[prev_peak_idx_offset])*1000, mini['prev_decay_A'], mini['prev_decay_const'])  + mini['prev_baseline'] * direction
                        try:
                            baseline_idx_ex = np.where(y_decay >= ys[prev_peak_idx_offset:peak_idx+1]*direction)[0][-1] + prev_peak_idx_offset
                        except:
                            baseline_idx_ex = None
                        # find where the 'min' valley value is between previous peak and current peak
                        baseline_idx_min = np.where(ys[prev_peak_idx_offset:peak_idx]*direction == min(ys[prev_peak_idx_offset:peak_idx] * direction))[0][0]+prev_peak_idx_offset
                        # update start_idx
                        try:
                            baseline_idx = max(baseline_idx_ex, baseline_idx_min)
                        except:
                            baseline_idx = baseline_idx_min
                        mini['start_idx'] = baseline_idx + offset
                        # extrapolate baseline at peak from previous decay
                        mini['baseline'] = single_exponent((xs[peak_idx] - xs[prev_peak_idx_offset])*1000,
                                                           mini['prev_decay_A'],
                                                           mini['prev_decay_const']) * direction + mini['prev_baseline']# get the extrapolated baseline value
                        self.print_time('reference extrapolation', show_time)
            # except Exception as e:
            #     print('decay extrapolation')
            #     print(e)
            #     pass
        self.print_time('reference', show_time)



        mini['amp'] = (mini['peak_coord_y'] - mini['baseline'])  # signed
        # store coordinate for start of mini (where the plot meets the baseline)
        mini['start_coord_x'] = xs[baseline_idx]
        mini['start_coord_y'] = ys[baseline_idx]

        if min_amp and (mini['amp'] * direction) < min_amp:
            mini['success'] = False
            mini['failure'] = 'Min amp not met'
            return mini

        if max_amp and mini['amp'] * direction > max_amp:
            mini['success'] = False
            mini['failure'] = 'Max amp exceeded'
            return mini
        self.print_time('amp', show_time)

        ####### calculate stdev ########
        mini['stdev'] = np.std(ys[max(0, baseline_idx - lag):baseline_idx])
        # else:
        #     mini['stdev'] = None
        #     if (min_s2n and min_s2n > 0) or (max_2n and max_s2n < np.inf): # cannot filter
        #         mini['success'] = False
        #         mini['failure'] = 'Not enough data to calculate stdev of baseline'
        #         return mini
        if mini['stdev'] and min_s2n and mini['amp']*direction/mini['stdev'] < min_s2n:
            mini['success'] = False
            mini['failure'] = 'Min signal to noise ratio not met'
            return mini
        if mini['stdev'] and max_s2n and mini['amp']*direction/mini['stdev'] > max_s2n:
            mini['success'] = False
            mini['failure'] = 'Max signal to noise exceeded'
            return mini
        ####### calculate end of event #######
        next_peak_idx = None
        if compound:
            next_search_start = np.where((ys[int(peak_idx+min_peak2peak):int(peak_idx+max_compound_interval_idx)] - mini['baseline'])*direction < mini['amp'] * p_valley /100 * direction)
            if len(next_search_start[0]>0):
                next_peak_idx = self.find_peak_recursive(xs=xs,
                                                         ys=ys,
                                                         start=int(min(next_search_start[0][0]+peak_idx+min_peak2peak, len(ys)-1)),
                                                         end=int(min(next_search_start[0][0]+peak_idx+min_peak2peak+max_compound_interval_idx, len(ys)-1)),
                                                         direction=direction
                                                         )

        end_idx = None
        if next_peak_idx is not None:
            # estimate amplitude of next peak
            if (ys[next_peak_idx] - mini['baseline']) * direction > min_amp:
                end_idx = np.where(ys[peak_idx:next_peak_idx] * direction == min(
                    ys[peak_idx:next_peak_idx] * direction))[0][0] + peak_idx
        if end_idx is None:
            end_idx = min(peak_idx + decay_max_points, len(xs)-1)

        mini['end_idx'] = end_idx + offset

        # store the coordinate for the end of mini (where the plot crosses the trailing average)
        mini['end_coord_x'] = xs[end_idx]
        mini['end_coord_y'] = ys[end_idx]
        self.print_time('find end', show_time)

        ####### calculate rise #######
        mini['rise_const'] = (mini['peak_coord_x'] - mini['start_coord_x']) * 1000  # convert to ms
        # print(f'min_rise: {min_rise}')
        # check against min_rise and max_rise
        if min_rise and mini['rise_const'] < min_rise:
            mini['success'] = False
            mini['failure'] = 'Min rise not met'
            return mini

        if max_rise and mini['rise_const'] > max_rise:
            mini['success'] = False
            mini['failure'] = 'Max rise exceeded'
            return mini
        self.print_time('rise', show_time)

        ####### calculate decay ########
        mini['decay_start_idx'] = mini['peak_idx']  # peak = start of decay
        # mini['decay_end_idx'] = min(mini['peak_idx'] + decay_max_points, len(xs) + offset)
        mini['decay_end_idx'] = mini['end_idx']


        # try:
        if decay_algorithm == 'Curve fit':
            try:
                mini['decay_A'], mini['decay_const'], mini['decay_baseline'] = self.fit_mini_decay(
                    xs=xs[peak_idx:min(peak_idx+decay_max_points, len(xs))],
                                    ys=ys[peak_idx:min(peak_idx+decay_max_points, len(ys))],
                                    sampling_rate=sampling_rate,
                                    end_idx=end_idx - peak_idx, # short for compound, all available data for non compound
                                    amplitude=mini['amp']*direction,
                                    decay_guess=decay_best_guess,
                                    direction=direction,
                                    baseline=mini['baseline'],
                                    prev_mini_decay=mini['prev_decay_const'],
                                    prev_mini_A=mini['prev_decay_A'],
                    prev_mini_decay_baseline=mini['prev_decay_baseline'],
                                    prev_mini_t=mini['prev_t'],
                    prev_mini_baseline=mini['prev_baseline']
                                )
            except:
                mini['decay_A'], mini['decay_const'], mini['decay_baseline'] = self.fit_mini_decay(
                    xs=xs[peak_idx:min(peak_idx + decay_max_points, len(xs))],
                    ys=ys[peak_idx:min(peak_idx + decay_max_points, len(ys))],
                    sampling_rate=sampling_rate,
                    end_idx=end_idx - peak_idx,  # short for compound, all available data for non compound
                    amplitude=mini['amp'] * direction,
                    decay_guess=decay_best_guess,
                    direction=direction,
                    baseline=mini['baseline'],
                )
        elif decay_algorithm == '% amplitude':
            # mimics Mini Analysis
            mini['decay_A'] = mini['amp'] * direction
            mini['decay_baseline'] = 0
            decay_idx = np.where((ys[int(peak_idx): int(min(peak_idx+decay_max_points, len(ys)))] - mini['baseline'])*direction < decay_p_amp * mini['amp'] * direction/100)
            if len(decay_idx[0])>0:
                mini['decay_const'] = decay_idx[0][0]/sampling_rate*1000
            else:
                mini['failure'] = 'Decay constant could not be calculated'
                mini['success'] = False
                return mini
        elif decay_algorithm == 'None':
            mini['decay_A'] = None
            mini['decay_const'] = None
            mini['decay_baseline'] = None
            mini['decay_idx'] = None
            mini['decay_coord_x'] = None
            mini['decay_coord_y'] = None


        # except Exception as e:
        #     print(f'decay error {e}')
        #     mini['success'] = False
        #     mini['failure'] = 'decay cannot be calculated'
        #     return mini
        if decay_algorithm != 'None':
            decay_idx = int(peak_idx + mini['decay_const'] / 1000 * sampling_rate)
            mini['decay_idx'] = decay_idx + offset

            if mini['decay_const'] < min_decay:
                mini['success'] = False
                mini['failure'] = 'Min decay not met'
                return mini
            if max_decay and mini['decay_const'] > max_decay:
                mini['success'] = False
                mini['failure'] = 'Max decay exceeded'
                return mini
            # print('here')
            try:
                mini['decay_coord_x'] = xs[decay_idx]
                prev_decay_y = single_exponent_constant(
                    mini['decay_const'] + (mini['t'] - mini['prev_t'])*1000,
                    mini['prev_decay_A'],
                    mini['prev_decay_const'],
                    mini['prev_decay_baseline']
                )*direction + mini['prev_baseline']
                mini['decay_coord_y'] =prev_decay_y+ single_exponent_constant(
                    mini['decay_const'],
                    mini['decay_A'],
                    mini['decay_const'],
                    mini['decay_baseline']
                ) * direction  #### add support for compound (add back subtracted baseline)
            except:
                mini['decay_coord_y'] = single_exponent_constant(
                    mini['decay_const'],
                    mini['decay_A'],
                    mini['decay_const'],
                    mini['decay_baseline']
                ) * direction + mini['baseline']
                pass
            self.print_time('decay', show_time)
        ####### calculate halfwidth #######
        # need to incorporate compound #
        mini['halfwidth_start_coord_y'] = mini['halfwidth_end_coord_y'] = None
        if compound and mini['compound']:
            halfwidth_start_idx, halfwidth_end_idx = self.find_mini_halfwidth(
                amp=mini['amp'], xs=xs[baseline_idx:end_idx], ys=ys[baseline_idx:end_idx],
                peak_idx=peak_idx-baseline_idx, baseline=mini['baseline'], direction=direction,
                prev_mini_t=mini['prev_t'], prev_mini_decay=mini['prev_decay_const'], prev_mini_A=mini['prev_decay_A'],
                prev_mini_decay_baseline=mini['prev_decay_baseline'],
                prev_mini_baseline=mini['prev_baseline']
            )
        else:
            halfwidth_start_idx, halfwidth_end_idx = self.find_mini_halfwidth(
                amp=mini['amp'], xs=xs[baseline_idx:end_idx], ys=ys[baseline_idx:end_idx],
                peak_idx=peak_idx-baseline_idx, baseline=mini['baseline'], direction=direction
            )

        if halfwidth_start_idx is not None and halfwidth_end_idx is None:  # decay doesn't happen long enough?
            if mini['decay_const'] is not None and extrapolate_hw: # use decay to extrapolate 50% value of decay
                t = np.log(0.5)*-1*mini['decay_const']/1000
                halfwidth_end_idx = search_index(xs[peak_idx]+t, xs[baseline_idx:],sampling_rate)

        if halfwidth_end_idx is None or halfwidth_start_idx is None:
            mini['success'] = False
            mini['failure'] = 'Halfwidth could not be calculated'
            return mini
        halfwidth_end_idx += baseline_idx
        halfwidth_start_idx += baseline_idx

        if halfwidth_end_idx >= len(xs):
            mini['success'] = False
            mini['failure'] = 'Halfwidth out of bounds'
            return mini
        mini['halfwidth'] = (xs[int(halfwidth_end_idx)] - xs[int(halfwidth_start_idx)]) * 1000

        mini['halfwidth_start_idx'] = halfwidth_start_idx + offset
        mini['halfwidth_end_idx'] = halfwidth_end_idx + offset

        mini['halfwidth_start_coord_x'] = xs[halfwidth_start_idx]
        mini['halfwidth_end_coord_x'] = xs[halfwidth_end_idx]

        if compound and mini['compound']:
            mini['halfwidth_start_coord_y'] = single_exponent_constant((xs[halfwidth_start_idx] - mini['prev_t']) * 1000,
                                                              mini['prev_decay_A'],
                                                              mini['prev_decay_const'],
                                                                       mini['prev_decay_baseline']
                                                              ) * direction + mini['prev_baseline'] + 0.5 * \
                                              mini['amp']
            mini['halfwidth_end_coord_y'] = single_exponent_constant((xs[halfwidth_end_idx] - mini['prev_t']) * 1000,
                                                            mini['prev_decay_A'],
                                                            mini['prev_decay_const'],
                                                                     mini['prev_decay_baseline']
                                                            ) * direction + mini['prev_baseline'] + 0.5 * mini[
                                                'amp']
        else:
            mini['halfwidth_start_coord_y'] = mini['halfwidth_end_coord_y'] = mini['baseline'] + 0.5 * mini['amp']

        if min_hw and mini['halfwidth'] < min_hw:
            mini['success'] = False
            mini['failure'] = 'Min halfwidth not met'
            return mini

        if max_hw and mini['halfwidth'] > max_hw:
            mini['success'] = False
            mini['failure'] = 'Max halfwidth exceeded'
            return mini

        ###### calculate decay:rise ratio #####
        if decay_algorithm != 'None':
            drr = mini['decay_const']/mini['rise_const']
            if min_drr and drr < min_drr:
                mini['success'] = False
                mini['failure'] = 'Min Decay:Rise ratio not met'
                return mini
            if max_drr and drr > max_drr:
                mini['success'] = False
                mini['failure'] = 'Max Decay:Rise ratio not met'
                return mini

        return mini

    def filter_mini(self,
                    mini_df:DataFrame=None,
                    xlim=None,
                    direction:int=1,
                    min_amp:float=0.0,
                    max_amp:float=np.inf,
                    min_rise:float=0.0,
                    max_rise:float=np.inf,
                    min_decay:float=0.0,
                    max_decay:float=np.inf,
                    min_hw:float=0.0,
                    max_hw:float=np.inf,
                    min_drr:float=0.0,
                    max_drr:float=np.inf,
                    min_s2n:float=0.0,
                    max_s2n:float=np.inf,
                    **kwargs):
        """
        Filters the previously found mini based on criteria
        df: DataFrame containing mini data
            If None, defaults to mini_df
        xlim: x-axis limits to apply the filter (the peak x-value ('t') is considered)
        direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
        max_amp: float representing the maximum accepted mini amplitude (y-axis unit of the recording)
        min_amp: float representing the minimum accepted mini amplitude (y-axis unit of the recording)
        max_rise: float representing the maximum accepted mini rise (ms)
        min_rise: float representing the minimum accepted mini rise (ms)
        max_decay: float representing the maximum accepted mini decay constant (ms)
        min_Decay: float representing the minimum accepted mini decay constant (ms)
        max_hw: float representing the maximum accepted mini halfwidth (ms)
        min_hw: float representing the minimum accepted mini halfwdith (ms)
        max_drr: float representing the maximum decay:rise ratio (no unit)
        min_drr: float representing the minimum decay:rise ratio (no unit)
        max_s2n: signal to noise ratio (amp/stdev) min
        min_s2n: signal to noise ratio (amp/stdev) max
        xlim: tuple representing the x-axis limits to apply the filter. If None, all entries in the dataframe are considered
        """
        if mini_df is None:
            mini_df = self.mini_df
        if xlim is None:
            xlim = (0.0, np.inf)
        if min_amp is not None:
            mini_df = mini_df[(mini_df['amp']*mini_df['direction'] >= min_amp) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if max_amp is not None:
            mini_df = mini_df[(mini_df['amp']*mini_df['direction'] < max_amp) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if min_rise is not None:
            mini_df = mini_df[(mini_df['rise_const'] >= min_rise) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if max_rise is not None:
            mini_df = mini_df[(mini_df['rise_const'] < max_rise) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if min_decay is not None:
            mini_df = mini_df[(mini_df['decay_const'] >= min_decay) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if max_decay is not None:
            mini_df = mini_df[(mini_df['decay_const'] < max_decay) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if min_hw is not None:
            mini_df = mini_df[(mini_df['halfwidth'] >= min_hw) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if max_hw is not None:
            mini_df = mini_df[(mini_df['halfwidth'] < max_hw) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if min_drr is not None:
            mini_df = mini_df[(mini_df['decay_const']/mini_df['rise_const'] > min_drr) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if max_drr is not None:
            mini_df = mini_df[(mini_df['decay_const']/mini_df['rise_const'] < max_drr) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
        if min_s2n is not None and min_s2n > 0:
            mini_df = mini_df[(mini_df['stdev'] != None) & (mini_df['amp']*mini_df['direction']/mini_df['stdev'] > min_s2n)]
        if max_s2n is not None and max_s2n < np.inf:
            mini_df = mini_df[(mini_df['stdev'] != None) & (mini_df['amp']*mini_df['direction']/mini_df['stdev'] < max_s2n)]

        return mini_df

    ###################
    # save/load
    ####################
    def load_minis_from_file(self, filename):
        self.mini_df = pd.read_csv(filename, index_col=0)

    ############## others
    # def mark_greater_than_baseline(self,
    #                                xs,
    #                                ys,
    #                                start_idx: int = 0,
    #                                end_idx: int = None,
    #                                lag: int = 100,
    #                                delta_x: int = 100,
    #                                min_amp: float = 0,
    #                                max_amp: float = np.inf,
    #                                direction: int = 1):
    #     hits = [0] * len(ys)
    #
    #     peaks = []
    #     peak_idx = start_idx + lag + delta_x
    #     if end_idx is None:
    #         end_idx = len(ys)
    #     if end_idx - start_idx < lag + delta_x:
    #         return None  # not enough data points to analyze
    #     y_avg = np.mean(ys[start_idx: start_idx + lag])
    #     ys_avg = [0] * len(ys)
    #     ys_avg[peak_idx] = y_avg
    #     max_peak_idx = -1
    #     while peak_idx < end_idx:
    #         while ys[peak_idx] * direction > y_avg * direction + min_amp:
    #             if max_peak_idx < 0 or ys[peak_idx] * direction > ys[max_peak_idx] * direction:
    #                 max_peak_idx = peak_idx  # update maximum index pointer
    #             y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
    #             hits[peak_idx] = 1
    #             ys_avg[peak_idx] = y_avg
    #             start_idx += 1
    #             peak_idx += 1
    #         else:
    #             if max_peak_idx > 0:
    #                 # print(max_peak_idx)
    #                 peaks.append(max_peak_idx)
    #                 max_peak_idx = -1
    #         y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
    #         ys_avg[peak_idx] = y_avg
    #         start_idx += 1
    #         peak_idx += 1
    #     return hits, peaks, ys_avg

    # def look_ahead_for_peak(self,
    #                         ys,
    #                         start_idx: int = 0,
    #                         end_idx: int = None,
    #                         lag: int = 100,
    #                         delta_x: int = 100,
    #                         min_amp: float = 0,
    #                         max_amp: float = np.inf,
    #                         direction: int = 1
    #                         ):
    #     """
    #     looks for candidate mini peak by comparing a data point further ahead in ys with average of a subset of ys
    #
    #     Args:
    #         ys: numpy array of float, representing y-values
    #         start_idx: int representing the starting index for the search
    #         end_idx: int representing the final index for the search (non-inclusive). If None, defaults to length of ys
    #         lag: int representing the number of data points to average to estimate the baseline value
    #         delta_x: int representing the number of data points to look ahead from baseline
    #         min_amp: float representing the minimum amplitude required to consider a peak
    #         max_amp: float representing the maximum allowed amplitude for a peak
    #         direction: int {-1, 1}. -1 for current 1 for potential
    #
    #     Returns:
    #         peak_idx: int representing the index of the candidate peak within ys
    #     """
    #
    #     peak_idx = start_idx + lag + delta_x
    #     if end_idx is None:
    #         end_idx = len(ys)
    #     if end_idx - start_idx < lag + delta_x:
    #         return None  # not enough data points to analyze
    #     y_avg = np.mean(ys[start_idx: start_idx + lag])
    #     max_peak_idx = -1
    #     while peak_idx < end_idx:
    #         while ys[peak_idx] * direction > y_avg * direction + min_amp:
    #             if max_peak_idx < 0 or ys[peak_idx] * direction > ys[max_peak_idx] * direction:
    #                 max_peak_idx = peak_idx  # update maximum index pointer
    #             y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
    #             start_idx += 1
    #             peak_idx += 1
    #         else:
    #             if max_peak_idx > 0:
    #                 if ys[max_peak_idx] * direction > max_amp:  # maximum amp reached
    #                     max_peak_idx = -1  # clear result
    #                 else:
    #                     return max_peak_idx
    #             y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
    #             start_idx += 1
    #             peak_idx += 1
    #     return None
    def calculate_frequency(self, channel):
        df = self.mini_df[self.mini_df['channel']==channel]
        freq = (df['t'].max() - df['t'].min())/df.shape[0]

        return freq

##############################
# Common Helper Functions
##############################
    def print_time(self, msg="", display=True):
        if display:
            current_time = time()
            try:
                print(f'{msg}\t{current_time - self.time_point}')
            except:
                pass
            self.time_point = current_time
def point_line_min_distance(point, xs, ys, sampling_rate, radius=np.inf, xy_ratio=1):
    """
    finds the minimum distance between x-y plot data and an x-y point

    point: float tuple (x,y)
    xs: float 1D numpy array
    ys: float 1D numpy array
    radius: float - maximum x-value range to calculate distance
    xy_ratio: float - used to normalize weights for x- and y-value distances. delta-x/delta-y
    sampling_rate: float - used to estimate relative location of the point to the plot

    returns float distance, int index, float tuple closest point
    """
    point_idx = int(point[0] * sampling_rate)
    if radius == np.inf:
        search_xlim = (0, len(xs))
    else:
        search_xlim = (max(0, int(point_idx - radius * sampling_rate)),  # search start index (0 or greater)
                       min(len(xs), int(point_idx + radius * sampling_rate)))  # search end index (len(xs) or less)
    xs_bool = (xs < xs[point_idx] + radius) & (xs > xs[point_idx] - radius)
    ys_bool = (ys < ys[point_idx] + radius / xy_ratio) & (ys > ys[point_idx] - radius/xy_ratio)
    min_d = np.inf
    min_i = None
    for i in range(search_xlim[0], search_xlim[1]):
        if xs_bool[i] and ys_bool[i]:
            d = euc_distance(point, (xs[i], ys[i]), xy_ratio)
            if d < min_d and d <= radius:
                min_d = d
                min_i = i
    if min_i:
        return min_d, min_i, (xs[min_i], ys[min_i])
    return None, None, None  # no match


def euc_distance(point1, point2, xy_ratio):
    """
    calculates the euclidean distance between two points on a 2D surface

    point1: float tuple (x,y)
    point2: float tuple (x,y)
    xy_ratio: float - Used to normalize the weight of x- and y- distances
    """
    return hypot((point2[0] - point1[0]), (point2[1] - point1[1]) * xy_ratio)


def search_index(x, l, rate=None):
    """
    used to search the index containing the value of interest in a sorted array
    x: x value to search
    l: array of list of x-values
    rate: float - the interval between each x-datapoint (inverse of sampling_rate)
    """
    if x < l[0]:
        return -1  # out of bounds
    if x > l[-1]:
        return len(l)  # out of bounds
    if rate is None:
        rate = 1 / np.mean(l[1:6] - l[0:5])  # estimate recording rate
    est = int((x - l[0]) * rate)
    if est > len(l):  # estimate is out of bounds
        est = len(l) - 1
    if l[est] == x:
        return est
    if l[est] > x:  # estimate is too high
        while est >= 0:  # loop until index hits 0
            if l[est] <= x:  # loop until x-value is reached
                return est
            est -= 1  # increment down
        else:
            return est  # out of bounds (-1)
    elif l[est] < x:  # estimated index is too low
        while est < len(l):  # loop until end of list
            if l[est] >= x:  # loop until x-value is reached
                return est
            est += 1
        else:
            return est  # out of bounds (len(l))


def single_exponent_constant(x, a, t, d):
    return a * np.exp(-(x) / t) + d

def single_exponent(x, a, t):
    return a * np.exp(-(x)/t)


def format_list_indices(idx):
    if len(idx) == 1:
        return str(idx[0])
    s = ""
    for i, n in enumerate(idx):
        if i == 0:
            s = str(n)
        elif i == len(idx) - 1:
            if n - 1 == idx[-2]:
                s = '{}..{}'.format(s, n)
            else:
                s = '{},{}'.format(s, n)
        elif n - 1 == idx[i - 1] and n + 1 == idx[i + 1]:
            # 0, [1, 2, 3], 4, 10, 11 --> '0'
            pass  # do nothing
        elif n - 1 == idx[i - 1] and n + 1 != idx[i + 1]:
            # 0, 1, 2, [3, 4, 10], 11 --> '0..4'
            s = '{}..{}'.format(s, n)
        elif n - 1 != idx[i - 1]:
            # 0, 1, 2, 3, [4, 10, 11], 14, 16 --> '0..4,10' -->'0..4,10..11'
            s = '{},{}'.format(s, n)
    return s

def translate_indices(s):
    sections = s.split(',')
    indices = []
    for section in sections:
        idx = section.split('..') # should be left with indeces (int)
        if len(idx) == 1:
            indices.append(int(idx[0]))
        else:
            for i in range(int(idx[0]),int(idx[1])):
                indices.append(int(i))
    return indices

def is_indices(s):
    # check formatting
    temp = s.replace('..', ',').split(',')
    # check every number is int
    for t in temp:
        try:
            int(t)
        except:
            return False
    try:
        translate_indices(s)
    except:
        return False
    return True







def calculate_window_around_x(x: float,
                              r: float,
                              xs: np.ndarray,
                              ys: np.ndarray = None,
                              xlim: tuple = None,
                              ylim: tuple = None,
                              offset: int = 0,
                              sampling_rate=None):
    """
    calculates a window around x-data by radius r, bound by xlim and ylim of axes, given xs and ys data

    Args:
        x: float x-data to center the window
        r: float radius around x value to limit the window
        xs: 1D numpy ndarray or list of float. Used in conjunction with xlim to further limit the window
        ys: 1D numpy ndarray or list of float. Used in conjunction with ylim to further limit the window
        xlim: tuple of floats
        ylim: tuple of floats
        offset: int used to adjust the returned indices
        sampling_rate: int the sampling rate of xs

    Returns:
        start_idx: int - index within xs
        end_idx: int
    """
    x_idx = search_index(x, xs, sampling_rate)
    start_idx = search_index(x - r, xs, sampling_rate)
    end_idx = search_index(x + r, xs, sampling_rate)

    # narrow window based on x-axis limits
    try:
        xlim_idx = (
            search_index(xlim[0], xs, sampling_rate),
            search_index(xlim[1], xs, sampling_rate)
        )
    except:
        xlim_idx = (0, len(xs))

    start_idx = max(start_idx, xlim_idx[0])
    end_idx = min(end_idx, xlim_idx[1])

    # narrow window based on y-axis limits
    # if the data goes out of y-lim (assuming data point at x is within ylim)
    # then the window is narrowed to the nearest data points around x that are within the ylim

    if ylim is not None and ys is not None:
        y_high = ys[start_idx:end_idx] > ylim[1]
        y_low = ys[start_idx:end_idx] < ylim[0]

        if sum(y_high) > 0 or sum(y_low) > 0:  # there are data points out of ylim bounds
            i = x_idx - start_idx
            while i > 0:
                if y_high[i] or y_low[i]:
                    break
                i -= 1
            start_idx = i

            i = x_idx - start_idx
            while i < len(y_high) - 1:
                if y_high[i] or y_low[i]:
                    break
                i += 1
            end_idx = i

    return start_idx + offset, end_idx + offset

# def point_line_min_distance(x, y, offset, xs, ys, x2y=1, rate=None):
#     # finds the minimum square difference between a point and a line.
#     idx = search_index(x, xs, rate)
#     min_d = np.inf
#     min_i = None
#     for i in range(max(idx - offset, 0), min(idx + offset, len(xs))):
#         d = euc_distance((x, y), (xs[i], ys[i]), x2y)
#         if d < min_d:
#             min_d = d
#             min_i = i
#     return min_d, min_i

def contains_line(xlim, ylim, xs, ys, rate=None):
    if xlim:
        xlim_idx = (search_index(xlim[0], xs, rate), search_index(xlim[1], xs, rate))
    else:
        xlim_idx = (0, len(xs))
    if xlim_idx[0] < 0 or xlim_idx[-1] > len(xs):
        return False
    if ylim:
        for y in ys[xlim_idx[0]:xlim_idx[1]]:
            if ylim[0] < y < ylim[1]:
                return True
        return False
    return True
