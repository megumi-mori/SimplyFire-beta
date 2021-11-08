# takes input from the Data Visualizers and takes appropriate action
import app
from tkinter import filedialog, messagebox
import tkinter as Tk
from DataVisualizer import data_display, log_display, trace_display, param_guide, results_display
import os
import pkg_resources
from Layout import detector_tab, graph_panel, sweep_tab, adjust_tab, menubar
import matplotlib as mpl
from Backend import interpreter, analyzer2
import gc
import pandas as pd
import numpy as np
from config import config

from time import time
# This module is the workhorse of the GUI
# All functions that connect inputs from the user to processes in the background should pass through here
# Any functions that require communications between different modules should be done here

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

global al
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

    # disable the undo command in the menubar
    menubar.disable_undo()

def add_undo(task):
    # enable the undo command in the menubar
    menubar.enable_undo()
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

    # if the stack is empty, disable the undo command in the menubar
    if len(undo_stack) == 0:
        menubar.disable_undo()


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
    app.widgets['channel_option'].set('{}: {}'.format(al.recording.channel, al.recording.y_label)) #0 indexing for channel num
    if app.widgets['trace_mode'].get() == 'continuous':
        plot_continuous(fix_x=True, draw=False)
    else:
        plot_overlay(fix_x=True, draw=False)
        for i, var in enumerate(sweep_tab.sweep_vars):
            if not var.get():
                trace_display.hide_sweep(i)
    trace_display.canvas.draw()
    data_display.clear()

    if len(al.mini_df.index) > 0:
        xs = al.mini_df.index.where(al.mini_df['channel'] == al.recording.channel)
        xs = xs.dropna()
        data_display.set(al.mini_df.loc[xs])
        update_event_marker()


def plot_continuous(fix_axis=False, draw=True, fix_x=False, fix_y=False):
    if not al.recording:
        return None # no recording open
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
# Handling GUI placements
######################################

global trace_mode
trace_mode = 'continuous'

def config_cp_tab(tab_name, **kwargs):
    """
    use this function to display a hidden tab in the control panel

    Args:
        tab_name: str tab name must be one of the keys in app.cp_tab_details

    Returns:
        None
    """
    # check if current tab would be replaced by the new tab being displayed
    try:
        if kwargs['state'] == 'normal':
            idx = app.cp_notebook.index('current')
            if idx in [app.cp_tab_details[tab]['index'] for tab in app.cp_tab_details[tab_name]['partner']]:
                idx = app.cp_tab_details[tab_name]['index']
            for partner in app.cp_tab_details[tab_name]['partner']:
                app.cp_notebook.tab(app.cp_tab_details[partner]['tab'], state='hidden')
            app.cp_notebook.tab(app.cp_tab_details[tab_name]['tab'], state='normal')
            app.cp_notebook.select(idx)
            return
    except Exception as e:
        print(e)
        pass
    else:
        app.cp_notebook.tab(app.cp_tab_details[tab_name]['tab'], **kwargs)

def config_data_tab(tab_name, **kwargs):
    """
    use this function to enable a disabled tab
    """
    print('config data tab')
    try:
        if kwargs['state'] == 'normal':
            print('normal')
            for key, tab in app.data_tab_details.items():
                app.data_notebook.tab(tab['tab'], state='hidden')
            pass
    except:
        pass
    app.data_notebook.tab(app.data_tab_details[tab_name]['tab'], **kwargs)
    app.data_notebook.select(app.data_tab_details[tab_name]['index'])

    pass


######################################
# Handling mini data
######################################

def save_events(filename):
    al.mini_df.to_csv(filename, index=False)

def save_events_dialogue(e=None):
    if not app.event_filename:
        save_events_as_dialogue()
        return None
    try:
        if len(al.mini_df) > 0:
            al.mini_df.to_csv(app.event_filename, index=True)
        else:
            messagebox.showerror('Error', 'No minis to save')
    except:
        messagebox.showerror('Write error', 'Could not write data to selected filename.')
    return None


def save_events_as_dialogue(e=None):
    if len(al.mini_df) > 0:
        filename=filedialog.asksaveasfilename(filetypes=[('event files', '*.event'), ('All files', '*.*')], defaultextension='.csv')
        try:
            al.mini_df.to_csv(filename, index=True)
            app.event_filename = filename
        except:
            messagebox.showerror('Write error', 'Could not write data to selected filename.')
    else:
        messagebox.showerror('Error', 'No minis to save')
    return

def open_events(filename, log=True):
    global mini_df
    if not al.recording:
        # recording file not open yet
        messagebox.showerror('Open error', 'Please open a recording file first.')

    temp_filename = os.path.join(pkg_resources.resource_filename('PyMini', 'temp/'), 'temp_{}.temp'.format(get_temp_num()))
    save_events(temp_filename)
    add_undo([
        data_display.clear,
        lambda f=temp_filename:restore_events(f),
        lambda msg='Undo open event file':log_display.log(msg),
        update_event_marker,
    ])
    al.mini_df = pd.read_csv(filename)
    app.event_filename = filename
    data_display.clear()
    xs = al.mini_df[al.mini_df['channel'] == al.recording.channel]
    data_display.append(xs)

    update_event_marker()
    if log:
        log_display.open_update('mini data: {}'.format(filename))
    # try:

    #
    # except:
    #     messagebox.showerror('Read error', 'Could not read data.')

def restore_events():
    try:
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
    params = detector_tab.extract_mini_parameters()
    r = (xlim[1]-xlim[0])*float(params['manual_radius'])/100
    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()

    guide = False
    if app.widgets['window_param_guide'].get() == '1':
        guide = True
        param_guide.clear()

    mini = al.find_mini_manual(xlim=(max(x-r, xlim[0]), min(x+r,xlim[1])), xs=xs, ys=ys, x_sigdig=al.recording.x_sigdig,
                               sampling_rate=al.recording.sampling_rate, channel=al.recording.channel,
                               reference_df=True, y_unit=al.recording.y_unit,
                               x_unit=al.recording.x_unit, **params)
    if guide:
        report_to_param_guide(xs, ys, mini)
    if mini['success']:
        data_display.add({key: value for key,value in mini.items() if key in data_display.mini_header2config})
        update_event_marker()
        if int(app.widgets['config_undo_stack'].get()) > 0:
            add_undo([
                lambda iid=mini['t']:data_display.delete_one(iid),
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

    t0 = time()
    data_display.unselect()
    print(f'data_display.unselect(): {time()-t0}')
    t0=time()
    xs = trace_display.ax.lines[0].get_xdata()
    ys = trace_display.ax.lines[0].get_ydata()
    print(f'get xs, ys: {time()-t0}')
    t0=time()
    # temp_filename = os.path.join(pkg_resources.resource_filename('PyMini', 'temp/'), 'temp_{}.temp'.format(get_temp_num()))
    # save_events(temp_filename)
    # add_undo([
    #     lambda f=temp_filename: al.load_minis_from_file(f),
    #     restore_events,
    #     lambda msg='Undo auto mini detection in range: {} - {}'.format(xlim[0], xlim[1]): detector_tab.log(msg)
    # ])
    params = detector_tab.extract_mini_parameters()
    print(f'get params: {time()-t0}')

    df = al.find_mini_auto(xlim=xlim, xs=xs, ys=ys, x_sigdig=al.recording.x_sigdig,
                               sampling_rate=al.recording.sampling_rate, channel=al.recording.channel,
                           kernel=int(params['auto_radius']), stride=int(int(params['auto_radius'])/2),
                      reference_df=True, y_unit=al.recording.y_unit,
                               x_unit=al.recording.x_unit, progress_bar=app.pb, **params)
    update_event_marker()
    trace_display.canvas.draw()
    data_display.append(df)

    if detector_tab.changed:
        log_display.search_update('Manual')
        log_display.param_update(detector_tab.changes)
        detector_tab.changes = {}
        detector_tab.changed = False
    app.pb['value'] = 0

def select_single_mini(iid):
    data = al.mini_df[al.mini_df.t == float(iid)]
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
    if data['failure']:
        param_guide.msg_label.insert(data['failure'] + '\n')
    try:
        try:
            param_guide.plot_trace(xs[int(max(data['start_idx'] - data['lag'] - data['delta_x'], 0)):int(min(data['end_idx'] + data['max_points_decay'], len(xs)))],
                                       ys[int(max(data['start_idx'] - data['lag'] - data['delta_x'], 0)):int(min(data['end_idx'] + data['max_points_decay'], len(xs)))])
        except Exception as e:
            param_guide.plot_trace(xs[int(max(data['peak_idx'] - data['delta_x'] - data['lag'],0)):int(min(data['peak_idx']+data['lag']+data['delta_x'], len(xs)))],
                                       ys[int(max(data['peak_idx'] - data['delta_x'] - data['lag'],0)):int(min(data['peak_idx']+data['lag']+data['delta_x'], len(xs)))])
            print('exception during plot {}'.format(e))

    # except:
    #     pass
        param_guide.msg_label.insert(
            'Peak: {:.3f},{:.3f}\n'.format(data['peak_coord_x'], data['peak_coord_y']))
        param_guide.plot_peak(data['peak_coord_x'], data['peak_coord_y'])

        param_guide.plot_start(data['start_coord_x'], data['start_coord_y'])

        param_guide.plot_start(xs[data['base_idx'][0]], ys[data['base_idx'][0]])
        param_guide.plot_start(xs[data['base_idx'][1]], ys[data['base_idx'][1]])

        param_guide.plot_ruler((data['peak_coord_x'], data['peak_coord_y']), (data['peak_coord_x'], data['baseline']))
        param_guide.msg_label.insert('Baseline: {:.3f} {}\n'.format(data['baseline'], data['baseline_unit']))
        param_guide.msg_label.insert('Amplitude: {:.3f} {}\n'.format(data['amp'], data['amp_unit']))

        param_guide.ax.set_xlim((xs[int(max(data['start_idx']-data['lag'],0))], xs[int(min(data['end_idx']+data['lag'], len(xs)))]))

        param_guide.msg_label.insert('Rise: {:.3f} {}\n'.format(data['rise_const'], data['rise_unit']))

        param_guide.plot_ruler((xs[int(max(data['start_idx'] - data['lag'], 0))], data['baseline']),
                                   (xs[int(min(data['end_idx'] + data['lag'], len(xs)))], data['baseline']))


        x_data = (xs[int(data['peak_idx']):int(min(data['peak_idx'] + data['max_points_decay'], len(xs)))] - xs[int(data['peak_idx'])]) * 1000
        y_decay = analyzer2.single_exponent(x_data, data['decay_A'], data['decay_const'])

        x_data = x_data / 1000 + xs[int(data['peak_idx'])]
        y_decay = y_decay * data['direction'] + data['baseline']

        param_guide.plot_decay_fit(x_data, y_decay)

        param_guide.msg_label.insert('Decay: {:.3f} {}\n'.format(data['decay_const'], data['decay_unit']))
        param_guide.plot_decay(data['decay_coord_x'], data['decay_coord_y'])
        # param_guide.msg_label.insert('Decay was fitted using {}\n'.format(data['decay_func']))

        param_guide.plot_ruler((xs[data['halfwidth_start_idx']], data['baseline'] + data['amp'] / 2),
                                       (xs[data['halfwidth_end_idx']], data['baseline'] + data['amp'] / 2))
        param_guide.msg_label.insert(f'Halfwidth: {data["halfwidth"]} {data["halfwidth_unit"]}\n')
    except Exception as e:
        print(e)
        pass

    param_guide.canvas.draw()


def get_column(colname, t = None):
    if al.recording is None:
        return None
    if len(al.mini_df) == 0:
        return None
    if t:
        try:
            return list(al.mini_df[al.mini_df['t'].isin(t)][colname])
        except:
            print(t)
            return al.mini_df[al.mini_df.t.isin(t)][colname]
    else:
        xs = al.mini_df.index.where(al.mini_df['channel'] == al.recording.channel)
        xs = xs.dropna()
        return list(al.mini_df.loc[xs][colname])


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
            trace_display.center_plot_on(get_column('peak_coord_x', selection), get_column('peak_coord_y', selection))
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
        # al.mini_df = al.mini_df[al.mini_df.t not in selection]
        al.mini_df.drop(al.mini_df.index[al.mini_df['t'].isin(selection)], inplace=True)
        # al.mini_df.drop(selection, axis=1, inplace=True)
        update_event_marker()
    if app.widgets['window_param_guide'].get():
        param_guide.clear()


#######################################
# Sweeps
#######################################

def plot_overlay(fix_axis=False, fix_x=False, draw=False):
    if not al.recording:
        return None # no recording to plot
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
    """
    not done
    """
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
                'channel': c,  # 0 indexing
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
        target_sweeps = range(al.recording.sweep_count)
    elif target == 'All sweeps':
        target_sweeps = range(al.recording.sweep_count)
    elif target == 'Visible sweeps':
        target_sweeps = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()] #check visible sweeps
    elif target == 'Highlighted sweeps':
        target_sweeps = [i for i in trace_display.highlighted_sweep]
    if not target_sweeps:
        return None # no target to be adjusted

    app.pb['value'] = 25
    app.pb.update()

    if int(app.widgets['config_undo_stack'].get()) > 0:
        ########### Save temp file ##############
        temp_filename = os.path.join(pkg_resources.resource_filename('PyMini', 'temp/'), 'temp_{}.temp'.format(get_temp_num()))
        al.recording.save_y_data(filename=temp_filename,
                                       channels=channels,
                                       sweeps=target_sweeps)
        add_undo([
            lambda f=temp_filename, c=channels, s=target_sweeps: al.recording.load_y_data(f, c, s),
            lambda s=target_sweeps: update_plot_ys(s),
            lambda f=temp_filename: os.remove(f)
        ])
        #########################################
    app.pb['value'] = 50
    app.pb.update()

    al.filter_sweeps(filter=mode, params=params, channels=channels, sweeps=target_sweeps)
    update_plot_ys(target_sweeps)

    app.pb['value'] = 100
    app.pb.update()

    app.pb['value'] = 0
    app.pb.update()


    log('Filter trace', header=True)
    log('Sweeps: {}'.format(analyzer2.format_list_indices(target_sweeps)), False)
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