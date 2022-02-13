"""
simplyfire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import numpy as np
import os.path
import matplotlib.pyplot as plt
from math import ceil, hypot, isnan, sqrt
from datetime import datetime

from pandas import DataFrame, Series
import pandas as pd
from scipy import optimize
from time import time  # debugging

############################################
# Analyzer functions
############################################

class Analyzer():
    def __init__(self, plot_mode='continuous'):
        self.plot_mode = plot_mode

        # initialize dataframes
        # self.mini_df = DataFrame()

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

    ###################
    # save/load
    ####################
    def load_minis_from_file(self, filename):
        return pd.read_csv(filename, index_col=0)

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
    def calculate_frequency(self, mini_df, channel):
        df = mini_df[mini_df['channel']==channel]
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
    if not s:
        return True
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
