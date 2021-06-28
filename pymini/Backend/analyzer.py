# specific maths for event detection
# most likely won't require a class
from utils import recording
from config import config
import numpy as np
import datetime
from scipy import optimize
import time

import matplotlib.pyplot as plt

from DataVisualizer import param_guide, trace_display  # remove this during deployment


### this module does all the calculations for event detection and modeling
### this module should be able to function on its own

def open_trace(filename, channel=0):
    global trace
    trace = recording.Trace(filename)
    trace.set_channel(channel)


def search_index(x, l, rate=None):
    if rate is None:
        rate = np.mean(l[1:6] - l[0:5])
    est = int((x - l[0]) * rate)
    if est >= len(l):
        return len(l)  # out of bounds
    elif l[est] == x:
        return est
    elif l[est] > x:  # overshot
        while est >= 0:
            if l[est] < x:
                return est + 1
            est -= 1
    elif l[est] < x:  # need to go higher
        while est < len(l):
            if l[est] > x:
                return est
            est += 1
    return est  # out of bounds


def find_peak_at(
        x,
        xs=None,
        ys=None,
        sampling_rate=None,
        x_unit='seconds',
        y_unit="",
        xlim=None,
        ylim=None,
        direction=1,
        lag=config.detector_points_baseline,
        points_search=config.detector_points_search,
        max_points_baseline=config.detector_max_points_baseline,
        max_points_decay=config.detector_max_points_decay,
        min_amp=config.detector_min_amp,
        min_decay=config.detector_min_decay,
        max_decay=config.detector_max_decay,
        min_hw=config.detector_min_hw,
        max_hw=config.detector_max_hw,
        min_rise=config.detector_min_rise,
        max_rise=config.detector_max_rise,
        decay_func_type=config.detector_decay_func_type,
        decay_func_constant=config.detector_decay_func_constant,
        decay_fit_ftol=config.detector_decay_fit_ftol,
        prev=None
):
    """
    searches for a synaptic event centered around x using the parameters given
    :param decay_func_type:
    :param decay_fit_percent:
    :param decay_func_constant:
    :param x: central x-coordinate used for the search. float. must be within the y-data of the trace
    :param xlim: x-axis search limit. tuple(min_x, max_x)
    :param ylim: y-axis search limit. tuple (min_y, max_y)
    :param direction: expected direction of the synaptic event. int 1 = positive, -1 = negative
    :param xs: x data, given as a 1D numpy array
    :param ys: y data, given as a 1D numpy array
    :param lag: number of points to average to find start/end (baseline) of the event. int > 10
    :param points_search: number of data points around central x to search for an event peak. (*not this is _not_ float in seconds)
    :param max_points_baseline: maximum number of data points from candidate peak to look for a baseline. If baseline is not found within this limit, the candidate peak is rejected
    :param max_points_decay: maximum number of data points from candidate peak to include for decay fitting. - used if the 'end' cannot be found (i.e. compound peaks)
    :param min_amp: minimum event amplitude. a candidate peak with a smaller amplitude is rejected
    :param min_decay: minimum decay constant. a candidate peak with a smaller decay constant is rejected. float >= 0
    :param max_decay: maximum decay constant. a candidate peak with a larger decay constant is rejected. float >= 0 or str 'None'
    :param min_hw: minimum halfwidth. a candidate peak with a  smaller halfwidth is rejected. float >= 0
    :param max_hw: maximum halfwidth. a candidate peak with a larger halfwidth is rejected. float >=0 or str 'None'
    :param min_rise: minimum rise constant. a candidate peak with a smaller rise is rejected. float >= 0
    :param max_rise: maximum rise constant. a candidate peak with a larger rise is rejected. float >=0 or str 'None'
    :return:
    """
    if xs is None:
        xs = trace.get_xs(mode='continuous')
        x_unit = trace.x_unit
    if ys is None:
        ys = trace.get_ys(mode='continuous')
        y_unit = trace.y_unit

    x_idx = search_index(x, xs, sampling_rate)

    # initialize search range for peak
    start_idx = x_idx - points_search
    end_idx = x_idx + points_search

    try:
        xlim_idx = (
            search_index(xlim[0], xs, sampling_rate),
            search_index(xlim[1], xs, sampling_rate)
        )
    except:
        xlim_idx = (0, -1)

    # narrow search range by xlim
    start_idx = max(start_idx, xlim_idx[0])
    end_idx = min(end_idx, xlim_idx[1])

    # find where y values are beyond limits
    try:
        y_high = ys[start_idx:end_idx] > ylim[1]
        y_low = ys[start_idx:end_idx] < ylim[0]

        ylim_idx = np.where(y_high | y_low)[0] + start_idx  # get all indices where y is outside of ylim
        y_left, y_right = None, None
        if len(ylim_idx) > 0:  # there are ys that are beyond ylim
            for i, y_idx in enumerate(ylim_idx):  # start from left to right
                if y_idx > x_idx:  # y_idx passed x_idx (right side of x_idx)
                    y_right = y_idx
                    if y_idx[i - 1] < y_right:
                        y_left = y_idx[i - 1]
                    break
            else:
                if y_idx[-1] < x_idx:
                    y_left = y_idx[-1]
        if y_left:
            start_idx = max(start_idx, y_left)
        if y_right:
            end_idx = min(end_idx, y_right)
    except:
        pass

    ######### find peak ##########
    data = find_peak_recursive(
        start_idx,
        end_idx,
        xs=xs,
        ys=ys,
        x_unit=x_unit,
        y_unit=y_unit,
        direction=direction,
        lag=lag,
        max_points_baseline=max_points_baseline,
        max_points_decay=max_points_decay,
        min_amp=min_amp,
        min_decay=min_decay,
        max_decay=max_decay,
        min_hw=min_hw,
        max_hw=max_hw,
        min_rise=min_rise,
        max_rise=max_rise,
        decay_func_type=decay_func_type,
        decay_func_constant=decay_func_constant,
        decay_fit_ftol=decay_fit_ftol,
        prev=prev
    )

    return data
    pass


def find_peak_recursive(
        start_idx,
        end_idx,
        xs,
        ys,
        x_unit=None,
        y_unit=None,
        direction=1,
        lag=config.detector_points_baseline,
        max_points_baseline=config.detector_max_points_baseline,
        max_points_decay=config.detector_max_points_decay,
        min_amp=config.detector_min_amp,
        min_decay=config.detector_min_decay,
        max_decay=config.detector_max_decay,
        min_hw=config.detector_min_hw,
        max_hw=config.detector_max_hw,
        min_rise=config.detector_min_rise,
        max_rise=config.detector_max_rise,
        decay_func_type=config.detector_decay_func_type,
        decay_func_constant=config.detector_decay_func_constant,
        decay_fit_ftol=config.detector_decay_fit_ftol,
        prev=None
):
    data = {}
    data['start_idx'] = start_idx
    data['end_idx'] = end_idx

    ######## search candidate peak ##########
    peak_y = max(ys[start_idx:end_idx] * direction)
    peaks = np.where(ys[start_idx:end_idx] * direction == peak_y)[0] + start_idx  # list of indices where ys is at peak
    peak_idx = peaks[0]  # take the earliest time point as candidate

    FUDGE = 10  # adjust if needed

    if end_idx - start_idx < FUDGE * 2:
        data['msg'] = 'extremum_not_found'
        data['success'] = False
        return data

    # check if the peak is only a cut-off of a slope:
    # recursively narrow the search area and look for another local extremum within the range

    if peak_idx < start_idx + FUDGE:  # peak is too close to the left end of search range
        return find_peak_recursive(start_idx + FUDGE, end_idx, xs, ys, x_unit, y_unit, direction=direction, lag=lag,
                                   max_points_baseline=max_points_baseline,
                                   max_points_decay=max_points_decay,
                                   min_amp=min_amp,
                                   min_decay=min_decay,
                                   max_decay=max_decay,
                                   min_hw=min_hw,
                                   max_hw=max_hw,
                                   min_rise=min_rise,
                                   max_rise=max_rise,
                                   decay_func_type=decay_func_type,
                                   decay_func_constant=decay_func_constant,
                                   decay_fit_ftol=decay_fit_ftol,
                                   prev=prev
                                   )
    if peak_idx > end_idx - FUDGE:  # peak is too close to the right end of search range
        return find_peak_recursive(start_idx, end_idx - FUDGE, xs, ys, x_unit, y_unit, direction=direction, lag=lag,
                                   max_points_baseline=max_points_baseline,
                                   max_points_decay=max_points_decay,
                                   min_amp=min_amp,
                                   min_decay=min_decay,
                                   max_decay=max_decay,
                                   min_hw=min_hw,
                                   max_hw=max_hw,
                                   min_rise=min_rise,
                                   max_rise=max_rise,
                                   decay_func_type=decay_func_type,
                                   decay_func_constant=decay_func_constant,
                                   decay_fit_ftol=decay_fit_ftol,
                                   prev=prev
                                   )

    for i in ['direction',
        'lag', 'max_points_baseline', 'max_points_decay', 'min_amp', 'min_decay',
        'min_hw', 'max_hw', 'min_rise', 'max_rise', 'decay_fit_ftol'
    ]:
        data[i] = locals()[i]


    data['t'] = xs[peak_idx]
    data['t_unit'] = x_unit
    data['datetime'] = datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S')
    data['peak_coord_x'] = xs[peak_idx]
    data['peak_coord_y'] = ys[peak_idx]
    data['peak_idx'] = peak_idx

    ######### search start of event ##########

    base_idx = peak_idx - 1

    # y_avg is always going to be a positive peak
    y_avg = np.mean(ys[base_idx - lag + 1:base_idx + 1] * direction)
    # should include the base_idx in the calculation, also, why was it base_idx+2?
    # baseline_x = [xs[base_idx]]
    # baseline_y = [y_avg]
    base_idx -= 1

    while base_idx > max(peak_idx - max_points_baseline + lag, lag):
        y_avg = (y_avg * (lag) + (ys[base_idx - lag] - ys[base_idx]) * direction) / (lag)
        # equivalent to np.mean(ys[base_idx - lag: base_idx]))
        # baseline_x.append(xs[base_idx])
        # baseline_y.append(y_avg)
        if y_avg >= ys[base_idx] * direction:
            break
        base_idx -= 1
    else:
        data['msg'] = 'start_of_event_not_found'
        # return results
        data['success'] = False
        return data  # could not find start
    data['start_coord_x'] = xs[base_idx]
    data['start_coord_y'] = y_avg * direction  # the point may not be on the trace itself

    data['baseline'] = y_avg * direction  # instead of the coord right at the interception (can be different from start_coord_x
    data['baseline_unit'] = y_unit
    data['t_start'] = xs[base_idx]
    data['start_idx'] = base_idx  # use this to map back to data present in the trace
    # data['baseline_plot'] = (baseline_x, baseline_y)

    ###### determine amplitude ########
    data['amp'] = (ys[peak_idx] - y_avg * direction)  # implement decay extrapolation later
    data['amp_unit'] = y_unit
    if data['peak_coord_y'] * direction < data['baseline']:
        data['msg'] = 'baseline_unreliable'
        data['success'] = False
        return data
    if data['amp'] * direction < min_amp:
        data['msg'] = 'minimum_amplitude_unmet'
        data['success'] = False
        return data

    end_idx = peak_idx
    y_avg = np.mean(ys[end_idx: end_idx + lag]) * direction
    # baseline_end_x = [xs[end_idx]]
    # baseline_end_y = [y_avg]
    end_idx += 1
    while end_idx < len(ys) - lag:
        y_avg = (y_avg * (lag) + (ys[end_idx + lag] - ys[end_idx]) * direction) / (
            lag)  # equivalent to np.mean(ys[end_idx + 1: end_idx + lag + 1])
        # baseline_end_x.append(xs[end_idx])
        # baseline_end_y.append(y_avg)
        if y_avg > ys[end_idx] * direction:
            data['end_coord_x'] = xs[end_idx]
            data['end_coord_y'] = y_avg  # the point may not be on the trace itself
            data['t_end'] = xs[end_idx]
            data['end_idx'] = end_idx  # use this to map to trace data
            break

        end_idx += 1
    else:
        data['end_coord_x'] = None
        data['end_coord_y'] = None
        data['t_end'] = None

    # data['baseline_end_plot'] = (baseline_end_x, baseline_end_y)

        # might not necessarily be a bad thing - the peak is still picked out.

    ####### calculate rise #######
    data['rise_const'] = (xs[peak_idx] - xs[base_idx]) * 1000
    data['rise_unit'] = 'ms' if x_unit in ['s', 'seconds', 'second', 'sec'] else '{} E-3'.format(
        x_unit)
    if data['rise_const'] < min_rise:
        data['msg'] = 'minimum_rise_unmet'
        data['success'] = False
        return data
    try:
        if data['rise_const'] > max_rise:
            data['msg'] = 'maximum_rise_surpassed'
            data['success'] = False
            return data
    except:
        pass

    ###### calculate halfwidth #####
    hw_idx_left = base_idx
    while ys[hw_idx_left] * direction < (data['baseline'] + data['amp']/2) * direction and hw_idx_left < len(xs):
        hw_idx_left+= 1

    hw_idx_right = peak_idx
    while ys[hw_idx_right] * direction > (data['baseline'] + data['amp']/2) * direction and hw_idx_right < len(xs):
        hw_idx_right += 1

    try:
        data['halfwidth'] = (xs[hw_idx_right] - xs[hw_idx_left]) * 1000
        data['halfwidth_unit'] = 'ms' if x_unit in ['s', 'seconds', 'second', 'sec'] else '{} E-3'.format(
            x_unit)
        data['halfwidth_idx'] = (hw_idx_left, hw_idx_right)
    except:
        data['msg'] = 'halfwidth_could_not_be_calculated'
        data['success'] = False
        return data
    if data['halfwidth'] < min_hw:
        data['msg'] = 'minimum_halfwidth_unmet'
        data['success'] = False
        return data
    try:
        if data['halfwidth'] > max_hw:
            data['msg'] = 'maximum_halfwidth_surpassed'
            data['success'] = False
            return data
    except:
        pass

    ################ DECAY!!!! ###################
    # scipy curve_fit: need to define a function
    # Zero xs and ys using the peak t and baseline Vm
    # def rise_decay(x, t_2, t_1):
    #     return data['amp'] * direction * 2 * (1 - np.exp(-x / t_1)) * (np.exp(-(x) / t_2))

    def single_exponent_constant(x, a, t, d):
        return a * np.exp(-(x) / t) + d

    def single_exponent(x, a, t):
        return a * np.exp(-(x) / t)

    def double_exponent_constant(x, a_1, t_1, a_2, t_2, c):
        return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-((x) / t_2)) + c

    def double_exponent(x, a_1, t_1, a_2, t_2):
        return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-(x) / t_2)

    # def triple_exponent_constant(x, t_1, t_2, t_3, c):
    #     a = data['amp'] * direction
    #     return a * direction * np.exp(-(x) / t_1) + a * np.exp(-(x) / t_2) + a * np.exp(-(x) / t_3) + c
    def triple_exponent_constant(x, a_1, t_1, a_2, t_2, a_3, t_3, c):
        return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-(x) / t_2) + a_3 * np.exp(-(x) / t_3) + c

    def triple_exponent(x, a_1, t_1, a_2, t_2, a_3, t_3):
        return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-(x) / t_2) + a_3 * np.exp(-(x) / t_3)

    x_data = (xs[peak_idx:min(peak_idx + max_points_decay, len(xs))] - xs[peak_idx]) * 1000
    y_data = (ys[peak_idx:min(peak_idx + max_points_decay, len(xs))] - data['baseline']) * direction

    fmap = {(1, ""): single_exponent,
            (1, '1'): single_exponent_constant,
            (2, ""): double_exponent,
            (2, "1"): double_exponent_constant,
            (3, ""): triple_exponent,
            (3, "1"): triple_exponent_constant
            }
    decay_func = fmap[(decay_func_type, decay_func_constant)]
    try:
        results = optimize.curve_fit(decay_func,
                                 x_data,
                                 y_data,
                                 ftol=decay_fit_ftol,
                                 maxfev=15000)
    except Exception as e:
        data['msg'] = 'decay fit unsuccessful \n {}'.format(e)
        data['success'] = False
        return data
    y_data = np.array(decay_func(x_data, *results[0]))
    e = np.where(y_data < data['amp'] * direction * np.exp(-1))[0][0]
    data['decay_const'] = x_data[e]
    data['decay_coord_x'] = xs[peak_idx] + data['decay_const'] / 1000
    data['decay_coord_y'] = data['baseline'] + y_data[e] * direction
    data['decay_fit'] = results[0]
    data['decay_func'] = decay_func.__name__
    data['decay_unit'] = 'ms' if x_unit in ['s', 'seconds', 'second', 'sec'] else '{} E-3'.format(
        x_unit)
    if data['decay_const'] < min_decay:
        data['msg'] = 'minimum_decay_constant_unmet'
        data['success'] = False
        return data
    try:
        if data['decay_const'] > max_decay:
            data['msg'] = 'maximum_decay_exceeded'
            data['success'] = False
            return data
    except:
        pass
    data['msg'] = 'success!'
    data['success'] = True

    return data
    #### other fitting functions:

    # if decay_func_type == '4' or decay_func_type == 4:
    #     # x_data = (xs[start_idx:end_idx] - xs[start_idx]) * 1000
    #     # y_data = (ys[start_idx:end_idx] - data['baseline']) * direction
    #     # decay_func = rise_decay
    #     # p0=[3, 0.5]
    #     # results = optimize.curve_fit(decay_func,
    #     #                              x_data,
    #     #                              y_data,
    #     #                              p0=p0,
    #     #                              ftol=decay_fit_percent,
    #     #                              maxfev=15000)
    #     pass # not supported
    # else:
    #     x_data = (xs[peak_idx:min(peak_idx + max_points_decay, len(xs))] - xs[peak_idx]) * 1000
    #     y_data = (ys[peak_idx:min(peak_idx + max_points_decay, len(xs))] - data['baseline']) * direction
    #     # x_data = (xs[peak_idx:end_idx] - xs[peak_idx]) * 1000
    #     # y_data = (ys[peak_idx:end_idx] - data['baseline']) * direction
    #
    #
    #     if decay_func_type == '1' or decay_func_type == 1:
    #         if decay_func_constant:
    #             decay_func = single_exponent_constant
    #         else:
    #             decay_func = single_exponent
    #     elif decay_func_type == '2' or decay_func_type == 2:
    #         if decay_func_constant:
    #             decay_func = double_exponent_constant
    #         else:
    #             decay_func = double_exponent
    #     elif decay_func_type == '3' or decay_func_type == 3:
    #         if decay_func_constant:
    #             decay_func = triple_exponent_constant
    #         else:
    #             decay_func = triple_exponent
    #     results = optimize.curve_fit(decay_func,
    #                                  x_data,
    #                                  y_data,
    #                                  ftol=decay_fit_percent,
    #                                  maxfev=15000)


def single_exponent_constant(x, a, t, d):
    return a * np.exp(-(x) / t) + d


def single_exponent(x, a, t):
    return a * np.exp(-(x) / t)


def double_exponent_constant(x, a_1, t_1, a_2, t_2, c):
    return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-((x) / t_2)) + c


def double_exponent(x, a_1, t_1, a_2, t_2):
    return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-(x) / t_2)


def triple_exponent_constant(x, a_1, t_1, a_2, t_2, a_3, t_3, c):
    return a_1 * np.exp(-(x ) / t_1) + a_2 * np.exp(-(x ) / t_2) + a_3 * np.exp(-(x ) / t_3) + c
# def triple_exponent_constant(x, a, t_1,t_2, t_3, c):
#     return a * np.exp(-(x ) / t_1) + a * np.exp(-(x ) / t_2) + a * np.exp(-(x ) / t_3) + c


def triple_exponent(x, a_1, t_1, a_2, t_2, a_3, t_3):
    return a_1 * np.exp(-(x) / t_1) + a_2 * np.exp(-(x) / t_2) + a_3 * np.exp(-(x) / t_3)

def rise_decay(x, a, t_2, t_1):
    return a * (1 - np.exp(-x/t_1))*(np.exp(-(x)/t_2))

# def single_exponent(x, V, s, t, b, d):
#     #V = Vm
#     #s= start
#     #t =tau
#     #b = baseline
#     #d = adjust at the end
#     return V * np.exp(-(x-s)/t) + b + d
