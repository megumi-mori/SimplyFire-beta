# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog, messagebox
from DataVisualizer import data_display, log_display, trace_display, param_guide
import os
from Layout import detector_tab, graph_panel
import matplotlib as mpl
from Backend import analyzer
import gc
import pandas as pd
import numpy as np

from utils import recording

### this module connects the analyzer and the gui

df = pd.DataFrame(columns = [
    # panel -- make sure this matches with the config2header dict
    # = analyzer generates the data
    't',  #
    'amp',  #
    'amp_unit',  #
    'decay_const', #
    'decay_unit', #
    'decay_func', #
    'rise_const',  #
    'rise_unit',  #
    'halfwidth', #
    'halfwidth_unit', #
    'baseline',  #
    'baseline_unit',  #
            #'auc',
    't_start',  #
    't_end',  #
    'channel',  #
    # plot
    'peak_idx', #
    'peak_coord_x',  # (x,y) #
    'peak_coord_y',  #
    'decay_coord_x',
    'decay_coord_y',
    'start_coord_x',  #
    'start_coord_y',  #
    'start_idx',  #
    'end_coord_x',  #
    'end_coord_y',  #
    'end_idx',  #
    'decay_fit', #

    # data

    'datetime'  #
])






def open_trace(fname):
    # trace stored in analyzer
    try:
        analyzer.open_trace(fname)
    except:
        messagebox.showerror('Read file error', 'The selected file could not be opened.')
        return None
    try:
        log_display.open_update(fname)
        global df
        df = df.iloc[0:0]
    except:
        return None

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

    graph_panel.y_scrollbar.config(state='normal')
    graph_panel.x_scrollbar.config(state='normal')

    trace_display.update_x_scrollbar()
    trace_display.update_y_scrollbar()

    pymini.widgets['channel_option'].clear_options()

    for i in range(analyzer.trace.channel_count):
        pymini.widgets['channel_option'].add_option(
            label='{}: {}'.format(i+1, analyzer.trace.channel_labels[i]),
            command=lambda c=i:_change_channel(c)
        )
    # starting channel was set earlier in the code
    pymini.widgets['channel_option'].set('{}: {}'.format(analyzer.trace.channel + 1, analyzer.trace.y_label))

    trace_display.canvas.draw()

def save_events(filename):
    try:
        df.to_csv(filename)
        pymini.event_filename = filename

    except:
        messagebox.showerror('Write error', 'Could not write data to selected filename.')

def open_events(filename):
    try:
        global df
        df = pd.read_csv(filename, index_col=0)
        pymini.event_filename = filename
        print(df)
        data_display.clear()
        xs = df.index.where(df['channel'] == analyzer.trace.channel)
        xs = xs.dropna()
        for x in xs:
            data_display.add(df.loc[x].to_dict())

        update_event_marker()
    except:
        messagebox.showerror('Read error', 'Could not read data.')

def export_events(filename):
    #need to think about what columns to export and if/how the user interacts with that decision
    pass

# was thinking about export/import protocol, but I already have a system to store config files.
# def export_protocol(filename):
#     #write out the dictionary as JSON, and have a way to read it
#     pass
#
# def open_protocol(filename):
#     #read a JSON file to set parameters
#     pass

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

    data_display.clear()


    xs = df.index.where(df['channel'] == analyzer.trace.channel)
    xs = xs.dropna()
    for x in xs:
        data_display.add(df.loc[x].to_dict())
    update_event_marker()


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
    direction = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
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

    #convert % x-axis to points search using sampling rate?
    r = int((xlim[1]-xlim[0]) * float(pymini.widgets['detector_search_radius'].get()) / 100 * analyzer.trace.sampling_rate)
    print('radius: {}'.format(r))


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
            direction=direction,
            lag=int(pymini.widgets['detector_points_baseline'].get()),
            # points_search=int(pymini.widgets['detector_points_search'].get()),
            points_search = r,
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
            decay_fit_ftol=float(pymini.widgets['detector_decay_fit_ftol'].get())
        )
        data['channel'] = analyzer.trace.channel

    if detector_tab.changed:
        log_display.search_update('Manual')
        # log_display.param_update(dict([(i, pymini.widgets[i].get()) for i in pymini.widgets.keys() if 'detector_' in i]))
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False
    # try:
    if data['success']:
        global df
        df = df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
        data_display.add(data)
        update_event_marker()
            # if pymini.widgets['show_end'].get():
            #     trace_display.plot_end(get_column('end_coord_x'), get_column('end_coord_y'))
        try:
            if pymini.widgets['window_param_guide'].get() == '1':
                report_to_param_guide(xs, ys, data)
        except:
            pass
    # except:
    #     print('error!!!!')
        # param_guide.clear()
        # param_guide.msg_label.insert('Event at t={} {} was already detected. Please select the event marker to view details.\n'.format(data['t'], data['t_unit']))
        pass # the event was already in the list

    pass

def select_single(iid):
    data = df.loc[float(iid)]
    if pymini.widgets['window_param_guide'].get() == '1':
        try:
            report_to_param_guide(trace_display.ax.lines[0].get_xdata(), trace_display.ax.lines[0].get_ydata(), data)
        except:
            pass



def report_to_param_guide(xs, ys, data):
    param_guide.clear()
    direction = data['direction']
    param_guide.msg_label.insert('{}\n'.format(data['msg']))
    lag = int(data['lag'])
    max_points_decay = int(data['max_points_decay'])
    try:
        param_guide.msg_label.insert(
            'Candidate peak: {:.3f},{:.3f}\n'.format(data['peak_coord_x'], data['peak_coord_y']))
        param_guide.plot_peak(data['peak_coord_x'], data['peak_coord_y'])
    except:
        param_guide.msg_label.insert('Peak not found.\n')
        print('peak plot error')
    try:
        try:
            param_guide.plot_trace(xs[max(data['start_idx'] - lag, 0):min(data['end_idx'] + max_points_decay, len(xs))],
                                   ys[max(data['start_idx'] - lag, 0):min(data['end_idx'] + max_points_decay, len(xs))])
        except:
            param_guide.plot_trace(xs[max(data['start_idx'] - lag, 0):min(data['peak_idx'] + lag, len(xs))],
                                   ys[max(data['start_idx'] - lag, 0):min(data['peak_idx'] + lag, len(xs))])

    except:
        param_guide.plot_trace(xs[max(data['peak_idx'] - lag, 0):min(data['peak_idx'] + max_points_decay, len(xs))],
                               ys[max(data['peak_idx'] - lag, 0):min(data['peak_idx'] + max_points_decay, len(xs))])

    try:
        param_guide.plot_start(data['start_coord_x'], data['start_coord_y'])
        param_guide.plot_ruler((data['peak_coord_x'], data['peak_coord_y']), (data['peak_coord_x'], data['baseline']))
        param_guide.plot_ruler((xs[max(data['start_idx'] - lag, 0)], data['baseline']),
                               (xs[min(data['end_idx'] + lag, len(xs))], data['baseline']))
    except:
        param_guide.msg_label.insert(
            'Baseline was not found. Try adjusting the maximum number of data points considered for baseline, and number of data points used to calculate baseline.\n')
        return
    try:
        param_guide.msg_label.insert('Estimated amplitude : {:.3f}{}\n'.format(data['amp'], data['amp_unit']))
    except:
        param_guide.msg_label.insert('Amplitude could not be calculated.\n')
    try:
        param_guide.msg_label.insert(
            'Estimated start of event : {:.3f}, {:.3f}\n'.format(data['start_coord_x'], data['start_coord_y']))
    except:
        param_guide.msg_label.insert('Start of the event was not found. Try adjusting the number of data points used to calculate baseline.\n')

    # param_guide.plot_trace(data['baseline_plot'][0], np.array(data['baseline_plot'][1]) * direction)
    # param_guide.plot_trace(data['baseline_end_plot'][0], np.array(data['baseline_end_plot'][1]) * direction)

    try:
        param_guide.msg_label.insert(
        'Estimated end of event : {:.3f}, {:.3f}\n'.format(data['end_coord_x'], data['end_coord_y']))
    except:
        pass
    try:
        param_guide.msg_label.insert('Estimated rise: {:.3f}{}\n'.format(data['rise_const'], data['rise_unit']))
    except:
        param_guide.msg_label.insert('Rise could not be calculated.\n')
    try:
        param_guide.msg_label.insert(
            'Estimated halfwidth : {:.3f}{}\n'.format(data['halfwidth'], data['halfwidth_unit']))
        param_guide.plot_ruler((xs[data['halfwidth_idx'][0]], data['baseline'] + data['amp'] / 2),
                               (xs[data['halfwidth_idx'][1]], data['baseline'] + data['amp'] / 2))
    except:
        param_guide.msg_label.insert('Halfwidth could not be calculated\n')
    try:
        max_points_decay = int(pymini.widgets['detector_max_points_decay'].get())
        x_data = (xs[data['peak_idx']:min(data['peak_idx'] + max_points_decay, len(xs))] - xs[data['peak_idx']]) * 1000
        y_decay = getattr(analyzer, data['decay_func'])(x_data, *data['decay_fit'])


        x_data = x_data / 1000 + xs[data['peak_idx']]
        y_decay = y_decay * direction + data['baseline']

        param_guide.plot_decay_fit(x_data, y_decay)
        param_guide.plot_decay(data['decay_coord_x'], data['decay_coord_y'])

        param_guide.msg_label.insert(
            'Estimated decay constant : {:.3f}{}\n'.format(data['decay_const'], data['decay_unit']))
        param_guide.msg_label.insert('Decay was fitted using {}'.format(data['decay_func']))
    except:
        param_guide.msg_label.insert('Decay could not be calculated.\n')
    try:
        pass
    except Exception as e:
        print(e)
        pass
    pass

def get_column(colname, index = None):
    if index:
        try:
            return list(df.loc[index][colname])
        except:
            return df.loc[index][colname]
    else:
        xs = df.index.where(df['channel'] == analyzer.trace.channel)
        xs = xs.dropna()
        return list(df.loc[xs][colname])


def toggle_marker_display(type):
    if pymini.widgets[type].get():
        getattr(trace_display, 'plot_{}'.format(type[5:]))(get_column("{}_coord_x".format(type[5:])),
                                                           get_column('{}_coord_y'.format(type[5:])))
    else:
        trace_display.clear_markers(type[5:])

def highlight_selected(selection):
    if len(selection)>0:
        selection = [float(i) for i in selection]
        trace_display.plot_highlight(get_column('peak_coord_x', selection), get_column('peak_coord_y', selection))
        # focus display on the selected events:
        if len(selection) == 1:
            trace_display.center_plot_on(get_column('peak_coord_x', selection[0]), get_column('peak_coord_y', selection[0]))
        else:
            xs = get_column('peak_coord_x', selection)
            ys = get_column('peak_coord_y', selection)
            trace_display.center_plot_area(min(xs), max(xs), min(ys), max(ys))
    else:
        trace_display.clear_markers('highlight')

def update_event_marker():
    if pymini.widgets['show_peak'].get():
        trace_display.plot_peak(get_column('peak_coord_x'), get_column('peak_coord_y'))
    if pymini.widgets['show_start'].get():
        trace_display.plot_start(get_column('start_coord_x'), get_column('start_coord_y'))
    if pymini.widgets['show_decay'].get():
        trace_display.plot_decay(get_column('decay_coord_x'), get_column('decay_coord_y'))

def delete_event(selection):
    if len(selection)>0:
        selection=[float(i) for i in selection]
        df.drop(selection, axis=0, inplace=True)
        update_event_marker()