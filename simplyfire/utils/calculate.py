import numpy as np
import math
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


def find_closest_sweep_to_point(recording, point, xlim=None, ylim=None, height=1, width=1, radius=np.inf,
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
    return math.hypot((point2[0] - point1[0]), (point2[1] - point1[1]) * xy_ratio)

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
