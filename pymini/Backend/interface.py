# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog
from DataVisualizer import data_display, log_display, trace_display, param_guide
import os
from Layout import detector_tab
import matplotlib as mpl
from Backend import analyzer
import gc
import pandas as pd
import numpy as np

from utils import recording

### this module connects the analyzer and the gui

df = pd.DataFrame()
df.clear = lambda:df.iloc[0:0]


def ask_open_trace():
    gc.collect()
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    if fname:
        pymini.trace_filename = fname
    else:
        return None

    open_trace(fname)


def open_trace(fname):
    # trace stored in analyzer
    analyzer.open_trace(fname)

    log_display.open_update(fname)

    # update save file directory
    if pymini.widgets['config_file_autodir'].get() == '1':
        mpl.rcParams['savefig.directory'] = os.path.split(fname)[0]

    # check if channel number is specified by user:
    if pymini.widgets['force_channel'].get() == '1':
        try:
            analyzer.trace.set_channel(int(pymini.widgets['force_channel_id'].get()) - 1)  # 1 indexing
        except Exception as e:
            print(analyzer.trace.channel)
            print(e)
            pass

    trace_display.clear()
    data_display.clear()

    trace_display.ax.set_xlabel(analyzer.trace.x_label)
    trace_display.ax.set_ylabel(analyzer.trace.y_label)

    pymini.widgets['trace_info'].set(
        '{}: {}Hz : {} channel{}'.format(
            analyzer.trace.fname,
            analyzer.trace.sampling_rate,
            analyzer.trace.channel_count,
            's' if analyzer.trace.channel_count > 1 else ""
        )
    )
    trace_display.ax.autoscale(enable=True, axis='both', tight=True)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        plot_continuous()
    else:
        plot_overlay()

    param_guide.update()

    if pymini.widgets['force_axis_limit'].get() == '1':
        trace_display.set_axis_limit('x', (pymini.widgets['min_x'].get(), pymini.widgets['max_x'].get()))
        trace_display.set_axis_limit('y', (pymini.widgets['min_y'].get(), pymini.widgets['max_y'].get()))

    pymini.widgets['channel_option'].clear_options()

    for i in range(analyzer.trace.channel_count):
        pymini.widgets['channel_option'].add_option(
            label='{}: {}'.format(i+1, analyzer.trace.channel_labels[i]),
            command=lambda c=i:_change_channel(c)
        )
    # starting channel was set earlier in the code
    pymini.widgets['channel_option'].set('{}: {}'.format(analyzer.trace.channel + 1, analyzer.trace.y_label))

    trace_display.canvas.draw()

def _change_channel(num):
    analyzer.trace.set_channel(num)
    pymini.widgets['channel_option'].set('{}: {}'.format(analyzer.trace.channel + 1, analyzer.trace.y_label))
    xlim = trace_display.ax.get_xlim()
    trace_display.clear()
    trace_display.plot_trace(analyzer.trace.get_xs(mode='continuous'),
                          analyzer.trace.get_ys(mode='continuous'),
                             draw=True,
                             relim=True)
    trace_display.ax.set_xlim(xlim)
    trace_display.canvas.draw()


def plot_continuous():
    trace_display.plot_trace(analyzer.trace.get_xs(mode='continuous'),
                             analyzer.trace.get_ys(mode='continuous'),
                             draw=True,
                             relim=True)
    pass


def plot_overlay():
    print('overlay currently not supported')
    pass


def configure(key, value):
    globals()[key] = value


def search_event_from_click(x):
    pass


#######################################

def pick_event_manual(x):
    # dir = 1
    dir = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
    # if pymini.widgets['detector_direction'].get() == 'negative':
    #     dir = -1
    try:
        max_decay = float(pymini.widgets['detector_max_decay'].get())
    except:
        max_decay = None
    try:
        max_hw = float(pymini.widgets['detector_max_hw'].get())
    except:
        max_hw = None
    try:
        max_rise = float(pymini.widgets['detector_max_rise'].get())
        print('max rise is: {}'.format(max_rise))
    except:
        max_rise = None
    xlim=trace_display.ax.get_xlim()
    xlim = (min(xlim), max(xlim))
    ylim=trace_display.ax.get_ylim()
    ylim = (min(ylim), max(ylim))

    if pymini.widgets['trace_mode'].get() == 'continuous':
        xs = trace_display.ax.lines[0].get_xdata()
        ys = trace_display.ax.lines[0].get_ydata()
        # assumptions that can be safely made:
        # the plot should only have 1 trace (the continuous trace)
        # the only line plotted is the data of the entire trace
        # the sampling rate of the plotted trace is the same as the sampling rate of the original trace
        data = analyzer.find_peak_at(
            x=x,
            xs=xs,
            ys=ys,
            sampling_rate=analyzer.trace.sampling_rate,
            x_unit=analyzer.trace.x_unit,
            y_unit=analyzer.trace.y_unit,
            xlim=xlim,
            ylim=ylim,
            dir=dir,
            lag=int(pymini.widgets['detector_points_baseline'].get()),
            points_search=int(pymini.widgets['detector_points_search'].get()),
            max_points_baseline=int(pymini.widgets['detector_max_points_baseline'].get()),
            max_points_decay=int(pymini.widgets['detector_max_points_decay'].get()),
            min_amp=float(pymini.widgets['detector_min_amp'].get()),
            min_decay=float(pymini.widgets['detector_min_decay'].get()),
            max_decay=max_decay,
            min_hw=float(pymini.widgets['detector_min_hw'].get()),
            max_hw=max_hw,
            min_rise=float(pymini.widgets['detector_min_rise'].get()),
            max_rise=max_rise,
            decay_func_type=int(pymini.widgets['detector_decay_func_type'].get()),
            decay_func_constant=pymini.widgets['detector_decay_func_constant'].get(),
            decay_fit_percent=float(pymini.widgets['detector_decay_fit_percent'].get())
        )

        if pymini.widgets['window_param_guide'].get() == '1':
            report_to_param_guide(xs, ys, data)

        print(detector_tab.changed)
        if detector_tab.changed:
            log_display.search_update('Manual')
            log_display.param_update(dict([(i, pymini.widgets[i].get()) for i in pymini.widgets.keys() if 'detector_' in i]))
            detector_tab.changed = False

    pass

def report_to_param_guide(xs, ys, data):
    param_guide.clear()
    direction = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
    param_guide.msg_label.insert('{}\n'.format(data['error']))
    param_guide.msg_label.insert(
        'Candidate peak: {:.3f},{:.3f}\n'.format(data['peak_coord_x'], data['peak_coord_y']))
    param_guide.plot_peak(data['peak_coord_x'], data['peak_coord_y'])
    lag = int(pymini.widgets['detector_points_baseline'].get())
    try:
        param_guide.msg_label.insert(
            'Estimated start of event is: {:.3f}, {:.3f}\n'.format(data['start_coord_x'], data['start_coord_y']))
    except:
        param_guide.msg_label.insert('Start of the event was not found. Try adjusting the number of data points used to calculate baseline.\n')

    # param_guide.plot_trace(data['baseline_plot'][0], np.array(data['baseline_plot'][1]) * direction)
    # param_guide.plot_trace(data['baseline_end_plot'][0], np.array(data['baseline_end_plot'][1]) * direction)
    try:
        try:
            param_guide.plot_trace(xs[max(data['start_idx'] - lag, 0):min(data['end_idx'] + lag, len(xs))],
                                   ys[max(data['start_idx'] - lag, 0):min(data['end_idx'] + lag, len(xs))])
        except:
            param_guide.plot_trace(xs[max(data['start_idx'] - lag, 0):min(data['peak_idx'] + lag, len(xs))],
                                   ys[max(data['start_idx'] - lag, 0):min(data['peak_idx'] + lag, len(xs))])
        try:
            param_guide.plot_ruler((xs[max(data['start_idx'] - lag, 0)], data['baseline']),
                                   (xs[min(data['end_idx'] + lag, len(xs))], data['baseline']))
        except:
            param_guide.msg_label.insert('baseline ruler could not be plotted\n')
        param_guide.plot_start(data['start_coord_x'], data['start_coord_y'])
        param_guide.msg_label.insert('Estimated amplitude is: {:.3f}{}\n'.format(data['amp'], data['amp_unit']))
        param_guide.plot_ruler((data['peak_coord_x'], data['peak_coord_y']), (data['peak_coord_x'], data['baseline']))
    except:
        pass
    try:
        param_guide.msg_label.insert(
        'Estimated end of event is: {:.3f}, {:.3f}\n'.format(data['end_coord_x'], data['end_coord_y']))
    except:
        pass
    try:
        param_guide.msg_label.insert('Estimated rise is: {:.3f}{}\n'.format(data['rise_const'], data['rise_unit']))
    except:
        param_guide.msg_label.insert('rise could not be calculated')
    try:
        param_guide.msg_label.insert(
            'Estimated halfwidth is {:.3f}{}\n'.format(data['halfwidth'], data['halfwidth_unit']))
        param_guide.plot_ruler((xs[data['halfwidth_idx'][0]], data['baseline'] + data['amp'] / 2),
                               (xs[data['halfwidth_idx'][1]], data['baseline'] + data['amp'] / 2))
    except:
        param_guide.msg_label.insert('halfwidth could not be calculated')
    try:
        max_points_decay = int(pymini.widgets['detector_max_points_decay'].get())
        x_data = (xs[data['peak_idx']:min(data['peak_idx'] + max_points_decay, len(xs))] - xs[data['peak_idx']]) * 1000
        y_decay = getattr(analyzer, data['decay_func'])(x_data,*data['decay_fit'])


        x_data = x_data / 1000 + xs[data['peak_idx']]
        y_decay = y_decay * direction + data['baseline']

        param_guide.plot_decay_fit(x_data, y_decay)
        param_guide.plot_decay(data['decay_coord_x'], data['decay_coord_y'])

        param_guide.msg_label.insert(
            'Estimated decay constant is {:.3f}{}\n'.format(data['decay_const'], data['decay_unit']))
        param_guide.msg_label.insert('Decay was fitted using {}'.format(data['decay_func']))
    except:
        pass
    try:
        pass
    except Exception as e:
        print(e)
        pass
    pass
