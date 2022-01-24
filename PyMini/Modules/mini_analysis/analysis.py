from typing import Dict, List, Any, Union

from PyMini import app
from PyMini.Backend import analyzer2
import os
import pandas as pd
import numpy as np

def find_mini_manual(x, params, mini_df):
    # connect to param_guide later
    xlim = app.trace_display.ax.get_xlim()
    xlim = (min(xlim), max(xlim))
    ylim = app.trace_display.ax.get_ylim()
    ylim = (min(ylim), max(ylim))

    # convert % x-axis to points search using sampling rate?
    r = (xlim[1] - xlim[0]) * float(params['manual_radius']) / 100
    xs = app.trace_display.ax.lines[0].get_xdata()
    ys = app.trace_display.ax.lines[0].get_ydata()

    mini = app.interface.al.find_mini_manual(xlim=(max(x - r, xlim[0]), min(x + r, xlim[1])), xs=xs, ys=ys,
                           x_sigdig=app.interface.recordings[0].x_sigdig,
                           sampling_rate=app.interface.recordings[0].sampling_rate, channel=app.interface.recordings[0].channel,
                           reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                           x_unit=app.interface.recordings[0].x_unit, **params)

    return mini

def find_mini_in_range(params, mini_df, xlim=None, ylim=None):
    app.pb['value'] = 0
    app.pb.update()

    try:
        xs = app.trace_display.ax.lines[0].get_xdata()
        ys = app.trace_display.ax.lines[0].get_ydata()
    except:
        return

    # temp_filename = os.path.join(pkg_resources.resource_filename('PyMini', 'temp/'), 'temp_{}.temp'.format(get_temp_num()))
    # save_events(temp_filename)
    # add_undo([
    #     lambda f=temp_filename: al.load_minis_from_file(f),
    #     restore_events,
    #     lambda msg='Undo auto mini detection in range: {} - {}'.format(xlim[0], xlim[1]): detector_tab.log(msg)
    # ])

    df = app.interface.al.find_mini_auto(xlim=xlim, xs=xs, ys=ys, x_sigdig=app.interface.recordings[0].x_sigdig,
                               sampling_rate=app.interface.recordings[0].sampling_rate, channel=app.interface.recordings[0].channel,
                      reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                               x_unit=app.interface.recordings[0].x_unit, progress_bar=app.pb, **params)
    return df

def open_minis(filename):
    filetype = os.path.splitext(filename)[1]
    if filetype in ('.csv', '.temp', '.event', '.mini'):
        df = open_mini_csv(filename)
    elif filetype == '.minipy':
        df = open_minipy(filename)
    df = df.replace({np.nan: None})
    return df

def open_mini_csv(filename):
    df = pd.read_csv(filename, comment='@')
    return df

def open_minipy(filename):
    """
    open mini files from Minipy (ancestral version)
    """
    channel = 0
    minis = []
    header_idx = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        for l in lines:
            info = l.strip().split(',')
            if info[0] == "@Trace":
                recording_filename = info[1]
            elif info[0] == '@Channel':
                channel = int(info[1])
            elif info[0] == '@Header':
                for i,h in enumerate(info):
                    header_idx[h] = i
                xs = app.interface.recordings[0].get_xs(mode='continuous', channel=channel)
                ys= app.interface.recordings[0].get_ys(mode='continuous', channel=channel)
            elif info[0] == '@Data':
                mini = {
                    't':float(info[header_idx['x']]),
                    'peak_coord_x':float(info[header_idx['x']]),
                    'peak_coord_y':float(info[header_idx['y']]),
                    'amp':float(info[header_idx['Vmax']])*float(info[header_idx['direction']]),
                    'baseline':float(info[header_idx['baseline']]),
                    'compound': False,
                    'decay_A':float(info[header_idx['Vmax']]),
                    'decay_const':float(info[header_idx['tau']])*1000,
                    'decay_baseline':0,
                    'decay_coord_x':float(info[header_idx['tau_x']]),
                    'decay_coord_y':float(info[header_idx['tau_y']]),
                    'decay_max_points':int(float(app.widgets['detector_core_decay_max_interval'].get())/1000*recordings[0].sampling_rate),
                    'failure':None,
                    'lag':int(info[header_idx['lag']]),
                    'rise_const':float(info[header_idx['rise_time']])*1000,
                    'start_coord_x':float(info[header_idx['left_x']]),
                    'start_coord_y':float(info[header_idx['left_y']]),
                    'amp_unit':app.interface.recordings[0].channel_units[channel],
                    'baseline_unit':app.interface.recordings[0].channel_units[channel],
                    'decay_unit':'ms',
                    'halfwidth_unit': 'ms',
                    'rise_unit':'ms',
                    'channel':channel,
                    'delta_x':0,
                    'direction':int(info[header_idx['direction']]),
                    'end_coord_x':float(info[header_idx['right_x']]),
                    'end_coord_y':float(info[header_idx['right_y']]),
                    'max_amp':np.inf,
                    'min_amp':0.0,
                    'max_rise': np.inf,
                    'min_rise': 0.0,
                    'max_decay': np.inf,
                    'min_decay': 0.0,
                    'max_hw': np.inf,
                    'min_hw': 0.0,
                    'max_s2n':np.inf,
                    'min_s2n':0.0,
                    'stdev_unit':app.interface.recordings[0].channel_units[channel],
                    'success':True,
                }
                pass
                mini['start_idx'] = int(analyzer2.search_index(mini['start_coord_x'], xs, rate=app.interface.recordings[0].sampling_rate))
                mini['baseline_idx'] = mini['start_idx']
                mini['base_idx_L'] = mini['start_idx'] - mini['lag']
                mini['base_idx_R'] = mini['start_idx']
                mini['decay_idx'] = int(analyzer2.search_index(mini['start_coord_x']+mini['decay_const'], xs, rate=app.interface.recordings[0].sampling_rate))
                mini['peak_idx'] = int(analyzer2.search_index(mini['peak_coord_x'], xs, rate=app.interface.recordings[0].sampling_rate))
                mini['decay_start_idx'] = mini['peak_idx']
                mini['end_idx'] = analyzer2.search_index(mini['end_coord_x'], xs, rate=app.interface.recordings[0].sampling_rate)
                mini['stdev'] = np.std(ys[mini['base_idx_L']:mini['base_idx_R']])

                #try finding halfwidth
                hw_start_idx,hw_end_idx = app.interface.al.find_mini_halfwidth(amp=mini['amp'],
                                                                 xs=xs[mini['baseline_idx']:mini['end_idx']],
                                                                 ys=ys[mini['baseline_idx']:mini['end_idx']],
                                                                 peak_idx=mini['peak_idx'] - mini['baseline_idx'],
                                                                 baseline=mini['baseline'],
                                                                 direction=mini['direction'])
                if hw_start_idx is not None and hw_end_idx is None:
                    if app.widgets['detector_core_extrapolate_hw'].get():
                        t = np.log(0.5)*(-1)*mini['decay_const']/1000
                        hw_end_idx = analyzer2.search_index(xs[mini['peak_idx']]+t,xs[mini['baseline_idx']:], app.interface.recordings[0].sampling_rate)
                if hw_start_idx is None or hw_end_idx is None:
                    mini['halfwidth'] = 0 # could not be calculated
                else:
                    mini['halfwidth_start_idx'] = hw_start_idx + mini['baseline_idx']
                    mini['halfwidth_end_idx'] = hw_end_idx + mini['baseline_idx']
                    mini['halfwidth'] = (xs[int(mini['halfwidth_end_idx'])] - xs[int(mini['halfwidth_start_idx'])])*1000
                    mini['halfwidth_start_coord_x'] = xs[mini['halfwidth_start_idx']]
                    mini['halfwidth_end_coord_x'] = xs[mini['halfwidth_end_idx']]
                    mini['halfwidth_start_coord_y'] = mini['halfwidth_end_coord_y'] = mini['baseline']+0.5*mini['amp']


                minis.append(mini)
        if len(minis)>0:
            df = pd.DataFrame.from_dict(minis)
            return df
        return pd.DataFrame() # empty