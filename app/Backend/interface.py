# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog, messagebox
import tkinter as Tk
from DataVisualizer import data_display, log_display, trace_display, param_guide
import os
from Layout import detector_tab, graph_panel, sweep_tab
import matplotlib as mpl
from Backend import analyzer, interpreter
import gc
import pandas as pd
import numpy as np

from utils import recording

### this module connects the analyzer and the gui

mini_df = pd.DataFrame(columns = [
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

def get_temp_num():
    global temp_num
    try:
        temp_num += 1
        return temp_num % int(pymini.widgets['config_undo_stack'].get())
    except:
        temp_num = 0
        return 0

def get_prev_temp_num():
    global temp_num
    try:
        return temp_num % int(pymini.widgets['config_undo_stack'].get())
    except:
        return None

global undo_stack
undo_stack = []

def clear_undo():
    global undo_stack
    for stack in undo_stack:
        del stack
    undo_stack = []

def add_undo(task):
    global undo_stack
    undo_stack.append(task)
    if len(undo_stack) > int(pymini.widgets['config_undo_stack'].get()):
        temp = undo_stack.pop(0)
        del temp
    return

def undo(e=None):
    print('undo: {}'.format(e))
    if len(undo_stack) > 0:
        task = undo_stack.pop()
        print(task.__name__)
        task()
        del task
    else:
        return




def open_trace(fname):
    # trace stored in analyzer
    try:
        analyzer.open_trace(fname)
    except Exception as e:
        messagebox.showerror('Read file error', 'The selected file could not be opened.')
        return None
    try:
        log_display.open_update(fname)
        global mini_df
        mini_df = mini_df.iloc[0:0]
    except:
        return None

    # clear undo
    clear_undo()

    # update save file directory
    if pymini.widgets['config_file_autodir'].get() == '1':
        mpl.rcParams['savefig.directory'] = os.path.split(fname)[0]

    # check if channel number is specified by user:
    if pymini.widgets['force_channel'].get() == '1':
        try:
            analyzer.trace_file.set_channel(int(pymini.widgets['force_channel_id'].get()) - 1)  # 1 indexing
        except Exception as e:
            print(analyzer.trace_file.channel)
            print('force_channel id error:{}'.format(e))
            pass

    trace_display.clear()
    data_display.clear()

    trace_display.ax.set_xlabel(analyzer.trace_file.x_label)
    trace_display.ax.set_ylabel(analyzer.trace_file.y_label)

    pymini.widgets['trace_info'].set(
        '{}: {}Hz : {} channel{}'.format(
            analyzer.trace_file.fname,
            analyzer.trace_file.sampling_rate,
            analyzer.trace_file.channel_count,
            's' if analyzer.trace_file.channel_count > 1 else ""
        )
    )
    trace_display.ax.autoscale(enable=True, axis='both', tight=True)

    sweep_tab.populate_list(analyzer.trace_file.sweep_count)

    print('after populating list: {}'.format(len(sweep_tab.panels)))

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

    for i in range(analyzer.trace_file.channel_count):
        pymini.widgets['channel_option'].add_option(
            label='{}: {}'.format(i+1, analyzer.trace_file.channel_labels[i]),
            command=lambda c=i:_change_channel(c)
        )
    # starting channel was set earlier in the code
    pymini.widgets['channel_option'].set('{}: {}'.format(analyzer.trace_file.channel + 1, analyzer.trace_file.y_label))

    # trace_display.refresh()

def save_events(filename):
    try:
        mini_df.to_csv(filename)
        pymini.event_filename = filename

    except:
        messagebox.showerror('Write error', 'Could not write data to selected filename.')

def open_events(filename):
    try:
        global mini_df
        mini_df = pd.read_csv(filename, index_col=0)
        pymini.event_filename = filename
        data_display.clear()
        xs = mini_df.index.where(mini_df['channel'] == analyzer.trace_file.channel)
        xs = xs.dropna()
        data_display.append(mini_df.loc[xs])

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
    analyzer.trace_file.set_channel(num)
    pymini.widgets['channel_option'].set('{}: {}'.format(analyzer.trace_file.channel + 1, analyzer.trace_file.y_label))
    xlim = trace_display.ax.get_xlim()
    trace_display.clear()
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.plot_trace(analyzer.trace_file.get_xs(mode='continuous'),
                              analyzer.trace_file.get_ys(mode='continuous'),
                                 draw=True,
                                 relim=True)
    else:
        for i in range(analyzer.trace_file.sweep_count):
            trace_display.plot_trace(analyzer.trace_file.get_xs(mode='overlay', sweep=i),
                                     analyzer.trace_file.get_ys(mode='overay', sweep=i),
                                     draw=False,
                                     relim=False,
                                     idx=i)
        for i, var in enumerate(sweep_tab.sweep_vars):
            if not var.get():
                trace_display.hide_sweep(i)
    trace_display.ax.set_xlim(xlim)
    trace_display.canvas.draw()

    data_display.clear()


    xs = mini_df.index.where(mini_df['channel'] == analyzer.trace_file.channel)
    xs = xs.dropna()
    # for x in xs:
    #     data_display.add(mini_df.loc[x].to_dict())
    data_display.set(mini_df.loc[xs])
    update_event_marker()


def plot_continuous(fix_axis=False):
    if fix_axis:
        xlim = trace_display.get_axis_limits('x')
        ylim = trace_display.get_axis_limits('y')
    trace_display.clear()
    trace_display.plot_trace(analyzer.trace_file.get_xs(mode='continuous'),
                             analyzer.trace_file.get_ys(mode='continuous'),
                             draw=True,
                             relim=True)
    if fix_axis:
        trace_display.set_axis_limit('x', xlim)
        trace_display.set_axis_limit('y', ylim)

    xs = mini_df.index.where(mini_df['channel'] == analyzer.trace_file.channel)
    xs = xs.dropna()
    data_display.append(mini_df.loc[xs])

    update_event_marker()

def configure(key, value):
    globals()[key] = value


def search_event_from_click(x):
    pass


def accept_data(data, update=True):
    global mini_df
    mini_df = mini_df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
    data_display.add(data)
    if update:
        update_event_marker()

#######################################
# Mini Analysis
#######################################

def pick_event_manual(x):
    try:
        param_guide.accept_button.config(state='disabled')
        param_guide.reanalyze_button.config(state='disabled')
        param_guide.reject_button.config(state='disabled')
        param_guide.goto_button.config(state='disabled')
    except:
        pass
    data_display.unselect()

    xlim=trace_display.ax.get_xlim()
    xlim = (min(xlim), max(xlim))
    ylim=trace_display.ax.get_ylim()
    ylim = (min(ylim), max(ylim))

    #convert % x-axis to points search using sampling rate?
    r = int((xlim[1]-xlim[0]) * float(pymini.widgets['detector_search_radius'].get()) / 100 * analyzer.trace_file.sampling_rate)
    global mini_df
    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()

    guide = False
    if pymini.widgets['window_param_guide'].get() == '1':
        guide = True
        param_guide.clear()

    ##### get search window ######
    start_idx, end_idx = analyzer.find_window(x, r, xs, ys, analyzer.trace_file.sampling_rate, xlim, ylim)

    direction = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
    lag = int(pymini.widgets['detector_points_baseline'].get())
    try:
        max_decay = float(pymini.widgets['detector_max_decay'].get())
    except:
        max_decay = np.inf
    try:
        max_hw = float(pymini.widgets['detector_max_hw'].get())
    except:
        max_hw = np.inf
    try:
        max_rise = float(pymini.widgets['detector_max_rise'].get())
    except:
        max_rise = np.inf


    data, success = analyzer.filter_mini(
        start_idx,
        end_idx,
        xs,
        ys,
        x_unit=analyzer.trace_file.x_unit,
        y_unit=analyzer.trace_file.y_unit,
        direction=direction,
        lag=lag,
        min_amp=float(pymini.widgets['detector_min_amp'].get()),
        min_rise=float(pymini.widgets['detector_min_rise'].get()),
        max_rise=max_rise,
        min_hw=float(pymini.widgets['detector_min_hw'].get()),
        max_hw=max_hw,
        min_decay=float(pymini.widgets['detector_min_decay'].get()),
        max_decay=max_decay,
        max_points_decay=int(pymini.widgets['detector_max_points_decay'].get()),
        df=mini_df
    )

    if guide:
        report_to_param_guide(xs, ys, data)
    if success:
        data['channel'] = analyzer.trace_file.channel
        mini_df = mini_df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
        data_display.add(data)
        update_event_marker()
    if detector_tab.changed:
        log_display.search_update('Manual')
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False


def find_mini_in_range(xlim, ylim):
    try:
        param_guide.accept_button.config(state='disabled')
        param_guide.reanalyze_button.config(state='disabled')
        param_guide.reject_button.config(state='disabled')
        param_guide.goto_button.config(state='disabled')
    except:
        pass
    pymini.pb['value'] = 0
    pymini.pb.update()

    data_display.unselect()
    lag = int(pymini.widgets['detector_points_baseline'].get())
    direction = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
    search_range = int(pymini.widgets["detector_auto_radius"].get())

    min_amp = float(pymini.widgets['detector_min_amp'].get())

    min_rise = float(pymini.widgets['detector_min_rise'].get())
    try:
        max_rise = float(pymini.widgets['detector_max_rise'].get())
    except:
        max_rise = np.inf

    min_hw = float(pymini.widgets['detector_min_hw'].get())
    try:
        max_hw = float(pymini.widgets['detector_max_hw'].get())
    except:
        max_hw = np.inf

    max_points_decay = int(pymini.widgets['detector_max_points_decay'].get())

    min_decay = float(pymini.widgets['detector_min_decay'].get())
    try:
        max_decay = float(pymini.widgets['detector_max_decay'].get())
    except:
        max_decay = np.inf
    # lag = 100
    # direction = -1
    # search_range = 60
    # min_amp = 0.3
    # min_rise = 0
    # max_rise = np.inf
    # min_hw = 0
    # max_hw = np.inf
    # max_points_decay = 500
    # min_decay = 0
    # max_decay = np.inf

    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()

    x_unit = analyzer.trace_file.x_unit
    y_unit = analyzer.trace_file.y_unit

    xlim_idx = (analyzer.search_index(xlim[0], xs), analyzer.search_index(xlim[1], xs))
    i=max(xlim_idx[0], lag)
    task_start = i
    task_length = xlim_idx[1] - i
    j = 0
    global mini_df
    while i < xlim_idx[1]:
        data, success = analyzer.filter_mini(
            start_idx=i,
            end_idx=min(i+search_range*2, xlim_idx[1]),
            xs=xs,
            ys=ys,
            x_unit=x_unit,
            y_unit=y_unit,
            direction=direction,
            lag=lag,
            min_amp=min_amp,
            min_rise=min_rise,
            max_rise=max_rise,
            min_hw=min_hw,
            max_hw=max_hw,
            min_decay=min_decay,
            max_decay=max_decay,
            max_points_decay=max_points_decay,
            df=mini_df
        )

        pymini.pb['value'] = (i - task_start)/task_length * 100
        pymini.pb.update()
        data['channel'] = analyzer.trace_file.channel
        if data['peak_idx'] is None:
            i+= search_range
        else:
            i += max(search_range, data['peak_idx'] - i)
        if success:
            try:
                mini_df = mini_df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
            except:
                pass


    update_event_marker()
    trace_display.canvas.draw()
    data_display.append(mini_df)

    if detector_tab.changed:
        log_display.search_update('Manual')
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False
    pymini.pb['value'] = 0


def select_single_mini(iid):
    data = mini_df.loc[float(iid)]
    if pymini.widgets['window_param_guide'].get() == '1':
        report_to_param_guide(trace_display.ax.lines[0].get_xdata(), trace_display.ax.lines[0].get_ydata(), data, clear=True)

def select_in_data_display(iid):
    print('selecting one: ')
    data_display.select_one(iid)
    print('selected one!')
    data_display.table.update()
    if len(data_display.selected)<1:
        print('select again')
        data_display.select_one(iid)

def reanalyze(xs, ys, data, remove_restrict=False):

    try:
        selected = data_display.table.selection()[0] == str(data['t'])
    except:
        selected = False
    try:
        data_display.delete_one(data['t'])
    except:
        pass

    try:
        param_guide.accept_button.config(state='disabled')
        param_guide.reanalyze_button.config(state='disabled')
        param_guide.reject_button.config(state='disabled')
        param_guide.goto_button.config(state='disabled')
    except:
        pass
    direction = {'negative': -1, 'positive': 1}[pymini.widgets['detector_direction'].get()]
    lag = int(pymini.widgets['detector_points_baseline'].get())
    if pymini.widgets['window_param_guide'].get():
        param_guide.clear()
    if remove_restrict:
        if pymini.widgets['window_param_guide'].get():
            param_guide.msg_label.insert('Reanalyzing without restrictions.\n')
        min_amp = 0,
        min_rise = 0,
        max_rise = np.inf,
        min_hw = 0,
        max_hw = np.inf,
        min_decay = 0,
        max_decay = np.inf,
    else:
        min_amp = float(pymini.widgets['detector_min_amp'].get())

        min_rise = float(pymini.widgets['detector_min_rise'].get())
        try:
            max_rise = float(pymini.widgets['detector_max_rise'].get())
        except:
            max_rise = np.inf

        min_hw = float(pymini.widgets['detector_min_hw'].get())
        try:
            max_hw = float(pymini.widgets['detector_max_hw'].get())
        except:
            max_hw = np.inf

        min_decay = float(pymini.widgets['detector_min_decay'].get())
        try:
            max_decay = float(pymini.widgets['detector_max_decay'].get())
        except:
            max_decay = np.inf

    global mini_df
    new_data, success = analyzer.filter_mini(
        start_idx=None,
        end_idx=None,
        xs=xs,
        ys=ys,
        peak_idx=data['peak_idx'],
        x_unit=analyzer.trace_file.x_unit,
        y_unit=analyzer.trace_file.y_unit,
        direction=direction,
        lag=lag,
        min_amp=min_amp,
        min_rise=min_rise,
        max_rise=max_rise,
        min_hw=min_hw,
        max_hw=max_hw,
        min_decay=min_decay,
        max_decay=max_decay,
        max_points_decay=int(pymini.widgets['detector_max_points_decay'].get()),
        df=mini_df
    )
    new_data['channel'] = analyzer.trace_file.channel
    new_data['search_xlim'] = data['search_xlim']
    if success:
        try:
            mini_df = mini_df.append(pd.Series(new_data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
            data_display.add(new_data)
            update_event_marker()
            data_display.table.update()
        except Exception as e:
            print('reanalyze {}'.format(e))
            pass

    if pymini.widgets['window_param_guide'].get():
        report_to_param_guide(xs, ys, new_data)

    if detector_tab.changed:
        log_display.search_update('Manual')
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False

def report_to_param_guide(xs, ys, data, clear=False):
    if clear:
        param_guide.clear()

    direction = data['direction']
    if data['peak_idx'] is None:
        param_guide.msg_label.insert('Could not find peak. Make sure the search radius is wide enough (>40 data '
                                         'points).\n')
    elif data['peak_coord_x'] is None:
        param_guide.msg_label.insert('Event already in table. Please select the event marker to see details.\n')
        data['peak_coord_x'] = xs[data['peak_idx']]
        data['peak_coord_y'] = ys[data['peak_idx']]
        param_guide.goto_button.config(state='normal')
        param_guide.goto_button.config(command=lambda iid=data['peak_coord_x']:data_display.select_one(iid))
    elif data['baseline'] is None:
        param_guide.msg_label.insert('Baseline could not be found.')
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False: reanalyze(xs, ys, data, r))
    elif data['amp'] * direction < data['baseline']:
        param_guide.msg_label.insert('Peak is within baseline.\n')
    elif data['amp'] * direction < data['min_amp']:
        param_guide.msg_label.insert('Amplitude < minimum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['base_end_idx'] is None:
        param_guide.msg_label.insert('End of event not found.\n')
    elif data['rise_const'] < data['min_rise']:
        param_guide.msg_label.insert('Rise < minimum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['rise_const'] > data['max_rise']:
        param_guide.msg_label.insert('Rise > maximum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['halfwidth'] is None:
        param_guide.msg_label.insert('Halfwidth unknown\n')
    elif data['halfwidth'] < data['min_hw']:
        param_guide.msg_label.insert('Halfwidth < minimum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['halfwidth'] > data['max_hw']:
        param_guide.msg_label.insert('Halfwidth > maximum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['decay_fit'] is None:
        param_guide.msg_label.insert('Decay fit error:\n')
        param_guide.msg_label.insert('{}\n'.format(data['decay_error']))
    elif data['decay_const'] < data['min_decay']:
        param_guide.msg_label.insert('Decay < minimum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    elif data['decay_const'] > data['max_decay']:
        param_guide.msg_label.insert('Decay > maximum\n')
        param_guide.accept_button.config(state='normal')
        param_guide.accept_button.config(command=lambda xs=xs, ys=ys, data=data, r=True:reanalyze(xs, ys, data, r))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False:reanalyze(xs, ys, data, r))
    else:
        param_guide.msg_label.insert('Success\n')
        param_guide.reject_button.config(state='normal')
        param_guide.reject_button.config(command=lambda iid=data['t']:data_display.delete_one(iid))
        param_guide.reanalyze_button.config(state='normal')
        param_guide.reanalyze_button.config(command=lambda xs=xs, ys=ys, data=data, r=False: reanalyze(xs, ys, data, r))
        param_guide.goto_button.config(state='normal')
        param_guide.goto_button.config(command=lambda iid=data['peak_coord_x']: data_display.select_one(iid))

    try:
        try:
            param_guide.plot_trace(xs[int(max(data['base_idx'] - data['lag'], 0)):int(min(data['base_end_idx'] + data['max_points_decay'], len(xs)))],
                                   ys[int(max(data['base_idx'] - data['lag'], 0)):int(min(data['base_end_idx'] + data['max_points_decay'], len(xs)))])
        except Exception as e:
            param_guide.plot_trace(xs[int(max(data['search_xlim'][0] - data['lag'],0)):int(min(data['search_xlim'][1]+data['lag'], len(xs)))],
                                   ys[int(max(data['search_xlim'][0] - data['lag'],0)):int(min(data['search_xlim'][1]+data['lag'], len(xs)))])
            print('exception during plot {}'.format(e))
        param_guide.msg_label.insert(
            'Peak: {:.3f},{:.3f}\n'.format(data['peak_coord_x'], data['peak_coord_y']))
        param_guide.plot_peak(data['peak_coord_x'], data['peak_coord_y'])

        param_guide.plot_start(data['start_coord_x'], data['start_coord_y'])

        param_guide.plot_ruler((data['peak_coord_x'], data['peak_coord_y']), (data['peak_coord_x'], data['baseline']))
        param_guide.msg_label.insert('Baseline: {:.3f} {}\n'.format(data['baseline'], data['baseline_unit']))
        param_guide.msg_label.insert('Amplitude: {:.3f} {}\n'.format(data['amp'], data['amp_unit']))

        param_guide.ax.set_xlim((xs[int(max(data['base_idx']-data['lag'],0))], xs[int(min(data['base_end_idx']+data['lag'], len(xs)))]))

        param_guide.msg_label.insert('Rise: {:.3f} {}\n'.format(data['rise_const'], data['rise_unit']))
        param_guide.msg_label.insert('Halfwidth: {:.3f} {}\n'.format(data['halfwidth'], data['halfwidth_unit']))

        param_guide.plot_ruler((xs[data['halfwidth_idx'][0]], data['baseline'] + data['amp'] / 2),
                                       (xs[data['halfwidth_idx'][1]], data['baseline'] + data['amp'] / 2))


        param_guide.plot_ruler((xs[int(max(data['base_idx'] - data['lag'], 0))], data['baseline']),
                                   (xs[int(min(data['base_end_idx'] + data['lag'], len(xs)))], data['baseline']))


        x_data = (xs[int(data['peak_idx']):int(min(data['peak_idx'] + data['max_points_decay'], len(xs)))] - xs[int(data['peak_idx'])]) * 1000
        y_decay = getattr(analyzer, data['decay_func'])(x_data, *data['decay_fit'])

        x_data = x_data / 1000 + xs[int(data['peak_idx'])]
        y_decay = y_decay * data['direction']

        param_guide.plot_decay_fit(x_data, y_decay)

        param_guide.msg_label.insert('Decay: {:.3f} {}\n'.format(data['decay_const'], data['decay_unit']))
        param_guide.plot_decay(data['decay_coord_x'], data['decay_coord_y'])
        param_guide.msg_label.insert('Decay was fitted using {}\n'.format(data['decay_func']))
    except:
        pass

    param_guide.canvas.draw()


def get_column(colname, index = None):
    if analyzer.trace_file is None:
        return None
    if index:
        try:
            return list(mini_df.loc[index][colname])
        except:
            return mini_df.loc[index][colname]
    else:
        xs = mini_df.index.where(mini_df['channel'] == analyzer.trace_file.channel)
        xs = xs.dropna()
        return list(mini_df.loc[xs][colname])


def toggle_marker_display(type):
    if pymini.widgets[type].get():
        getattr(trace_display, 'plot_{}'.format(type[5:]))(get_column("{}_coord_x".format(type[5:])),
                                                           get_column('{}_coord_y'.format(type[5:])))
        trace_display.canvas.draw()
    else:
        trace_display.clear_markers(type[5:])

def highlight_selected_mini(selection):
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
    trace_display.canvas.draw()

def highlight_events_in_range(xlim=None, ylim=None):
    # called when right click drag on plot surrounding peak event markers
    if xlim and xlim[0] > xlim[1]:
        xlim = (xlim[1], xlim[0])
    if ylim and ylim[0] > ylim[1]:
        ylim = (ylim[1], ylim[0])
    if len(mini_df.index) == 0:
        return None
    xs = mini_df
    if xlim:
        xs = xs.loc[mini_df.index > xlim[0]]
        xs = xs.loc[xs.index < xlim[1]]
    if ylim:
        xs = xs.loc[xs['peak_coord_y'] > ylim[0]]
        xs = xs.loc[xs['peak_coord_y'] < ylim[1]]
    data_display.table.selection_set([str(x) for x in xs.index])



    pass
def update_event_marker():
    if analyzer.trace_file is None:
        return None
    if pymini.widgets['show_peak'].get():
        trace_display.plot_peak(get_column('peak_coord_x'), get_column('peak_coord_y'))
    if pymini.widgets['show_start'].get():
        trace_display.plot_start(get_column('start_coord_x'), get_column('start_coord_y'))
    if pymini.widgets['show_decay'].get():
        trace_display.plot_decay(get_column('decay_coord_x'), get_column('decay_coord_y'))
    trace_display.canvas.draw()

def delete_event(selection):
    if len(selection)>0:
        selection=[float(i) for i in selection]
        mini_df.drop(selection, axis=0, inplace=True)
        update_event_marker()
    if pymini.widgets['window_param_guide'].get():
        param_guide.clear()


#######################################
# Sweeps
#######################################

def plot_overlay(fix_axis=False):
    if fix_axis:
        xlim = trace_display.get_axis_limits('x')
        ylim = trace_display.get_axis_limits('y')
    trace_display.clear()
    data_display.clear()
    for i in range(analyzer.trace_file.sweep_count):
        trace_display.plot_trace(analyzer.trace_file.get_xs(mode='overlay', sweep=i),
                                 analyzer.trace_file.get_ys(mode='overlay', sweep=i),
                                 draw=False,
                                 relim=False,
                                 idx=i)
    trace_display.show_all_plot(update_default=True)
    for i, var in enumerate(sweep_tab.sweep_vars):
        if var.get():
            trace_display.show_sweep(i)
        else:
            trace_display.hide_sweep(i)
    if fix_axis:
        trace_display.set_axis_limit('x', xlim)
        trace_display.set_axis_limit('y', ylim)
    trace_display.canvas.draw()

def toggle_sweep(idx, v, draw=True):
    if v == 1:
        # trace_display.plot_trace(analyzer.trace_file.get_xs(mode='overlay', sweep=idx),
        #                          analyzer.trace_file.get_ys(mode='overlay', sweep=idx),
        #                          draw=draw,
        #                          relim=False,
        #                          idx=idx)
        trace_display.show_sweep(idx, draw)
    else:
        trace_display.hide_sweep(idx, draw)

def select_trace_from_plot(x, y):
    #called by trace_display during mouse click near trace
    min_d = np.inf
    pick = None
    offset = int(pymini.widgets['sweep_picker_offset'].get())
    xlim = trace_display.ax.get_xlim()
    radius = int(abs(xlim[1] - xlim[0]) * offset/100 * analyzer.trace_file.sampling_rate)
    ylim = trace_display.ax.get_ylim()
    x2y = (xlim[1] - xlim[0])/(ylim[1] - ylim[0])
    for i, var in enumerate(sweep_tab.sweep_vars):
        if var.get():
            line = trace_display.get_sweep(i)
            d, idx = analyzer.point_line_min_distance(x, y, offset=radius, xs=line.get_xdata(), ys=line.get_ydata(),
                                             x2y=x2y, rate=analyzer.trace_file.sampling_rate)
            if d < min_d:
                min_d = d
                pick = i
    if pick is None:
        return None
    trace_display.toggle_sweep_highlight(pick, not interpreter.multi_select, draw=True)

def hide_highlighted_sweep():
    for idx in trace_display.highlighted_sweep:
        sweep_tab.sweep_vars[idx].set(0)
        toggle_sweep(idx, 0, draw=False)
    trace_display.canvas.draw()

def highlight_all_sweeps():
    for i in range(len(sweep_tab.sweep_vars)):
        if sweep_tab.sweep_vars[i].get():
            trace_display.set_highlight_sweep(i, highlight=True, draw=False)
    trace_display.canvas.draw()
    return

def unhighlight_all_sweeps(draw=True):
    for i in range(len(sweep_tab.sweep_vars)):
        if sweep_tab.sweep_vars[i].get():
            trace_display.set_highlight_sweep(i, highlight=False, draw=False)
    if draw:
        trace_display.canvas.draw()
    return

def highlight_sweep_in_range(xlim=None, ylim=None, draw=True):
    # called when right click drag on plot
    unhighlight_all_sweeps(draw=True)
    print(trace_display.highlighted_sweep)
    if xlim and xlim[0] > xlim[1]:
        xlim = (xlim[1], xlim[0])
    if ylim and ylim[0] > ylim[1]:
        ylim = (ylim[1], ylim[0])

    # for sweep in trace_display.sweeps:
    #     if analyzer.contains_line(xlim, ylim, trace_display.sweeps[sweep].get_xdata(),
    #                               trace_display.sweeps[sweep].get_ydata(), rate=analyzer.trace_file.sampling_rate):
    #         trace_display.set_highlight_sweep(int(sweep.split('_')[-1]), highlight=True, draw=False)
    for i, s in get_sweep_in_range(xlim, ylim):
        trace_display.set_highlight_sweep(int(i), highlight=True, draw=False)
    if draw:
        trace_display.canvas.draw()


def get_sweep_in_range(xlim=None, ylim=None):
    ls = []
    for i, sweep in enumerate(trace_display.sweeps):
        if analyzer.contains_line(xlim, ylim, trace_display.sweeps[sweep].get_xdata(),
                                  trace_display.sweeps[sweep].get_ydata(), rate=analyzer.trace_file.sampling_rate):
            ls.append((i, sweep))
    return ls


def delete_hidden(delete):
    if len(delete) == analyzer.trace_file.sweep_count:
        messagebox.showerror(message='Must have at least 1 visible trace')
        return None
    if len(mini_df.index) > 0:
        selection = messagebox.askokcancel(message='You have more than 1 mini data. Deleting sweeps may cause the events to misalign.\n'+
                               'Continue?', icon=messagebox.WARNING)
        if not selection:
            return None
    count = 0
    for idx in delete:
        analyzer.trace_file.delete_sweep(idx - count)
        count += 1

    sweep_tab.populate_list(analyzer.trace_file.sweep_count)
    # should only be called during 'overlay' mode
    plot_overlay(fix_axis=True)



######################################
# Save Trace
######################################
def save_trace_as(fname):
    c = analyzer.trace_file.channel
    for i in range(analyzer.trace_file.sweep_count):
        try:
            ys = trace_display.get_sweep(i).get_ydata()
            analyzer.trace_file.update_datea(channel=c, sweep=i, data=ys)
        except:
            pass



