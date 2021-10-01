# takes input from the Data Visualizers and takes appropriate action
import app
from tkinter import filedialog, messagebox
import tkinter as Tk
from DataVisualizer import data_display, log_display, trace_display, param_guide, results_display
import os
from Layout import detector_tab, graph_panel, sweep_tab, adjust_tab
import matplotlib as mpl
from Backend import interpreter, analyzer2
import gc
import pandas as pd
import numpy as np
from config import config

import time

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

al = analyzer2.Analyzer()
def get_temp_num():
    global temp_num
    try:
        temp_num += 1
        return temp_num % int(app.widgets['config_undo_stack'].get())
    except:
        temp_num = 0
        return 0

def get_prev_temp_num():
    global temp_num
    try:
        return temp_num % int(app.widgets['config_undo_stack'].get())
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
    if isinstance(task, list):
        undo_stack.append(task)
    else:
        undo_stack.append([task])
    try:
        if len(undo_stack) > int(app.widgets['config_undo_stack'].get()):
            temp = undo_stack.pop(0)
            del temp
    except:
        pass
    print(undo_stack)
    return

def undo(e=None):
    print('undo')
    app.pb['value'] = 0
    app.pb.update()
    if len(undo_stack) > 0:
        task_stack = undo_stack.pop()
        len_task = len(task_stack)
        for i, task in enumerate(task_stack):
            app.pb['value'] = i / len_task * 100
            app.pb.update()
            task()
            del task

        del task_stack
        print(undo_stack)
    app.pb['value'] = 0
    app.pb.update()


def configure(key, value):
    globals()[key] = value

#################################
# Handling recording data
#################################

def open_trace(fname):
    # trace stored in analyzer
    print('open_trace')
    try:
        # al.open_trace(fname)
        al.open_file(fname)
    except Exception as e:
        print(e)
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
    if app.widgets['config_file_autodir'].get() == '1':
        mpl.rcParams['savefig.directory'] = os.path.split(fname)[0]

    # check if channel number is specified by user:
    if app.widgets['force_channel'].get() == '1':
        try:
            al.recording.set_channel(int(app.widgets['force_channel_id'].get()))  # 0 indexing
        except Exception as e:
            print(al.recording.channel)
            print('force_channel id error:{}'.format(e))
            al.recording.set_channel(0) # force to open the first channel
            pass
    else:
        al.recording.set_channel(0)

    trace_display.clear()
    data_display.clear()

    trace_display.ax.set_xlabel(al.recording.x_label)
    trace_display.ax.set_ylabel(al.recording.y_label)

    app.widgets['trace_info'].set(
        '{}: {}Hz : {} channel{}'.format(
            al.recording.filename,
            al.recording.sampling_rate,
            al.recording.channel_count,
            's' if al.recording.channel_count > 1 else ""
        )
    )
    trace_display.ax.autoscale(enable=True, axis='both', tight=True)

    sweep_tab.populate_list(al.recording.sweep_count)

    print('after populating list: {}'.format(len(sweep_tab.panels)))

    if app.widgets['trace_mode'].get() == 'continuous':
        plot_continuous()
    else:
        plot_overlay()

    param_guide.update()

    if app.widgets['force_axis_limit'].get() == '1':
        trace_display.set_axis_limit('x', (app.widgets['min_x'].get(), app.widgets['max_x'].get()))
        trace_display.set_axis_limit('y', (app.widgets['min_y'].get(), app.widgets['max_y'].get()))

    graph_panel.y_scrollbar.config(state='normal')
    graph_panel.x_scrollbar.config(state='normal')

    trace_display.update_x_scrollbar()
    trace_display.update_y_scrollbar()

    app.widgets['channel_option'].clear_options()

    for i in range(al.recording.channel_count):
        app.widgets['channel_option'].add_command(
            label='{}: {}'.format(i, al.recording.channel_labels[i]),
            command=lambda c=i:_change_channel(c)
        )
    # starting channel was set earlier in the code
    app.widgets['channel_option'].set('{}: {}'.format(al.recording.channel, al.recording.y_label))

    # trace_display.refresh()
def _change_channel(num, save_undo=True):
    log_display.log('@ graph_viewer: switch to channel {}'.format(num))
    if save_undo and num != al.recording.channel:
        add_undo(lambda n=al.recording.channel, s=False:_change_channel(n, s))

    al.recording.set_channel(num)
    app.widgets['channel_option'].set('{}: {}'.format(al.recording.channel + 1, al.recording.y_label))
    if app.widgets['trace_mode'].get() == 'continuous':
        plot_continuous(fix_x=True, draw=False)
    else:
        plot_overlay(fix_x=True, draw=False)
        for i, var in enumerate(sweep_tab.sweep_vars):
            if not var.get():
                trace_display.hide_sweep(i)
    trace_display.canvas.draw()

    data_display.clear()


    xs = mini_df.index.where(mini_df['channel'] == al.recording.channel)
    xs = xs.dropna()
    # for x in xs:
    #     data_display.add(mini_df.loc[x].to_dict())
    data_display.set(mini_df.loc[xs])
    update_event_marker()


def plot_continuous(fix_axis=False, draw=True, fix_x=False, fix_y=False):
    if fix_axis:
        xlim = trace_display.get_axis_limits('x')
        ylim = trace_display.get_axis_limits('y')
    if fix_x:
        xlim = trace_display.get_axis_limits('x')
    if fix_y:
        ylim=trace_display.get_axis_limits('y')
    trace_display.clear()
    trace_display.plot_trace(al.recording.get_xs(mode='continuous'),
                             al.recording.get_ys(mode='continuous'),
                             draw=draw,
                             relim=True)
    if fix_axis:
        trace_display.set_axis_limit('x', xlim)
        trace_display.set_axis_limit('y', ylim)
    if fix_x:
        trace_display.set_axis_limit('x', xlim)
    if fix_y:
        trace_display.set_axis_limit('y', ylim)

    xs = mini_df.index.where(mini_df['channel'] == al.recording.channel)
    xs = xs.dropna()
    data_display.append(mini_df.loc[xs])

    update_event_marker()

def delete_last_sweep():
    al.recording.delete_last_sweep()
    sweep_tab.delete_last_sweep()
    trace_display.delete_last_sweep()

######################################
# Handling mini data
######################################

def save_events(filename, dataframe=None):
    if dataframe is None:
        dataframe = mini_df
        app.event_filename = filename
    try:
        dataframe.to_csv(filename)
    except:
        messagebox.showerror('Write error', 'Could not write data to selected filename.')

def open_events(filename, log=True):
    global mini_df

    temp_filename = os.path.join(config.DIR, *config.default_temp_path,
                                 'temp_{}.temp'.format(get_temp_num()))
    save_events(temp_filename)
    add_undo([
        data_display.clear,
        lambda f=temp_filename:restore_events(f),
        lambda msg='Undo open event file':log_display.log(msg),
        update_event_marker,
    ])
    try:
        mini_df = pd.read_csv(filename, index_col=0)
        app.event_filename = filename
        data_display.clear()
        xs = mini_df.index.where(mini_df['channel'] == al.recording.channel)
        xs = xs.dropna()
        data_display.append(mini_df.loc[xs])

        update_event_marker()
        if log:
            log_display.open_update('mini data: {}'.format(filename))

    except:
        messagebox.showerror('Read error', 'Could not read data.')

def restore_events(filename):
    print('restore events!! {}'.format(filename))
    try:
        global mini_df
        mini_df = pd.read_csv(filename, index_col=0)
        print(mini_df)
        app.event_filename = filename
        data_display.clear()
        xs = mini_df.index.where(mini_df['channel'] == al.recording.channel)
        xs = xs.dropna()
        data_display.append(mini_df.loc[xs])

        update_event_marker()
    except Exception as e:
        print('restore events error: {}'.format(e))
        pass

def export_events(filename):
    #need to think about what columns to export and if/how the user interacts with that decision
    pass



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
    r = int((xlim[1]-xlim[0]) * float(app.widgets['detector_search_radius'].get()) / 100 * al.recording.sampling_rate)
    global mini_df
    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()

    guide = False
    if app.widgets['window_param_guide'].get() == '1':
        guide = True
        param_guide.clear()

    ##### get search window ######
    start_idx, end_idx = al.find_window(x, r, xs, ys, al.recording.sampling_rate, xlim, ylim)

    direction = {'negative': -1, 'positive': 1}[app.widgets['detector_direction'].get()]
    lag = int(app.widgets['detector_points_baseline'].get())
    try:
        max_decay = float(app.widgets['detector_max_decay'].get())
    except:
        max_decay = np.inf
    try:
        max_hw = float(app.widgets['detector_max_hw'].get())
    except:
        max_hw = np.inf
    try:
        max_rise = float(app.widgets['detector_max_rise'].get())
    except:
        max_rise = np.inf


    data, success = al.filter_mini(
        start_idx,
        end_idx,
        xs,
        ys,
        x_unit=al.recording.x_unit,
        y_unit=al.recording.y_unit,
        direction=direction,
        lag=lag,
        min_amp=float(app.widgets['detector_min_amp'].get()),
        min_rise=float(app.widgets['detector_min_rise'].get()),
        max_rise=max_rise,
        min_hw=float(app.widgets['detector_min_hw'].get()),
        max_hw=max_hw,
        min_decay=float(app.widgets['detector_min_decay'].get()),
        max_decay=max_decay,
        max_points_decay=int(app.widgets['detector_max_points_decay'].get()),
        df=mini_df,
        x_sigdig=al.recording.sampling_rate_sigdig
    )
    if guide:
        report_to_param_guide(xs, ys, data)
    if success:
        data['channel'] = al.recording.channel
        mini_df = mini_df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)
        data_display.add({key: value for key, value in data.items() if key in data_display.mini_header2config})
        update_event_marker()
        add_undo([
            lambda iid=data['t']:data_display.delete_one(iid),
            lambda msg='Undo manual mini detection at {}'.format(x):detector_tab.log(msg)
        ])
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
    app.pb['value'] = 0
    app.pb.update()

    data_display.unselect()
    lag = int(app.widgets['detector_points_baseline'].get())
    direction = {'negative': -1, 'positive': 1}[app.widgets['detector_direction'].get()]
    search_range = int(app.widgets["detector_auto_radius"].get())

    min_amp = float(app.widgets['detector_min_amp'].get())

    min_rise = float(app.widgets['detector_min_rise'].get())
    try:
        max_rise = float(app.widgets['detector_max_rise'].get())
    except:
        max_rise = np.inf

    min_hw = float(app.widgets['detector_min_hw'].get())
    try:
        max_hw = float(app.widgets['detector_max_hw'].get())
    except:
        max_hw = np.inf

    max_points_decay = int(app.widgets['detector_max_points_decay'].get())

    min_decay = float(app.widgets['detector_min_decay'].get())
    try:
        max_decay = float(app.widgets['detector_max_decay'].get())
    except:
        max_decay = np.inf

    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()

    x_unit = al.recording.x_unit
    y_unit = al.recording.y_unit

    xlim_idx = (al.search_index(xlim[0], xs), al.search_index(xlim[1], xs))
    i=max(xlim_idx[0], lag)
    task_start = i
    task_length = xlim_idx[1] - i
    global mini_df
    temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(get_temp_num()))
    save_events(temp_filename, mini_df)
    add_undo([
        lambda f=temp_filename: restore_events(f),
        lambda msg='Undo auto mini detection in range: {} - {}'.format(xlim[0], xlim[1]): detector_tab.log(msg)
    ])

    while i < xlim_idx[1]:
        data, success = al.filter_mini(
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
            df=mini_df,
            x_sigdig=al.recording.sampling_rate_sigdig
        )

        app.pb['value'] = (i - task_start)/task_length * 100
        app.pb.update()
        data['channel'] = al.recording.channel
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
    app.pb['value'] = 0


def select_single_mini(iid):
    data = mini_df.loc[float(iid)]
    if app.widgets['window_param_guide'].get() == '1':
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
    global mini_df
    try:
        old_data = mini_df.loc[data['t']]
    except:
        old_data = None

    data_display.delete_one(data['t'])
    try:
        param_guide.accept_button.config(state='disabled')
        param_guide.reanalyze_button.config(state='disabled')
        param_guide.reject_button.config(state='disabled')
        param_guide.goto_button.config(state='disabled')
    except:
        pass
    direction = {'negative': -1, 'positive': 1}[app.widgets['detector_direction'].get()]
    lag = int(app.widgets['detector_points_baseline'].get())
    if app.widgets['window_param_guide'].get():
        param_guide.clear()
    if remove_restrict:
        if app.widgets['window_param_guide'].get():
            param_guide.msg_label.insert('Reanalyzing without restrictions.\n')
        min_amp = 0,
        min_rise = 0,
        max_rise = np.inf,
        min_hw = 0,
        max_hw = np.inf,
        min_decay = 0,
        max_decay = np.inf,
    else:
        min_amp = float(app.widgets['detector_min_amp'].get())

        min_rise = float(app.widgets['detector_min_rise'].get())
        try:
            max_rise = float(app.widgets['detector_max_rise'].get())
        except:
            max_rise = np.inf

        min_hw = float(app.widgets['detector_min_hw'].get())
        try:
            max_hw = float(app.widgets['detector_max_hw'].get())
        except:
            max_hw = np.inf

        min_decay = float(app.widgets['detector_min_decay'].get())
        try:
            max_decay = float(app.widgets['detector_max_decay'].get())
        except:
            max_decay = np.inf

    new_data, success = al.filter_mini(
        start_idx=None,
        end_idx=None,
        xs=xs,
        ys=ys,
        peak_idx=data['peak_idx'],
        x_unit=al.recording.x_unit,
        y_unit=al.recording.y_unit,
        direction=direction,
        lag=lag,
        min_amp=min_amp,
        min_rise=min_rise,
        max_rise=max_rise,
        min_hw=min_hw,
        max_hw=max_hw,
        min_decay=min_decay,
        max_decay=max_decay,
        max_points_decay=int(app.widgets['detector_max_points_decay'].get()),
        df=mini_df,
        x_sigdig=al.recording.sampling_rate_sigdig
    )
    new_data['channel'] = al.recording.channel
    new_data['search_xlim'] = data['search_xlim']
    undo = []
    if success:
        try:
            mini_df = mini_df.append(pd.Series(new_data, name=new_data['t']), ignore_index=False, verify_integrity=True,
                                     sort=True)
            data_display.add({key: value for key, value in new_data.items() if key in data_display.mini_header2config})
            update_event_marker()
            data_display.table.update()
            undo = [
                lambda t=new_data['t']:data_display.delete_one(t),
                lambda msg='Undo reanalysis of mini at {}'.format(data['t']):log_display.log(msg)
            ]
        except Exception as e:
            print('reanalyze {}'.format(e))
            pass
    if old_data is not None:
        pass
        undo.append(lambda d=old_data: add_event(d))
    undo.append(update_event_marker)
    add_undo(undo)

    if app.widgets['window_param_guide'].get():
        report_to_param_guide(xs, ys, new_data)

    if detector_tab.changed:
        log_display.search_update('Manual')
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False

def add_event(data):
    # populate this and replace with repeated calls in interpreter
    # also include add to data display after removing calls
    data_display.add({key:value for key, value in data.items() if key in data_display.mini_header2config})
    global mini_df
    mini_df = mini_df.append(pd.Series(data, name=data['t']), ignore_index=False, verify_integrity=True, sort=True)

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
        param_guide.msg_label.insert(
            'Baseline could not be found. Make sure lag is not '
            'longer than the start of recording to the start of the mini.\n')
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
    if al.recording is None:
        return None
    if index:
        try:
            return list(mini_df.loc[index][colname])
        except:
            return mini_df.loc[index][colname]
    else:
        xs = mini_df.index.where(mini_df['channel'] == al.recording.channel)
        xs = xs.dropna()
        return list(mini_df.loc[xs][colname])


def toggle_marker_display(type):
    if app.widgets[type].get():
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
    if al.recording is None:
        return None
    if app.widgets['show_peak'].get():
        trace_display.plot_peak(get_column('peak_coord_x'), get_column('peak_coord_y'))
    if app.widgets['show_start'].get():
        trace_display.plot_start(get_column('start_coord_x'), get_column('start_coord_y'))
    if app.widgets['show_decay'].get():
        trace_display.plot_decay(get_column('decay_coord_x'), get_column('decay_coord_y'))
    trace_display.canvas.draw()

def delete_event(selection):
    if len(selection)>0:
        selection=[float(i) for i in selection]
        mini_df.drop(selection, axis=0, inplace=True)
        update_event_marker()
    if app.widgets['window_param_guide'].get():
        param_guide.clear()


#######################################
# Sweeps
#######################################

def plot_overlay(fix_axis=False, fix_x=False, draw=False):
    if fix_axis:
        xlim = trace_display.get_axis_limits('x')
        ylim = trace_display.get_axis_limits('y')
    if fix_x:
        xlim = trace_display.get_axis_limits('x')
    trace_display.clear()
    data_display.clear()
    for i in range(al.recording.sweep_count):
        trace_display.plot_trace(al.recording.get_xs(mode='overlay', sweep=i),
                                 al.recording.get_ys(mode='overlay', sweep=i),
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
    if fix_x:
        trace_display.set_axis_limit('x', xlim)
    if draw:
        trace_display.canvas.draw()

def toggle_sweep(idx, v, draw=True):
    if v == 1:
        # trace_display.plot_trace(al.recording.get_xs(mode='overlay', sweep=idx),
        #                          al.recording.get_ys(mode='overlay', sweep=idx),
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
    offset = int(app.widgets['sweep_picker_offset'].get())
    xlim = trace_display.ax.get_xlim()
    radius = int(abs(xlim[1] - xlim[0]) * offset/100 * al.recording.sampling_rate)
    ylim = trace_display.ax.get_ylim()
    x2y = (xlim[1] - xlim[0])/(ylim[1] - ylim[0])
    for i, var in enumerate(sweep_tab.sweep_vars):
        if var.get():
            line = trace_display.get_sweep(i)
            d, idx = al.point_line_min_distance(x, y, offset=radius, xs=line.get_xdata(), ys=line.get_ydata(),
                                             x2y=x2y, rate=al.recording.sampling_rate)
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
    #     if al.contains_line(xlim, ylim, trace_display.sweeps[sweep].get_xdata(),
    #                               trace_display.sweeps[sweep].get_ydata(), rate=al.recording.sampling_rate):
    #         trace_display.set_highlight_sweep(int(sweep.split('_')[-1]), highlight=True, draw=False)
    for i, s in get_sweep_in_range(xlim, ylim):
        trace_display.set_highlight_sweep(int(i), highlight=True, draw=False)
    if draw:
        trace_display.canvas.draw()


def get_sweep_in_range(xlim=None, ylim=None):
    ls = []
    for i, sweep in enumerate(trace_display.sweeps):
        if al.contains_line(xlim, ylim, trace_display.sweeps[sweep].get_xdata(),
                                  trace_display.sweeps[sweep].get_ydata(), rate=al.recording.sampling_rate):
            ls.append((i, sweep))
    return ls


def delete_hidden(delete):
    if len(delete) == al.recording.sweep_count:
        messagebox.showerror(message='Must have at least 1 visible trace')
        return None
    if len(mini_df.index) > 0:
        selection = messagebox.askokcancel(message='You have more than 1 mini data. Deleting sweeps may cause the events to misalign.\n'+
                               'Continue?', icon=messagebox.WARNING)
        if not selection:
            return None
    count = 0
    for idx in delete:
        al.recording.delete_sweep(idx - count)
        count += 1

    sweep_tab.populate_list(al.recording.sweep_count)
    # should only be called during 'overlay' mode
    plot_overlay(fix_axis=True)



######################################
# Save Trace
######################################
def save_trace_as(fname):
    c = al.recording.channel
    for i in range(al.recording.sweep_count):
        try:
            ys = trace_display.get_sweep(i).get_ydata()
            al.recording.update_datea(channel=c, sweep=i, data=ys)
        except:
            pass



########################################
# Adjust tab
########################################

# update changes made to the y-data in the recording data to the plot
def update_plot_ys(sweeps):
    if app.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(al.recording.get_ys(mode='continuous'))
    else:
        for s in sweeps:
            trace_display.get_sweep(s).set_ydata(al.recording.get_ys(mode='overlay', sweep=s))
    trace_display.canvas.draw()

def adjust_baseline(all_channels=False, target='All sweeps', mode='mean', xlim=None, fixed_val=None):
    if al.recording is None:
        return None
    if all_channels:
        channels = range(al.recording.channel_count)
    else:
        channels = [al.recording.channel]

    # determine sweeps to apply adjustment
    plot_mode = app.widgets['trace_mode'].get()
    target_sweeps = None
    if plot_mode == 'continuous':
        target_sweeps = range(al.recording.sweep_count)
    elif target == 'All sweeps':
        target_sweeps = range(al.recording.sweep_count)
    elif target == 'Visible sweeps':
        target_sweeps = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()]
    elif target == 'Highlighted sweeps':
        target_sweeps = [i for i in trace_display.highlighted_sweep] # make a getter?
    if not target_sweeps:
        return None # no target to be adjusted

    # clean unwanted params
    if mode != 'range':
        xlim = None
    if mode != 'fixed':
        fixed_val = None

    # perform adjustment
    baseline = al.subtract_baseline(plot_mode=plot_mode,
                               channels=channels, sweeps=target_sweeps, xlim=xlim,
                               fixed_val=fixed_val)
    update_plot_ys(target_sweeps)

    # save undo functions
    undo_baseline = baseline*(-1)
    add_undo([
        lambda b=undo_baseline, m=plot_mode, c=channels, s=target_sweeps: al.shift_y_data(b, m, c, s),
        lambda s=target_sweeps: update_plot_ys(s)
    ])

    app.pb['value'] = 0
    app.pb.update()

    ###### Log output ######
    log('Baseline adjustment', True)
    log('Sweeps: {}'.format(analyzer2.format_list_indices(target_sweeps)), False)
    log('Channels: {}'.format(channels), False)
    ########################
    if target == 'fixed':
        log('Subtract a fixed number', False)
        for c in channels:
            log('Channel {}: {}{}'.format(c, fixed_val, al.recording.channel_units[c]), False)
    elif mode == 'mean':
        log('Subtract the mean of all sweeps', False)
        for i, c in enumerate(channels):
            log('Channel {}: {:.6f}{}'.format(c, baseline[i, 0, 0], al.recording.channel_units[c]), False)
    elif mode == 'range':
        log('Subtract the mean of range {} from each sweep'.format(xlim), False)
        mean = np.mean(baseline, axis=1, keepdims=True)
        std = np.std(baseline, axis=1, keepdims=True)
        for i,c in enumerate(channels):
            log('Channel {}: mean: {:.6f}{} stdev: {:.6f}'.format(c,
                                                          mean[i, 0, 0],
                                                          al.recording.channel_units[c],
                                                          std[i, 0, 0]),
                False)

def average_y_data(all_channels=False, target='All sweeps', report_minmax=False, limit_minmax_window=False, hide_all=False):
    if not al.recording:
        return None # no recording file open
    if all_channels:
        channels = range(al.recording.channel_count)
    else:
        channels = [al.recording.channel]
    if app.widgets['trace_mode'].get() == 'continuous':
        return None
    target_sweeps=[]

    if target == 'All sweeps':
        target_sweeps = range(al.recording.sweep_count)
    elif target == 'Visible sweeps':
        target_sweeps = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()] #check visible sweeps
    elif target == 'Highlighted sweeps':
        target_sweeps = [i for i in trace_display.highlighted_sweep]
    if not target_sweeps:
        return None # no target to be adjusted



    visible_sweep_list = None
    if hide_all:
        visible_sweep_list = tuple([i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()])
        sweep_tab.hide_all()
    if report_minmax:
        xlim = None
        if limit_minmax_window:
            xlim = trace_display.ax.get_xlim()
        mins, mins_std = al.calculate_min_sweeps(plot_mode='overlay', channels=channels, sweeps=target_sweeps, xlim=xlim)
        maxs, maxs_std = al.calculate_max_sweeps(plot_mode='overlay', channels=channels, sweeps=target_sweeps, xlim=xlim)
    ys_avg = al.append_average_sweeps(channels=channels, sweeps=target_sweeps)

    sweep_tab.populate_list(1, replace=False, prefix='Avg ')
    trace_display.plot_trace(al.recording.get_xs(mode='overlay', sweep=-1),
                             al.recording.get_ys(mode='overlay', sweep=-1),
                             draw=True,
                             relim=False,
                             idx=al.recording.sweep_count-1)

    # sweep_tab.checkbuttons[-1].invoke()

    add_undo([
        delete_last_sweep,
        lambda s=visible_sweep_list, d=False: sweep_tab.show(s, d),
        trace_display.canvas.draw,
        lambda msg='Undo trace averaging', h=True: log(msg, h)
    ])
    log('Trace Averaging', True)
    log('Sweeps {}'.format(analyzer2.format_list_indices(target_sweeps)), False)
    log('Channels: {}'.format(channels), False)
    if report_minmax:
        for i,c in enumerate(channels):
            results_display.table_frame.add({
                'filename': al.recording.filename,
                'channel': c + 1,  # 0 indexing
                'analysis': 'trace averaging',
                'min': mins[i, 0, 0],
                'min_unit': al.recording.channel_units[c],
                'min_std': mins_std[i, 0, 0],
                # 'max': maxs[i,0,0],
                # 'max_unit': al.recording.channel_units[c],
                # 'max_std': max_std[i,0,0],
            })
            log('Channel {}: min: {:.6f} {} stdev: {:.6f}'.format(c,
                                                         mins[i,0,0],
                                                         al.recording.channel_units[c],
                                                         mins_std[i,0,0]), False)
            log('           max: {:.6f} {} stdev: {:.6f}'.format(maxs[i, 0, 0],
                                                        al.recording.channel_units[c],
                                                        maxs_std[i, 0, 0]), False)


def filter_y_data(all_channels=False, target='All sweeps', mode='Boxcar', params=None):
    if all_channels:
        channels = range(al.recording.channel_count)
    else:
        channels = [al.recording.channel]
    if app.widgets['trace_mode'].get() == 'continuous':
        ys = al.recording.get_y_data(mode='continuous', channels=channels)
        target_sweeps = range(al.recording.sweep_count)
    else:
        if target == 'All sweeps':
            target_sweeps = range(al.recording.sweep_count)
        elif target == 'Visible sweeps':
            target_sweeps = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()] #check visible sweeps
        elif target == 'Highlighted sweeps':
            target_sweeps = [i for i in trace_display.highlighted_sweep]
        if not target_sweeps:
            return None # no target to be adjusted
        ys = al.recording.get_y_data(mode='overlay', channels=channels, sweeps=target_sweeps)

    app.pb['value'] = 25
    app.pb.update()

    if int(app.widgets['config_undo_stack'].get()) > 0:
        ########### Save temp file ##############
        temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(get_temp_num()))
        al.recording.save_ydata(filename=temp_filename,
                                       channels=channels,
                                       sweeps=target_sweeps)
        #########################################
    app.pb['value'] = 50
    app.pb.update()

    if mode == 'Boxcar':
        kernel = params['kernel']
        filtered_ys = al.apply_boxcar(kernel, ys)
    al.recording.set_ydata(channels, target_sweeps, filtered_ys, app.widgets['trace_mode'].get())
    update_plot_ys(target_sweeps)

    app.pb['value'] = 100
    app.pb.update()

    if int(app.widgets['config_undo_stack'].get()) > 0:
        add_undo([
            lambda f=temp_filename, c=channels, s=target_sweeps: al.recording.load_ydata(f,c,s),
            lambda s=target_sweeps: update_plot_ys(s)
        ])

    app.pb['value'] = 0
    app.pb.update()


    log('Filter trace', header=True)
    log('Sweeps: {}'.format(al.format_list_indices(target_sweeps)), False)
    log('Channels: {}'.format(channels), False)

    log('Algorithm: {}'.format(mode), False)
    log('Parameters: {}'.format(str(params)), False)



#####################
# log
#####################

def log(msg, header=False):
    if not header:
        msg = '    '+msg
    log_display.log(msg, header)
