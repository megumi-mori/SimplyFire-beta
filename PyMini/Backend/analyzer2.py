import numpy as np
import os.path
import matplotlib.pyplot as plt
from math import ceil, hypot, isnan, sqrt
from datetime import datetime
from pyabf import abf

from pandas import DataFrame, Series
from scipy.optimize import curve_fit

from astropy.convolution import Box1DKernel, convolve

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
        print(f'opening {filename}')
        self.filetype = os.path.splitext(filename)[1]
        _, self.filename = os.path.split(filename)

        if self.filetype == '.abf':
            data = abf.ABF(filename)
            # store the raw ABF file for now
            # remove this later to reduce memory
            self.data = data

            # sampling rate of the recording
            self.sampling_rate = data.dataRate
            # sampling rate significant digits - used to round calculations
            self.x_sigdig = len(str(self.sampling_rate))-1
            # interval between each x-values (inverse of sampling rate)
            self.x_interval = 1/self.sampling_rate

            # channel metadata
            self.channel_count = data.channelCount
            self.channel_names = data.adcNames
            self.channel_units = data.adcUnits
            self.channel_labels = [""] * self.channel_count
            for c in range(self.channel_count):
                data.setSweep(0, c)
                self.channel_labels[c] = data.sweepLabelY

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

        else:
            # insert support for other filetypes here
            pass


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
        assert len(new_data.shape)==3, 'Matrix shape mismatch - the input data must be a 3D numpy array'
        if channels is None:
            channels = range(new_data.shape[0])

        if mode == 'continuous':
            assert new_data.shape[2] % self.sweep_points == 0, f'Sweep length mismatch. Each sweep in "continuous" mode must be a multiple of {self.sweep_points} datapoints'
            if sweeps is None:
                sweeps = range(int(new_data.shape[2]/self.sweep_points))

            new_data = np.reshape(new_data, (len(channels), len(sweeps), self.sweep_points))

        elif mode == 'overlay':
            assert new_data.shape[2] == self.sweep_points, f'Sweep length mismatch. Each sweep in "overlay" mode must be {self.sweep_points} datapoints'
            if sweeps is None:
                sweeps = range(new_data.shape[1])
        else:
            print(f'incorrect mode: {mode}')
            return None
        for i,c in enumerate(channels):
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
                return np.reshape(self.y_data[channels][:, sweeps, :], (len(channels), 1, len(sweeps) * self.sweep_points))[
                       :, :, max(0, int(xlim[0] / self.x_interval)):min(self.sweep_count * self.sweep_points,
                                                                        ceil(xlim[1] / self.x_interval)+1)]
            else:
                return np.reshape(self.y_data[channels][:, sweeps, :], (len(channels), 1, len(sweeps) * self.sweep_points))[
                       :, :, :]
        if mode == 'overlay':
            if xlim:
                return self.y_data[channels][:, sweeps,
                       max(0, int(xlim[0] / self.x_interval)):min(self.sweep_count * self.sweep_points, ceil(xlim[1] / self.x_interval) + 1)]
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
            x_matrix = np.reshape(self.x_data[channels][:, sweeps] + offset, (len(channels), 1, len(sweeps)*self.sweep_points))
            if xlim:
                start_idx = max(0, int(xlim[0] / self.x_interval))
                end_idx = min(self.sweep_count * self.sweep_points, ceil(xlim[1] / self.x_interval)+1)
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

        else: # the dimension needs to be fixed
            temp_data = np.full((self.channel_count, 1, self.sweep_points), dtype=np.float, fill_value=fill)
            assert new_data.shape[-1] == self.sweep_points, 'dimension mismatch - the sweep length does not match the existing data'
            new_data_reshape = np.reshape(new_data, (len(channels), 1, self.sweep_points))
            temp_data[channels] = new_data_reshape
            self.y_data = np.append(self.y_data, temp_data, axis=1)


        self.x_data = np.append(self.x_data, self.x_data[:, -new_data.shape[1]:, :], axis=1)
        self.sweep_count += 1
        self.added_sweep_count += 1

    def delete_last_sweep(self):
        if self.sweep_count == self.original_sweep_count:
            return None # cannot delete original data
        self.y_data = self.y_data[:, :-1, :]
        self.x_data = self.x_data[:, :-1, :]
        self.sweep_count -= 1
        self.added_sweep_count -=1


############################################
# Analyzer functions
############################################

class Analyzer():
    def __init__(self, plot_mode='continuous'):
        self.plot_mode=plot_mode

        #initialize dataframes
        self.mini_df = DataFrame()

        self.recording = None

    def open_file(self, filename):
        try:
            # clear memory of the old file
            del self.recording
        except:
            pass
        self.recording = Recording(filename)
        return self.recording

    def set_plot_mode(self, plot_mode):
        self.plot_mode = plot_mode

    def plot(self, plot_mode=None, channels=None, sweeps=None, xlim=None, ylim=None, color='black', linewidth=2, show=True):
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
        x_matrix = self.recording.get_x_matrix(mode=plot_mode, sweeps=sweeps, channels=channels) #2D numpy array
        y_matrix = self.recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels) #3D numpy array
        c_len, s_len, _ = y_matrix.shape
        for c in range(c_len):
            for s in range(s_len):
                plt.plot(x_matrix[c, s,:], y_matrix[c,s,:], color=color, linewidth=linewidth)

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

    def calculate_min_sweeps(self, plot_mode=None, channels=None, sweeps=None, xlim=None):
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
        y_matrix = self.recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels, xlim=xlim)  # 3D numpy array
        if sweeps is None:
            sweeps = range(self.recording.sweep_count)
        if channels is None:
            channels = range(self.recording.channel_count)
        mins = np.min(y_matrix, axis=2, keepdims=True)
        mins_std = np.std(mins, axis=1, keepdims=True)

        return mins, mins_std

    def calculate_max_sweeps(self, plot_mode=None, channels=None, sweeps=None, xlim=None):
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
        y_matrix = self.recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels, xlim=xlim)  # 3D numpy array
        if sweeps is None:
            sweeps = range(self.recording.sweep_count)
        if channels is None:
            channels = range(self.recording.channel_count)
        maxs = np.min(y_matrix, axis=2, keepdims=True)
        maxs_std = np.std(maxs, axis=1, keepdims=True)
        return maxs, maxs_std


    ########################
    # Recording Adjustment #
    ########################

    def average_sweeps(self, channels=None, sweeps=None, fill=0):
        """
        returns a 3D numpy array representing the average of specified sweeps in each channel

        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps
        fill: float - y-value to fill channels that will not be assessed. defaults to 0
        """
        # initialize matrix
        result = np.full((self.recording.channel_count, 1, self.recording.sweep_points),
                         fill_value=fill,
                         dtype=np.float)
        result[channels] = np.mean(self.recording.get_y_matrix(mode='overlay', sweeps=sweeps, channels=channels),
                                   axis=1,
                                   keepdims=True)
        return result

    def append_average_sweeps(self, channels=None, sweeps=None, fill=0):
        """
        averages sweeps in each channel and stores the result in the recording attribute

        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps
        fill: float - y-value to fill channels that will not be assessed. defaults to 0
        """

        avg = self.average_sweeps(channels=channels, sweeps=sweeps, fill=fill)
        self.recording.append_sweep(avg)

        return avg

    def subtract_baseline(self, plot_mode='continuous', channels=None, sweeps=None, xlim=None, fixed_val=None):
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
            baseline = np.mean(self.recording.get_y_matrix(mode=plot_mode,
                                                           channels=channels,
                                                           sweeps=sweeps,
                                                           xlim=xlim),
                               axis=2,
                               keepdims=True)
        result = self.recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps) - baseline

        self.recording.replace_y_data(mode=plot_mode, channels=channels, sweeps=sweeps, new_data=result)

        return baseline

    def shift_y_data(self, shift, plot_mode='continuous', channels=None, sweeps=None):
        """
        shifts y_data by specified amount

        shift: float or array. The dimensions must match dimension: (n_channels, n_sweeps, (1))
        plot_mode: string {'continuous', 'overlay'}. If continuous, all specified sweeps are concatenated into a 1D array per channel
        channels: list of int
        sweeps: list of int
        """
        result = self.recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps) - shift
        self.recording.replace_y_data(mode=plot_mode, channels=channels, sweeps=sweeps, new_data=result)

        return None

    def filter_sweeps(self, filter='boxcar', params=None, channels=None, sweeps=None):
        """
        applies a specified filter to the y-data in specified sweeps and channels

        filter: string {'boxcar'} (more will be added) - name of filter
        params: dict parameters specific to each filter type. See below for more details
        channels: list of int - if None, defaults to all channels
        sweeps: list of int - if None, defaults to all sweeps

        filter 'boxcar':
            see astropy.convolution.Box1DKernel for more details
            width: int - number of data points to use for boxcar filter
            if only a subset of sweeps are selected, y-values from selected sweeps are stitched together to form a continuous y-data sequence for the purpose of convolution
            At the edges of each sweep, the y-values from previous/next sweep may be used as if the data were continuous

            The first width/2 data points and last width/2 data points are not convolved to avoid


        """
        if filter == 'boxcar':
            k = Box1DKernel(width=params['width'])
            for c in channels:
                # apply filter
                ys = self.recording.get_y_matrix(mode='continuous',
                                                 channels=[c],
                                                 sweeps=sweeps)
                filtered = convolve(ys.flatten(), k)

                # reshape filtered data to 3D numpy array
                filtered = np.reshape(filtered, (1, 1, len(filtered)))

                # # even out the edge cases
                filtered[:, :, :int(params['width']/2)] = ys[:, :, :int(params['width']/2)]
                filtered[:, :, -int(params['width'] / 2):] = ys[:, :, -int(params['width'] / 2):]

                self.recording.replace_y_data(mode='continuous', channels=[c], sweeps=sweeps, new_data=filtered)
        return None

    def find_closest_sweep_to_point(self, point, xlim=None, ylim=None, height=1, width=1, radius=np.inf,
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
            xy_ratio = (xlim[1] - xlim[0])/(ylim[1] - ylim[0]) * height / width
        except Exception as e: # xlim and/or ylim not specified
            xy_ratio = 1
        if channels is None:
            channels = range(self.recording.channel_count)
        if sweeps is None:
            sweeps = range(self.recording.sweep_count)
        min_c = None
        min_s = None
        min_i = None
        min_d = np.inf
        for c in channels:
            for s in sweeps:
                d, i, _ = point_line_min_distance(
                    point,
                    self.recording.get_xs(mode='overlay', sweep=s, channel=c),
                    self.recording.get_ys(mode='overlay', sweep=s, channel=c),
                    sampling_rate=self.recording.sampling_rate,
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

    def find_mini_auto(self,
                       xlim=None,
                       xs=None,
                       ys=None,
                       channel=0,
                       sweeps=None,
                       kernel=300,
                       stride=150,
                       direction=1,
                       reference_df=True,
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
            channel: int indicating the channel number to analyze. Only required if xs and ys are not provided
            sweeps: list of int indicating the sweeps to analyzer. If left None, all sweeps will be considered
            kernel: int representing the number of data points to consider per iteration.
                The most extreme data point within the kernel will be tested as a candidate mini peak.
                Should be smaller than the shortest interval between two minis within the recording.
                Larger kernel size can speed up the search.
            stride: int representing the number of data points to shift every iteration.
                Recommended to be less than kernel.
                Larger strides can speed up the search.
            direction: int
            **kwargs: see list of parameters in find_single_mini()

        Returns:
            pandas DataFrame containing the information on search parameters and mini characteristics.
            In addition to the search parameters passed as arguments, the following data are included
            in the result:
                #### list columns here
        """
        if xs is None:
            xs = self.recording.get_x_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        if ys is None:
            ys = self.recording.get_y_matrix(mode='continuous', channels=[channel], sweeps=sweeps, xlim=xlim).flatten()
        try:
            xlim_idx = (search_index(xlim[0], xs), search_index(xlim[1], xs))
        except:
            xlim_idx = (0, len(xs))
        start_idx = xlim_idx[0]
        end_idx = start_idx + kernel

        while start_idx < len(xs):
            peak_idx = self.find_peak_recursive(xs, ys, start=start_idx, end=end_idx, direction=direction)
            if peak_idx is not None:
                mini = self.analyze_candidate_mini(
                    xs=xs,
                    ys=ys,
                    peak_idx=peak_idx,
                    x_sigdig=self.recording.x_sigdig,
                    channel=channel,
                    direction=direction,
                    reference_df=reference_df,
                    **kwargs
                )

                if reference_df and mini['success']:
                    self.mini_df = self.mini_df.append(Series(mini),
                                                       ignore_index=True,
                                                       verify_integrity=True,
                                                       sort=True)
                    self.mini_df = self.mini_df.sort_values(by='t')
                   # start_idx = max(peak_idx - 1, start_idx + stride)
                else:
                   #start_idx += stride

                    pass
            else:
                #start_idx += stride
                pass
            start_idx += stride
            end_idx = start_idx + kernel

    # def find_mini_manual(self,
    #                      point: tuple = None,
    #                      radius: float = 0.0,
    #                      xs: np.ndarray = None,
    #                      ys: np.ndarray = None,
    #                      channel: int = 0,
    #                      sweeps: list = None,
    #                      update_df: bool = True,
    #                      compare_df: bool = True,
    #                      **kwargs
    #                      ) -> DataFrame:
    #     """
    #     Searches mini near a specified point and adds the result to the mini_df attribute
    #
    #     Recommended for manual detection in combination with the GUI.
    #     If multiple searches are performed on the same xs and ys data, it is recommended to
    #     store the xs and ys data outside of the Analyzer and pass them as arguments to speed up
    #     the search time. If ys and xs are not provided as arguments, continuous sequence of
    #     xs and ys data are created on the fly from the recording data every function call.
    #
    #     Args:
    #         point: tuple float (x, y) representing a point to center the search
    #         radius: x-value radius. A window of [point-radius, point+radius] will be used for the search
    #         xs: float numpy array representing the x-values of the recording sequence.
    #             If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
    #         ys: float numpy array representing the y-values of the recording sequence.
    #             If None, data will be extracted from the recording attribute using the channel and sweeps arguments.
    #         channel: int indicating the channel number to analyze. Only required if xs and ys are not provided
    #         sweeps: list of int indicating the sweeps to analyzer. If left None, all sweeps will be considered
    #         update_df: bool representing whether to update the mini_df attribute when a mini is found
    #             If True, any new mini will be added to mini_df attribute
    #         compare_df: bool representing whether to use the mini_df attribute to check for previously found mini
    #             If True, any candidate mini will be compared against previously found mini
    #         **kwargs: see list of parameters in find_single_mini()
    #
    #     Returns:
    #         pandas DataFrame containing the information on search parameters and mini characteristics.
    #         In addition to the search parameters passed as arguments, the following data are included
    #         in the result:
    #             #### list columns here
    #     """
    #     if xs is None:
    #         xs = self.recording.get_x_matrix(mode='continuous', channels=[channel], sweeps=sweeps).flatten()
    #     if ys is None:
    #         ys = self.recording.get_y_matrix(mode='continuous', channels=[channel], sweeps=sweeps).flatten()
    #
    #     # if compare_df is True, pass the mini_df attribute as argument for comparison
    #     reference = None
    #     if compare_df:
    #         reference = self.mini_df
    #
    #     mini = self.find_mini_with_criteria(xs=xs,
    #                                  ys=ys,
    #                                  xlim=(point[0]-radius, point[0]+radius),
    #                                  x_sigdig=self.recording.x_sigdig,
    #                                  sampling_rate=self.recording.sampling_rate,
    #                                  reference=reference,
    #                                  channel=channel,
    #                                  **kwargs
    #                                  )
    #     # fill in data from the recordings attribute
    #     mini['t_unit'] = self.recording.x_unit
    #     mini['baseline_unit'] = self.recording.channel_units[channel]
    #     mini['amp_unit'] = self.recording.channel_units[channel]
    #     mini['rise_unit'] = 'ms' if self.recording.x_unit in ['s', 'seconds', 'second', 'sec'] else '{} E-3'.format(
    #         self.recording.x_unit)
    #
    #     print(mini)
    #     if update_df:
    #         self.mini_df = self.mini_df.append(Series(mini),
    #                                            ignore_index=True,
    #                                            verify_integrity=True,
    #                                            sort=True)
    #     print(self.mini_df)
    #
    #     return mini
    #


    # def find_mini_with_criteria(self,
    #                             xs,
    #                             ys,
    #                             start_idx: int = None,
    #                             end_idx: int = None,
    #                             direction: int = 1,
    #                             **kwargs
    #                             ):
    #     """
    #     searches for a single mini event. Returns a dict containing details of the mini found
    #         xs: 1D float numpy array - x-values
    #         ys: 1D float numpy array - y-values
    #         start_idx: int representing the lower limit of search window in index value
    #                 - If not None, this parameter takes priority over xlim
    #         end_idx: int representing the higher limit of search window in index value
    #                 - If not None, this parameter takes priority over xlim
    #         direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
    #
    #
    #     returns dict
    #     """
    #
    #     assert start_idx is not None and end_idx is not None, 'insufficient information on xlim'
    #     assert start_idx < end_idx, 'start_idx > end_idx'
    #     assert 0 < start_idx < len(xs) and 0 < end_idx <= len(xs), "search window out of bounds"
    #
    #     # store search parameters
    #
    #
    #     ######## search for peak #######
    #     # look for the local extremum
    #     peak_idx = self.find_peak_recursive(xs, ys, start=start_idx, end=end_idx, direction=direction)
    #
    #     # if peak is not found, report failure to find peak
    #     if peak_idx is None:
    #         return None
    #
    #     # fill the rest of the information
    #     mini = self.analyze_candidate_mini(xs, ys, peak_idx, direction=direction, **kwargs)
    #
    #     # ####### search baseline #######
    #     # # find baseline/start of event
    #     # prev_peak_x = np.nan
    #     # if reference is not None:
    #     #     try:
    #     #         # find the peak of the previous mini
    #     #         # peak x-value must be stored in the column 't'
    #     #         # check that the channels are the same
    #     #         prev_peak_x = max(reference.t.where(reference.t < mini['t']).where(reference.channel == channel))
    #     #         # can be nan if the reference DataFrame is empty
    #     #     except:
    #     #         pass
    #     # if isnan(prev_peak_x):
    #     #     prev_peak_x = xs[0]
    #     # mini['baseline_idx'], mini['baseline'] = self.calculate_mini_baseline(peak_idx=mini['peak_idx'],
    #     #                                                                       ys=ys,
    #     #                                                                       lag=lag,
    #     #                                                                       direction=direction,
    #     #                                                                       stride=-1)
    #     # if reference is not None and xs[mini['baseline_idx']] < prev_peak_x:
    #     #     # start of this mini is earlier than the peak of the previous mini - potential compound peak
    #     #
    #     #     # insert support for compound peak here:
    #     #
    #     #
    #     #     ######################################
    #     #
    #     #     pass
    #     #
    #     # # check if baseline calculation was successful
    #     # if mini['baseline_idx'] is None: # not successful
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Baseline could not be found'
    #     #     return mini
    #     #
    #     # # store coordinate for start of mini (where the plot meets the baseline)
    #     # mini['start_coord_x'] = xs[mini['baseline_idx']]
    #     # mini['start_coord_y'] = ys[mini['baseline_idx']]
    #     #
    #     # ####### calculate amplitude #######
    #     # mini['amp'] = (mini['peak_coord_y'] - mini['baseline']) # signed
    #     #
    #     # # check against min_amp and max_amp criteria
    #     # if mini['amp'] * direction < min_amp:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Min amp not met'
    #     #     return mini
    #     #
    #     # if mini['amp'] * direction > max_amp:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Max amp exceeded'
    #     #     return mini
    #     #
    #     # ####### calculate end of event #######
    #     # mini['end_idx'], _ = self.calculate_mini_baseline(peak_idx=mini['peak_idx'],
    #     #                                                   ys=ys,
    #     #                                                   lag=lag,
    #     #                                                   direction=direction,
    #     #                                                   stride=1)
    #     # if mini['end_idx'] is None: # not successful
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'End of mini could not be found'
    #     #     return mini
    #     #
    #     # # store the coordinate for the end of mini (where the plot crosses the trailing average)
    #     # mini['end_coord_x'] = xs[mini['end_idx']]
    #     # mini['end_coord_y'] = ys[mini['end_idx']]
    #     #
    #     # ####### calculate rise #######
    #     # mini['rise_const'] = (mini['peak_coord_x'] - mini['start_coord_x']) * 1000 # convert to ms
    #     # print(f'min_rise: {min_rise}')
    #     # # check against min_rise and max_rise
    #     # if mini['rise_const'] < min_rise:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Min rise not met'
    #     #     return mini
    #     #
    #     # if mini['rise_const'] > max_rise:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Max rise exceeded'
    #     #     return mini
    #     #
    #     #
    #     # ####### calculate decay ########
    #     # mini['decay_start_idx'] = mini['peak_idx'] # peak = start of decay
    #     # mini['decay_end_idx'] = min(mini['peak_idx'] + max_points_decay, len(xs))
    #     # mini['decay_amp'], mini['decay_constant'], mini['decay_scalar'], mini['decay_idx'] = self.calculate_mini_decay(
    #     #     xs =xs, ys=ys, start_idx=mini['decay_start_idx'], end_idx=mini['decay_end_idx'], direction=direction)
    #     # if mini['decay_constant'] < min_decay:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Min decay not met'
    #     #     return mini
    #     # if mini['decay_constant'] > max_decay:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Max decay exceeded'
    #     #     return mini
    #     #
    #     # print('here')
    #     # mini['decay_coord_x'] = xs[mini['decay_idx']]
    #     # mini['decay_coord_y'] = single_exponent_constant(
    #     #     mini['decay_constant'],
    #     #     mini['decay_amp'],
    #     #     mini['decay_constant'],
    #     #     mini['decay_scalar']
    #     # ) * direction #### add support for compound (add back subtracted baseline)
    #     #
    #     #
    #     # ####### calculate halfwidth #######
    #     # mini['halfwidth_start_idx'], mini['halfwidth_end_idx'], mini['halfwidth'] = self.calculate_mini_halfwidth(
    #     #     amp=mini['amp'], xs=xs, ys=ys, start_idx=mini['baseline_idx'], end_idx =mini['end_idx'],
    #     #     peak_idx=mini['peak_idx'], baseline=mini['baseline'], direction=direction)
    #     # if ['halfwidth'] is None:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Halfwidth could not be calculated'
    #     #     return mini
    #     #
    #     # if mini['halfwidth'] < min_hw:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Min halfwidth not met'
    #     #     return mini
    #     #
    #     # if mini['halfwidth'] > max_hw:
    #     #     mini['success'] = False
    #     #     mini['failure'] = 'Max halfwidth exceeded'
    #     #     return mini
    #     #
    #     # mini['halfwidth_start_coord_x'] = xs[mini['halfwidth_start_idx']]
    #     # mini['halfwidth_start_coord_y'] = ys[mini['halfwidth_start_idx']]
    #     #
    #     # mini['halfwidth_end_coord_x'] = xs[mini['halfwidth_end_idx']]
    #     # mini['halfwidth_end_coord_y'] = ys[mini['halfwidth_end_idx']]
    #     return mini

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
        peak_y = max(ys[start:end] * direction)
        peaks = np.where(ys[start:end] * direction == peak_y)[0] + start # get list of indices where ys is at peak
        peak_idx = peaks[int(len(peaks)/2)] # select the middle index of the peak
        FUDGE = 10 # margin at the edge of search window required to be considered peak (used to avoid edge cases)
        if end - start < FUDGE * 2:
            return None # the search window is too narrow

        # check if the peak is at the edge of the search window
        # if the peak is at the edge, the slope could continue further beyond the window
        # recursively narrow the search window and look for another local extremum within the new window

        if peak_idx < start + FUDGE: # the local extremum is at the left end of the search window
            return self.find_peak_recursive(xs, ys, start + FUDGE, end, direction)
        if peak_idx > end - FUDGE: # the local extremum is at the right end of the search window
            return self.find_peak_recursive(xs, ys, start, end - FUDGE, direction)
        return peak_idx

    def find_mini_start(self,
                        peak_idx: int,
                        ys: np.ndarray,
                        lag: int = 100,
                        direction: int = 1) -> tuple:
        """
        Calculates estimated baseline value and the index of start of a mini event

        Args:
            peak_idx: int representing the index at which the candiate mini peak was found in ys array
            ys: 1D numpy array representing the y-value to seearch for mini
            lag: int representing the number of datapoints averaged to find the trailing average. Default 100
                The result of the trailing average is used to estamate the baseline.
                The point at which the mini data crosses the trailing average is considered the start of the mini.
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
                return None, None # there are less than lag data points to the left of starting index

        y_avg = np.mean(ys[idx - lag:idx] * direction) # avg lag data points
        while lag <= idx <= len(ys) - lag:
            idx -= 1
            y_avg = y_avg + (ys[idx - lag] - ys[idx]) * direction / lag # update trailing avg
            # equivalent to np.mean(ys[base_idx-lag: base_idx])
            if y_avg >= ys[idx] * direction: # y-value dips below the estimated baseline
                break
        else:
            return None, None # could not find baseline until base_idx < lag or base_idx > len(ys) - lag
        return idx, y_avg * direction

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
                return None, None # there are less than lag data points to the right of the starting index

        y_avg = np.mean(ys[idx:idx + lag] * direction) # avg lag data points
        while lag <= idx <= len(ys) - lag:
            y_avg = y_avg + (ys[idx + lag] - ys[idx]) * direction / lag # update trailing avg
            # equivalent to np.mean(ys[base_idx-lag: base_idx])
            if y_avg >= ys[idx] * direction: # y-value dips below the estimated baseline
                break
            idx += 1
        else:
            return None, None # could not find baseline until base_idx < lag or base_idx > len(ys) - lag
        return idx, y_avg * direction

    def calculate_mini_halfwidth(self,
                                 amp: float,
                                 xs: np.ndarray,
                                 ys: np.ndarray,
                                 start_idx: int,
                                 end_idx: int,
                                 peak_idx:int,
                                 baseline: float,
                                 direction: int=1
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
        left_idx = np.where(ys[start_idx:peak_idx] * direction <= (amp * 0.5 + baseline) * direction)
        if len(left_idx[0]):
            left_idx = left_idx[0][-1] + start_idx
        else:
            left_idx = None
        right_idx = np.where(ys[peak_idx:end_idx] * direction <= (amp * 0.5 + baseline) * direction)
        if len(right_idx[0]):
            right_idx = right_idx[0][0] + peak_idx
        else:
            right_idx = None
        return left_idx, right_idx, xs[right_idx] - xs[left_idx]  # pick the shortest length


    def calculate_mini_decay(self,
                             xs: np.ndarray,
                             ys: np.ndarray,
                             start_idx: int,
                             end_idx: int,
                             direction: int = 1,
                             baseline:float=0.0):
        """
        calculates decay of a mini

        Args:
            xs: float numpy array of the x values
            ys: float numpy array of the y values
            start_idx: int representing the index to start the fit (should be peak of mini)
            end_idx: int reprsenting the index to end the fit
            direction: int {-1, 1}
            baseline: float to subtract from ys

        Returns:
            a, t, d: float, single exponential function parameters
            decay_constant_idx: int representing the index of xs, ys where y-value is e^-1 of max amplitude

        """

        ########## is it better the constrain a? ##############

        x_data = (xs[start_idx:end_idx] - xs[start_idx])*1000
        # print(x_data)
        y_data = (ys[start_idx:end_idx] - baseline) * direction

        # initialize weights for gradient descent
        y_weight = np.empty(len(y_data))
        y_weight.fill(10)
        y_weight[0] = 0.001

        # fit
        results = curve_fit(single_exponent_constant,
                            x_data,
                            y_data,
                            sigma=y_weight,
                            absolute_sigma=True,
                            maxfev=15000)
        # print(results[0])
        a = results[0][0]
        t = results[0][1]
        d = results[0][2]
        # print((a, t, d))
        decay_constant_idx = search_index(t, x_data) + start_idx # offset to start_idx

        return a, t, d, decay_constant_idx

    def find_mini_2(self,
                    xs,
                    ys,
                    delta_x: int = 100,
                    lag: int = 100,
                    min_amp: float = 0.3,
                    max_amp: float = np.inf,
                    decrease_threshold: int = 5,
                    increase_threshold: int = 5,
                    direction: int = 1,
                    offset: int=0
                    ):
        """
        uses the delta_x method to find peak - no window
        """
        ys = ys.copy()
        plt.plot(xs, ys)
        start_idx = 0
        end_idx = len(ys)
        decline_counter = 0

        DECLINE_COUNTER_THRESHOLD = 5
        increase_counter = 0
        INCREASE_COUNTER_THRESHOLD = 5

        switch = False
        switch_on_idx = []
        switch_off_idx = []

        querry_idx = start_idx + lag + delta_x
        if end_idx - start_idx < lag + delta_x:
            return None  # not enough data points to analyze
        y_avg = np.mean(ys[start_idx: start_idx + lag])
        y_var = np.var(ys[start_idx:start_idx+lag])

        inc_counter = [0]*len(ys)
        dec_counter = [0]*len(ys)
        print(y_var)
        # y_var = sum([(y - y_avg)**2 for y in ys[start_idx:start_idx+lag]])/lag
        y_std = np.std(ys[start_idx:start_idx + lag])

        max_peak_idx = -1
        while querry_idx < end_idx:
            if (ys[querry_idx] - y_avg) * direction > min_amp * 0.36: # try out std #min_amp * 0.36: # inside a potential mini event
                if decline_counter > DECLINE_COUNTER_THRESHOLD and switch and max_peak_idx > 0:
                    # user specified compound mini analysis
                    # sufficiently in negative slope after a local max is found
                    # consider this as a candidate mini peak, and perform analysis with criteria
                    mini = self.analyze_candidate_mini(
                        xs,
                        ys,
                        max_peak_idx,
                        x_sigdig=self.recording.x_sigdig,
                        direction=direction,
                        lag=lag,
                        min_amp=min_amp,
                        max_amp=max_amp,
                        offset=offset
                    )
                    if mini['success']:
                        self.mini_df = self.mini_df.append(Series(mini),
                                                           ignore_index=True,
                                                           verify_integrity=True,
                                                           sort=True)
                        # ys[max_peak_idx:mini['end_idx'] - offset] = ys[
                        #                                             max_peak_idx:mini['end_idx'] - offset
                        #                                             ] - single_exponent_constant(
                        #                     (xs[max_peak_idx:mini['end_idx'] - offset] - xs[max_peak_idx]) * 1000,
                        #                     mini['decay_A'],
                        #                     mini['decay_tau'],
                        #                     0
                        #                 ) * direction
                        # ys[int(mini['baseline_idx'] - offset):int(mini['peak_idx'] - offset)] = mini['baseline']
                    mini = {}
                    increase_counter = 0 # refresh positive slope tracker
                    decline_counter = 0 # refresh negative slope tracker
                    max_peak_idx = -1 # refresh max tracker
                    switch = False
                    switch_off_idx.append(querry_idx)
                elif max_peak_idx < 0 or ys[querry_idx] * direction > ys[max_peak_idx] * direction:
                    # no max found yet or new max found
                    max_peak_idx = querry_idx # update max tracker
                    decline_counter = 0 # refresh negative slope tracker
                if ys[querry_idx] * direction > ys[querry_idx - 1] * direction: # part of positive slope
                    increase_counter += 1 # increase positive slope tracker
                    if increase_counter > INCREASE_COUNTER_THRESHOLD:
                        switch = True
                        switch_on_idx.append(querry_idx)
                elif ys[querry_idx] * direction < ys[querry_idx - 1] * direction: # part of negative slope
                    decline_counter += 1
            else: # datapoint is close to baseline, ignore
                decline_counter = 0 # refresh negative slope tracker
                increase_counter = 0 # refresh positive slope tracker
                max_peak_idx = -1

            new_y_avg = y_avg + (ys[start_idx + lag] - ys[start_idx]) / lag
            # y_var += ((ys[start_idx+lag] - new_y_avg) + (ys[start_idx] - y_avg)) * (ys[start_idx + lag] - ys[start_idx])/lag
            # if y_var < 0:
            #     y_var = np.var(ys[start_idx+1:start_idx+lag+1])
            # y_std = sqrt(y_var)
            # y_std = np.std(ys[start_idx+1:start_idx + lag + 1])
            # ys_std[int(start_idx + lag/2)] = y_std
            dec_counter[querry_idx] = decline_counter
            inc_counter[querry_idx] = increase_counter

            y_avg = new_y_avg
            querry_idx += 1
            start_idx += 1

        plt.plot(xs, [i-8 for i in inc_counter], color='red')
        plt.plot(xs, [i-8 for i in dec_counter], color='purple')
        plt.plot(xs, ys, color='blue')


        plt.scatter([xs[i] for i in switch_on_idx], [ys[i] for i in switch_on_idx], color='green', marker='o')
        plt.scatter([xs[i] for i in switch_off_idx], [ys[i] for i in switch_off_idx], color='red', marker='o')

        scatter_x = [xs[int(idx)] for idx in self.mini_df.peak_idx[:]]
        scatter_y = [ys[int(idx)] for idx in self.mini_df.peak_idx[:]]
        plt.scatter(scatter_x, scatter_y, c='pink')
        plt.show()
        # plt.plot(xs, ys)
        # plt.fill_between(xs, ys+ys_std, ys-ys_std)
        # plt.scatter([x for i, x in enumerate(xs) if hits[i]],
        #             [y for i, y in enumerate(ys) if hits[i]],
        #          marker='x', color='red')
        # plt.show()
            # while ys[peak_idx] * direction > y_avg * direction + min_amp * 0.5 and \
            #         decline_counter < DECLINE_COUNTER_THRESHOLD:
            #     if max_peak_idx < 0 or ys[peak_idx] * direction > ys[max_peak_idx] * direction:
            #         max_peak_idx = peak_idx  # update maximum index pointer
            #         decline_counter = 0
            #     if ys[peak_idx] * direction < ys[peak_idx-1] * direction:
            #         decline_counter += 1 # downward slope
            #     elif ys[peak_idx] * direction > ys[peak_idx - 1] * direction:
            #         increase_counter += 1 # upward slope
            #     y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
            #     start_idx += 1
            #     peak_idx += 1
            # else:
            #     if max_peak_idx > 0:
            #         # potential peak found
            #         mini = self.analyze_candidate_mini(
            #             xs,
            #             ys,
            #             max_peak_idx,
            #             x_sigdig=self.recording.x_sigdig,
            #             direction=direction,
            #             lag=lag,
            #             min_amp = min_amp,
            #             max_amp=max_amp,
            #             offset=offset
            #         )
            #         if mini['success']:
            #             self.mini_df = self.mini_df.append(Series(mini),
            #                                            ignore_index=True,
            #                                            verify_integrity=True,
            #                                            sort=True)
            #             ys[max_peak_idx:mini['end_idx'] - offset] =  ys[max_peak_idx:mini['end_idx'] - offset]- single_exponent_constant(
            #                 (xs[max_peak_idx:mini['end_idx'] - offset] - xs[max_peak_idx]) * 1000,
            #                 mini['decay_A'],
            #                 mini['decay_tau'],
            #                 0
            #             ) * direction
            #             ys[int(mini['baseline_idx'] - offset):int(mini['peak_idx'] - offset)] = mini['baseline']
            #         mini = {}
            #         max_peak_idx = -1
            # y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
            # start_idx += 1
            # peak_idx += 1
        return ys

    def analyze_candidate_mini(self,
                               xs,
                               ys,
                               peak_idx,
                               x_sigdig = None,
                               channel=0,
                               direction=1,
                               reference_df=True,
                               ## parameters defined in GUI ##
                               lag=100,
                               min_amp=0.0,
                               max_amp=np.inf,
                               min_rise=0.0,
                               max_rise=np.inf,
                               min_hw=0.0,
                               max_hw=np.inf,
                               min_decay=0.0,
                               max_decay=np.inf,
                               max_points_decay=40000,
                               #################################

                               offset=0,
                               ):
        """
            peak_idx: int - use if reanalyzing an existing peak. Index within the xs data corresponding to a peak.
                - If provided, the data point at peak_idx is assumed to be the local extremum
            direction: int {-1, 1} indicating the expected sign of the mini event. -1 for current, 1 for potential.
            lag: int indicating the number of data points used to calculate the baseline.
                See calculate_mini_baseline() for algorithm on baseline estimation.
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
            max_decay_points: int indicating the number of data points after peak to consider for decay fit.
            allow_duplicate: bool indicating whether to accept mini that was already found by the Analyzer.
                If False, a candidate mini is rejected if the peak is already included in the mini_df attribute
            reference_df: bool indicating whether to compare the results against previously found minis stored in mini_df.
                If True, previously found minis will be ignored, and newly found minis will be added to the mini_df
        """
        mini = {'direction': direction, 'lag': lag, 'channel': channel, 'min_amp': min_amp, 'max_amp': max_amp,
                'min_rise': min_rise, 'max_rise': max_rise, 'min_hw': min_hw, 'max_hw': max_hw, 'min_decay': min_decay,
                'max_decay': max_decay, 'max_points_decay': max_points_decay,
                'datetime': datetime.now().strftime('%m-%d-%y %H:%M:%S'), 'failure': None, 'success': True,
                't': xs[peak_idx], 'peak_idx': peak_idx + offset, 'compound':False}

        # extract peak datapoint
        if x_sigdig is not None:
            mini['t'] = round(mini['t'], x_sigdig)  # round the x_value of the peak to indicated number of digits

        # check if the peak is duplicate of existing mini data
        if reference_df:
            try:
                if mini['t'] in self.mini_df.t.values:
                    mini['success'] = False
                    mini['failure'] = 'Mini was previously found'
                    return mini
            except Exception as e:  # if df is empty, will throw an error
                pass

        # store peak coordinate
        mini['peak_coord_x'] = xs[peak_idx]
        mini['peak_coord_y'] = ys[peak_idx]

        ####### search baseline #######
        # find baseline/start of event
        prev_peak_idx = None
        if reference_df and len(self.mini_df.index) > 0:
            try:
                # find the peak of the previous mini
                # peak x-value must be stored in the column 't'
                # check that the channels are the same
                prev_peak = max(self.mini_df.loc[(self.mini_df['channel']==channel) & (self.mini_df['t']<mini['t'])].index)
                prev_peak_t = self.mini_df[prev_peak].t
                prev_peak_end = self.mini_df[prev_peak_idx].end_coord_x # store end of previous mini
                if prev_peak_end > mini['t']: # peak is within the decay of another mini:
                    mini['compound'] = True

                # assume the df is sorted by 't' column
            except:
                pass
        # if not mini['compound']:
        if not mini['compound']:
            baseline_idx, mini['baseline'] = self.find_mini_start(peak_idx=peak_idx,
                                                                                  ys=ys,
                                                                                  lag=lag,
                                                                                  direction=direction)

            # check if baseline calculation was successful
            if baseline_idx is None:  # not successful
                mini['success'] = False
                mini['failure'] = 'Baseline could not be found'
                return mini
            mini['baseline_idx'] = baseline_idx + offset
            ####### calculate amplitude #######
            mini['amp'] = (mini['peak_coord_y'] - mini['baseline'])  # signed
        else:
            prev_peak_idx = search_index(prev_peak_t, ys)
            if prev_peak_idx <0 or prev_peak_idx > len(ys):
                mini['success'] = False
                mini['failure'] = 'The compound mini could not be analyzed - need more data points'
            baseline_idx = np.where(ys[prev_peak_idx:peak_idx] * direction == min(ys[prev_peak_idx:peak_idx] * direction))[0][0] + prev_peak_idx
            mini['baseline'] = xs[baseline_idx]
            # find the local minimum between the two peaks

            # extrapolate decay of previous peak at current peak
            y = single_exponent_constant(xs[peak_idx] - xs[prev_peak_idx], self.mini_df[prev_peak].decay_A,
                                         self.mini_df[prev_peak].decay_tau, self.mini_df[prev_peak].decay_C) * direction

            mini['amp'] = (mini['peak_coord_y'] - y) # signed



        # store coordinate for start of mini (where the plot meets the baseline)
        mini['start_coord_x'] = xs[baseline_idx]
        mini['start_coord_y'] = ys[baseline_idx]

        if mini['amp'] * direction < min_amp:
            mini['success'] = False
            mini['failure'] = 'Min amp not met'
            return mini

        if mini['amp'] * direction > max_amp:
            mini['success'] = False
            mini['failure'] = 'Max amp exceeded'
            return mini

        ####### calculate end of event #######
        end_idx, _ = self.find_mini_end(peak_idx=mini['peak_idx'],
                                                          ys=ys,
                                                          lag=lag,
                                                          direction=direction)
        mini['end_idx'] = end_idx + offset
        if mini['end_idx'] is None:  # not successful
            mini['success'] = False
            mini['failure'] = 'End of mini could not be found'
            return mini

        # store the coordinate for the end of mini (where the plot crosses the trailing average)
        mini['end_coord_x'] = xs[end_idx]
        mini['end_coord_y'] = ys[end_idx]

        ####### calculate rise #######
        mini['rise_const'] = (mini['peak_coord_x'] - mini['start_coord_x']) * 1000  # convert to ms
        # print(f'min_rise: {min_rise}')
        # check against min_rise and max_rise
        if mini['rise_const'] < min_rise:
            mini['success'] = False
            mini['failure'] = 'Min rise not met'
            return mini

        if mini['rise_const'] > max_rise:
            mini['success'] = False
            mini['failure'] = 'Max rise exceeded'
            return mini


        ####### calculate decay ########
        mini['decay_start_idx'] = mini['peak_idx']  # peak = start of decay
        mini['decay_end_idx'] = min(mini['peak_idx'] + max_points_decay, len(xs) + offset)
        mini['decay_A'], mini['decay_tau'], mini['decay_C'], decay_idx = self.calculate_mini_decay(
            xs=xs, ys=ys, start_idx=peak_idx, end_idx=min(peak_idx + max_points_decay, len(xs)), direction=direction)
        mini['decay_idx'] = decay_idx + offset
        if mini['decay_tau'] < min_decay:
            mini['success'] = False
            mini['failure'] = 'Min decay not met'
            return mini
        if mini['decay_tau'] > max_decay:
            mini['success'] = False
            mini['failure'] = 'Max decay exceeded'
            return mini

        # print('here')
        try:
            mini['decay_coord_x'] = xs[decay_idx]
            mini['decay_coord_x'] = xs[decay_idx]
            mini['decay_coord_y'] = single_exponent_constant(
                mini['decay_tau'],
                mini['decay_A'],
                mini['decay_tau'],
                mini['decay_C']
            ) * direction  #### add support for compound (add back subtracted baseline)
        except:
            pass

        ####### calculate halfwidth #######
        halfwidth_start_idx, halfwidth_end_idx, mini['halfwidth'] = self.calculate_mini_halfwidth(
            amp=mini['amp'], xs=xs, ys=ys, start_idx=baseline_idx, end_idx=end_idx,
            peak_idx=peak_idx, baseline=mini['baseline'], direction=direction)

        if halfwidth_end_idx is None or halfwidth_start_idx is None:
            if min_hw>0 and max_hw is not np.inf: # cannot check criteria
                mini['success'] = False
                mini['failure'] = 'Halfwidth could not be calculated'
                return mini
        else: # halfwidth was successfully found - check against criteria
            if mini['halfwidth'] < min_hw:
                mini['success'] = False
                mini['failure'] = 'Min halfwidth not met'
                return mini

            if mini['halfwidth'] > max_hw:
                mini['success'] = False
                mini['failure'] = 'Max halfwidth exceeded'
                return mini

            mini['halfwidth_start_idx'] = halfwidth_start_idx + offset
            mini['halfwidth_end_idx'] = halfwidth_end_idx + offset


            mini['halfwidth_start_coord_x'] = xs[halfwidth_start_idx]
            mini['halfwidth_start_coord_y'] = ys[halfwidth_start_idx]

            mini['halfwidth_end_coord_x'] = xs[halfwidth_end_idx]
            mini['halfwidth_end_coord_y'] = ys[halfwidth_end_idx]
        return mini
    def mark_greater_than_baseline(self,
                                   xs,
                                   ys,
                                   start_idx: int = 0,
                                   end_idx: int = None,
                                   lag: int = 100,
                                   delta_x: int = 100,
                                   min_amp: float = 0,
                                   max_amp: float = np.inf,
                                   direction: int=1):
        hits = [0]*len(ys)

        peaks=[]
        peak_idx = start_idx + lag + delta_x
        if end_idx is None:
            end_idx = len(ys)
        if end_idx - start_idx < lag + delta_x:
            return None  # not enough data points to analyze
        y_avg = np.mean(ys[start_idx: start_idx + lag])
        ys_avg = [0]*len(ys)
        ys_avg[peak_idx] = y_avg
        max_peak_idx = -1
        while peak_idx < end_idx:
            while ys[peak_idx] * direction > y_avg * direction + min_amp:
                if max_peak_idx < 0 or ys[peak_idx] * direction > ys[max_peak_idx] * direction:
                    max_peak_idx = peak_idx  # update maximum index pointer
                y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
                hits[peak_idx] = 1
                ys_avg[peak_idx] = y_avg
                start_idx += 1
                peak_idx += 1
            else:
                if max_peak_idx > 0:
                    # print(max_peak_idx)
                    peaks.append(max_peak_idx)
                    max_peak_idx = -1
            y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
            ys_avg[peak_idx] = y_avg
            start_idx += 1
            peak_idx += 1
        return hits, peaks, ys_avg
    def look_ahead_for_peak(self,
                            ys,
                            start_idx: int = 0,
                            end_idx: int = None,
                            lag: int = 100,
                            delta_x: int = 100,
                            min_amp: float = 0,
                            max_amp: float = np.inf,
                            direction: int = 1
                            ):
        """
        looks for candidate mini peak by comparing a data point further ahead in ys with average of a subset of ys

        Args:
            ys: numpy array of float, representing y-values
            start_idx: int representing the starting index for the search
            end_idx: int representing the final index for the search (non-inclusive). If None, defaults to length of ys
            lag: int representing the number of data points to average to estimate the baseline value
            delta_x: int representing the number of data points to look ahead from baseline
            min_amp: float representing the minimum amplitude required to consider a peak
            max_amp: float representing the maximum allowed amplitude for a peak
            direction: int {-1, 1}. -1 for current 1 for potential

        Returns:
            peak_idx: int representing the index of the candidate peak within ys
        """

        peak_idx = start_idx + lag + delta_x
        if end_idx is None:
            end_idx = len(ys)
        if end_idx - start_idx < lag + delta_x:
            return None # not enough data points to analyze
        y_avg = np.mean(ys[start_idx: start_idx + lag])
        max_peak_idx = -1
        while peak_idx < end_idx:
            while ys[peak_idx] * direction > y_avg * direction + min_amp:
                if max_peak_idx < 0 or ys[peak_idx] * direction > ys[max_peak_idx] * direction:
                    max_peak_idx = peak_idx # update maximum index pointer
                y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
                start_idx += 1
                peak_idx += 1
            else:
                if max_peak_idx > 0:
                    if ys[max_peak_idx] * direction > max_amp: # maximum amp reached
                        max_peak_idx = -1 # clear result
                    else:
                        return max_peak_idx
                y_avg = (y_avg * lag + ys[start_idx + lag] - ys[start_idx]) / lag
                start_idx += 1
                peak_idx += 1
        return None

    def find_mini_3(self,
                    xs,
                    ys,
                    lag: int=100,
                    min_amp:float=0.3,
                    max_amp:float=1,
                    direction:int=1,
                    range:int=100):
        index=0
        length = len(xs)
        hits= [0] * len(xs)
        while index < length:
            right_index = int(min(length, index+lag))
            peak_idx = self.find_peak_recursive(xs, ys, start=index, end=right_index, direction=direction)
            if peak_idx:
                peak = ys[peak_idx]
                base_idx, base = self.calculate_mini_baseline(
                    peak_idx,
                    ys,
                    lag=lag,
                    direction=direction,
                    stride=-1
                )
            else:
                base_idx, base = None, None

            if base and (peak - base) * direction > min_amp:
                hits[peak_idx] = 1
                index = int(peak_idx+1)
            else:
                index = int(index + lag/4)

        return hits




##############################
# Common Helper Functions
##############################

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
    point_idx = int(point[0]*sampling_rate)
    if radius == np.inf:
        search_xlim = (0, len(xs))
    else:
        search_xlim = (max(0, int(point_idx - radius*sampling_rate)), # search start index (0 or greater)
                       min(len(xs), int(point_idx + radius*sampling_rate))) # search end index (len(xs) or less)
    min_d = np.inf
    min_i = None
    for i in range(search_xlim[0], search_xlim[1], 1):
        d = euc_distance(point, (xs[i], ys[i]), xy_ratio)
        if d < min_d and d <= radius:
            min_d = d
            min_i = i
    if min_i:
        return min_d, min_i, (xs[min_i], ys[min_i])
    return None, None, None # no match

def euc_distance(point1, point2, xy_ratio):
    """
    calculates the euclidean distance between two points on a 2D surface

    point1: float tuple (x,y)
    point2: float tuple (x,y)
    xy_ratio: float - Used to normalize the weight of x- and y- distances
    """
    return hypot((point2[0] - point1[0]), (point2[1] - point1[1])*xy_ratio)

def search_index(x, l, rate=None):
    """
    used to search the index containing the value of interest in a sorted array
    x: x value to search
    l: array of list of x-values
    rate: float - the interval between each x-datapoint (inverse of sampling_rate)
    """
    if x < l[0]:
        return -1 # out of bounds
    if x > l[-1]:
        return len(l) # out of bounds
    if rate is None:
        rate = np.mean(l[1:6] - l[0:5]) # estimate recording rate
    est = int((x - l[0]) / rate)
    if est > len(l): # estimate is out of bounds
        est = len(l) - 1
    if l[est] == x:
        return est
    if l[est] > x: # estimate is too high
        while est >= 0: # loop until index hits 0
            if l[est] <= x: # loop until x-value is reached
                return est
            est -= 1 # increment down
        else:
            return est # out of bounds (-1)
    elif l[est] < x: # estimated index is too low
        while est < len(l): # loop until end of list
            if l[est] >= x: # loop until x-value is reached
                return est
            est += 1
        else:
            return est # out of bounds (len(l))

def single_exponent_constant(x, a, t, d):
    return a * np.exp(-(x) / t) + d


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
        elif n - 1 == idx[i-1] and n+1 == idx[i+1]:
            #0, [1, 2, 3], 4, 10, 11 --> '0'
            pass # do nothing
        elif n-1 == idx[i-1] and n+1 != idx[i+1]:
            #0, 1, 2, [3, 4, 10], 11 --> '0..4'
            s = '{}..{}'.format(s, n)
        elif n-1 != idx[i-1]:
            #0, 1, 2, 3, [4, 10, 11], 14, 16 --> '0..4,10' -->'0..4,10..11'
            s = '{},{}'.format(s, n)

    return s