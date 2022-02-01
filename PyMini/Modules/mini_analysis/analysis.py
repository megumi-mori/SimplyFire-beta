import numpy as np
import pandas as pd


def filter_mini(mini_df: pd.DataFrame = None,
                xlim=None,
                min_amp: float = 0.0,
                max_amp: float = np.inf,
                min_rise: float = 0.0,
                max_rise: float = np.inf,
                min_decay: float = 0.0,
                max_decay: float = np.inf,
                min_hw: float = 0.0,
                max_hw: float = np.inf,
                min_drr: float = 0.0,
                max_drr: float = np.inf,
                min_s2n: float = 0.0,
                max_s2n: float = np.inf,
                **kwargs):
    """
    Filters the previously found mini based on criteria
    df: DataFrame containing mini data
        If None, defaults to mini_df
    xlim: x-axis limits to apply the filter (the peak x-value ('t') is considered)
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
        return None
    if xlim is None:
        xlim = (0.0, np.inf)
    if min_amp is not None:
        mini_df = mini_df[
            (mini_df['amp'] * mini_df['direction'] >= min_amp) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
    if max_amp is not None:
        mini_df = mini_df[
            (mini_df['amp'] * mini_df['direction'] < max_amp) | (mini_df['t'] < xlim[0]) | (mini_df['t'] > xlim[1])]
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
        mini_df = mini_df[(mini_df['decay_const'] / mini_df['rise_const'] > min_drr) | (mini_df['t'] < xlim[0]) | (
                mini_df['t'] > xlim[1])]
    if max_drr is not None:
        mini_df = mini_df[(mini_df['decay_const'] / mini_df['rise_const'] < max_drr) | (mini_df['t'] < xlim[0]) | (
                mini_df['t'] > xlim[1])]
    if min_s2n is not None and min_s2n > 0:
        mini_df = mini_df[
            (mini_df['stdev'] is not None) & (mini_df['amp'] * mini_df['direction'] / mini_df['stdev'] > min_s2n)]
    if max_s2n is not None and max_s2n < np.inf:
        mini_df = mini_df[
            (mini_df['stdev'] is not None) & (mini_df['amp'] * mini_df['direction'] / mini_df['stdev'] < max_s2n)]

    return mini_df
