from utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from tkinter import ttk, StringVar, messagebox
import tkinter as Tk
import pymini
from config import config
from utils import widget
from Backend import analyzer, interface
from Layout import sweep_tab
from DataVisualizer import trace_display, log_display, results_display
import numpy as np
# from scipy.signal import convolve
import os
from astropy.convolution import Box1DKernel, convolve


#### DEBUG
import tracemalloc
global name
name = 'adjust'

def load(parent):
    optionframe = ScrollableOptionFrame(parent)

    frame = optionframe.frame

    frame.insert_title(
        name='adjust_title',
        text='Adjust Trace'
    )
    frame.insert_title(
        text='General Setting',
        separator=False
    )
    pymini.widgets['adjust_target'] = frame.insert_label_optionmenu(
        name='adjust_target',
        label='Apply adjustment to:',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )
    pymini.widgets['adjust_channel'] = frame.insert_label_checkbox(
        name='adjust_channel',
        label='Apply adjustment to visible channel only',
        onvalue='1',
        offvalue="",
        separator=False
    )
    frame.insert_separator()
    frame.insert_title(
        text='Baseline Subtraction',
        separator=False
    )
    frame.insert_title(
        name='baseline_subtraction',
        text='Perform baseline subtraction using:',
        separator=False,
    )
    baseline_panel = OptionFrame(frame)
    baseline_panel.grid_columnconfigure(0, weight=1)
    frame.insert_panel(baseline_panel)
    pymini.widgets['adjust_baseline_mode'] = StringVar(baseline_panel, config.adjust_baseline_mode)
    global baseline_options
    baseline_options = {
        'mean': {
         'value': 'mean',
            'button': None
         },
        'range': {
            'value': 'range',
            'button': None
        },
        'fixed': {
            'value': 'fixed',
            'button': None
        }
    }

    global prev_baseline_mode
    prev_baseline_mode = config.adjust_baseline_mode

    baseline_options['mean']['button'] = ttk.Radiobutton(
        baseline_panel,
        text='Mean of all target sweeps',
        value='mean',
        command=_select_baseline_mode,
        variable=pymini.widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_options['mean']['button'])

    baseline_options['range']['button'] = ttk.Radiobutton(
        baseline_panel,
        text='Mean of range (x-axis) per sweep:',
        value='range',
        command=_select_baseline_mode,
        variable=pymini.widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_options['range']['button'])

    panel = Tk.Frame(baseline_panel)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_columnconfigure(1, weight=1)
    pymini.widgets['adjust_range_left'] = widget.VarEntry(
                parent=panel,
                name='adjust_range_left',
                validate_type='float'
            )
    pymini.widgets['adjust_range_left'].grid(column=0, row=0, sticky='news')

    pymini.widgets['adjust_range_right'] = widget.VarEntry(
        parent=panel,
        name='adjust_range_right',
        validate_type='float'
    )
    pymini.widgets['adjust_range_right'].grid(column=1, row=0, sticky='news')
    baseline_panel.insert_widget(panel)

    baseline_options['fixed']['button'] = ttk.Radiobutton(
        baseline_panel,
        text='Fixed value:',
        value='fixed',
        command=_select_baseline_mode,
        variable=pymini.widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_options['fixed']['button'])

    pymini.widgets['adjust_fixed'] = widget.VarEntry(
        parent=baseline_panel,
        name='adjust_fixed',
        validate_type='float'
    )
    baseline_panel.insert_widget(pymini.widgets['adjust_fixed'])

    pymini.widgets['adjust_baseline_ylim'] = frame.insert_label_checkbox(
        name='adjust_baseline_ylim',
        label='Automatically adjust window y-axis limits',
        onvalue='1',
        offvalue='',
    )

    frame.insert_button(
        text='Apply',
        command=_adjust_baseline
    )
    baseline_options[config.adjust_baseline_mode]['button'].invoke()


    frame.insert_separator()

    frame.insert_title(
        name='averaging',
        text='Trace Averaging',
        separator=False
    )
    pymini.widgets['adjust_avg_show_result'] = frame.insert_label_checkbox(
        name='adjust_avg_show_result',
        label='Only show resultant trace (hide original sweeps)',
        onvalue='1',
        offvalue="",
        separator=False
    )
    pymini.widgets['adjust_avg_min_max'] = frame.insert_label_checkbox(
        name='adjust_avg_min_max',
        label='Output min/max',
        onvalue='1',
        offvalue="",
        separator=False
    )
    pymini.widgets['adjust_avg_window'] = frame.insert_label_checkbox(
        name='adjust_avg_window',
        label='Limit min/max to within trace window',
        onvalue='1',
        offvalue='',
        separator=False
    )
    frame.insert_button(
        text='Apply',
        command=_average_trace
    )
    frame.insert_separator()
    pymini.widgets
    frame.insert_title(
        name='filtering',
        text='Trace Filtering',
        separator=False,
        justify=Tk.LEFT
    )
    pymini.widgets['adjust_filter_lohi'] = frame.insert_label_optionmenu(
        name='adjust_filter_lohi',
        label='Filtering method:',
        options=['Lowpass', 'Highpass'],
        separator=False,
        command=_populate_filter_algorithm_choices
    )

    global filter_algorithm_panels
    filter_algorithm_panels = {}
    global lowpass_options
    pymini.widgets['adjust_filter_Lowpass_algorithm'] = frame.insert_label_optionmenu(
        name='adjust_filter_Lowpass_algorithm',
        label='Lowpass algorithm:',
        options=['Boxcar'],
        separator=False,
        command=_populate_filter_param_form
    )
    filter_algorithm_panels['Lowpass'] = pymini.widgets['adjust_filter_Lowpass_algorithm'].master.master
    filter_algorithm_panels['Lowpass'].grid_remove()

    pymini.widgets['adjust_filter_Highpass_algorithm'] = frame.insert_label_optionmenu(
        name='adjust_filter_Highpass_algorithm',
        label='Highpass algorithm:',
        options=[],
        separator=False,
        command=None
    )
    filter_algorithm_panels['Highpass'] = pymini.widgets['adjust_filter_Highpass_algorithm'].master.master
    filter_algorithm_panels['Highpass'].grid_remove()

    # handle other types of filtering

    global filter_parameter_panels
    filter_parameter_panels = {}

    filter_parameter_panels['Boxcar'] = OptionFrame(frame)
    filter_parameter_panels['Boxcar'].grid_columnconfigure(0, weight=1)
    frame.insert_panel(filter_parameter_panels['Boxcar'], separator=False)

    pymini.widgets['adjust_filter_boxcar_kernel'] = filter_parameter_panels['Boxcar'].insert_label_entry(
        name='adjust_filter_boxcar_kernel',
        label='Filter kernel',
        validate_type='int',
        separator=False
    )

    frame.insert_button(
        text='Apply',
        command=_filter
    )


    _populate_filter_algorithm_choices()
    _populate_filter_param_form()

    return optionframe


def log(msg, header=True):
    if header:
        log_display.log('@ {}: {}'.format(name, msg), header)
    else:
        log_display.log("   {}".format(msg), header)


def _populate_filter_algorithm_choices(e=None):
    for key in filter_algorithm_panels:
        filter_algorithm_panels[key].grid_remove()
    filter_algorithm_panels[pymini.widgets['adjust_filter_lohi'].get()].grid()

def _populate_filter_param_form(algorithm=None):
    if algorithm is None:
        lohi = pymini.widgets['adjust_filter_lohi'].get()
        algorithm = pymini.widgets['adjust_filter_{}_algorithm'.format(lohi)].get()
    for key in filter_parameter_panels:
        filter_parameter_panels[key].grid_remove()
    try:
        filter_parameter_panels[algorithm].grid()
    except:
        pass
    pass

def undo_trace_adjust_changes(filename, delete_sweep=False, sweep_list=None):
    analyzer.trace_file.load_ydata(filename)

    if delete_sweep:
        analyzer.trace_file.delete_last_sweep()
        sweep_tab.delete_last_sweep()
        trace_display.delete_last_sweep()
    if sweep_list is not None:
        sweep_tab.show(sweep_list, False)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))
    if pymini.widgets['trace_mode'].get() == 'overlay':
        for i in range(analyzer.trace_file.sweep_count):
            trace_display.get_sweep(i).set_ydata(analyzer.trace_file.get_ys(mode='overlay', sweep=i))
    trace_display.canvas.draw()


######### Baseline Adjust
def _select_baseline_mode(e=None, undo=True):
    global prev_baseline_mode
    # if undo:
    #     # interface.add_undo([lambda m=prev_baseline_mode:pymini.widgets['adjust_baseline_mode'].set(m),
    #     #                     lambda e=None, undo=False:_select_baseline_mode(e, undo)])
    prev_baseline_mode = pymini.widgets['adjust_baseline_mode'].get()
    if pymini.widgets['adjust_baseline_mode'].get() == 'mean':
        print('mean')
        pymini.widgets['adjust_range_left'].config(state='disabled')
        pymini.widgets['adjust_range_right'].config(state='disabled')
        pymini.widgets['adjust_fixed'].config(state='disabled')
        return
    if pymini.widgets['adjust_baseline_mode'].get() == 'range':
        print('range')
        pymini.widgets['adjust_range_left'].config(state='normal')
        pymini.widgets['adjust_range_right'].config(state='normal')
        pymini.widgets['adjust_fixed'].config(state='disabled')
        return
    if pymini.widgets['adjust_baseline_mode'].get() == 'fixed':
        print('fixed')
        pymini.widgets['adjust_range_left'].config(state='disabled')
        pymini.widgets['adjust_range_right'].config(state='disabled')
        pymini.widgets['adjust_fixed'].config(state='normal')


def _adjust_baseline(e=None):
    if analyzer.trace_file is None:
        return None
    pymini.pb['value'] = 5
    pymini.pb.update()
    if pymini.widgets['adjust_channel'].get():
        channels = [analyzer.trace_file.channel]
    else:
        channels = [i for i in range(analyzer.trace_file.channel_count)]

    ######### UNDO ##########
    temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(interface.get_temp_num()))
    analyzer.trace_file.save_ydata(filename=temp_filename,
                                   channels=channels,
                                   progress_bar=pymini.pb)
    #########################

    data_list = []

    if pymini.widgets['adjust_target'].get() == 'All sweeps' or pymini.widgets[
        'trace_mode'].get() == 'continuous':
        data_list = [i for i in range(analyzer.trace_file.sweep_count)]
        if not data_list:
            return None
    elif pymini.widgets['adjust_target'].get() == 'Visible sweeps':
        data_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if
                     v.get()]  # consider making a function for this in sweep_tab
        if not data_list:
            return None
    elif pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
        data_list = [i for i in trace_display.highlighted_sweep]
        if not data_list:
            return None

    ###### Log output ######
    log('Baseline adjustment performed on: {}'.format(pymini.widgets['adjust_target'].get()), True)
    log('Traces {}'.format(analyzer.format_list_indices(data_list)), False)
    log('Channels {}'.format(channels), False)
    ########################

    task_length = len(channels)
    task_progress = 1
    baseline = []
    for c in channels:
        pymini.pb['value'] = task_progress/task_length * 90 + 10
        task_progress += 1
        pymini.pb.update()
        if pymini.widgets['adjust_baseline_mode'].get() == 'fixed':
            baseline = [float(pymini.widgets['adjust_fixed'].get())]
            #### Log ####
            log('Subtract a fixed number: {}{}'.format(baseline, analyzer.trace_file.y_unit), False)
            #############
        elif pymini.widgets['trace_mode'].get() == 'overlay':
            if pymini.widgets['adjust_baseline_mode'].get() == 'mean':
                if pymini.widgets['adjust_target'].get() == 'All sweeps':
                    ys = analyzer.trace_file.get_ys(mode='continuous', channel=c)  # get data for all ys for the channel
                    baseline = [np.mean(ys)]
                elif pymini.widgets['adjust_target'].get() == 'Visible sweeps':
                    signal_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()]
                    if not signal_list:
                        messagebox.showwarning(title='Parameter error',
                                               message='No visible sweeps',
                                               icon=messagebox.WARNING)
                        return None
                    ys = np.array([])
                    for i in signal_list:
                        ys = np.concatenate((ys, analyzer.trace_file.get_ys(mode='overlay', channel=c, sweep=i)))
                    baseline = [np.mean(ys)]
                elif pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
                    signal_list = trace_display.highlighted_sweep
                    if len(signal_list) > 0:
                        ys = np.array([])
                        for i in signal_list:
                            ys = np.concatenate((ys, analyzer.trace_file.get_ys(mode='overlay', channel=c, sweep=i)))
                        baseline = [np.mean(ys)]
                    else:
                        messagebox.showwarning(title='Parameter error',
                                               message='No sweeps are highlighted (must be in Overlay mode)',
                                               icon=messagebox.WARNING)
                        return None
                ##### Log #####
                log('Subtract the mean value: {}{}'.format(baseline, analyzer.trace_file.y_unit), False)
                ###############
            elif pymini.widgets['adjust_baseline_mode'].get() == 'range':
                if len(trace_display.sweeps) == 0:
                    return None
                xlim = (float(pymini.widgets['adjust_range_left'].get()),
                        float(pymini.widgets['adjust_range_right'].get()))
                if xlim[0] > xlim[1]:
                    xlim = (xlim[1], xlim[0])

                xlim_idx = [
                        (
                            min(
                                max(
                                    analyzer.search_index(xlim[0],
                                                          analyzer.trace_file.get_xs(mode='overlay', sweep=i),
                                                          analyzer.trace_file.sampling_rate
                                                          ),
                                    0
                                ),
                                len(analyzer.trace_file.get_xs(mode='overlay', sweep=i))
                            ),
                            max(
                                min(
                                    analyzer.search_index(xlim[1],
                                                          analyzer.trace_file.get_xs(mode='overlay', sweep=i),
                                                          analyzer.trace_file.sampling_rate
                                                          ),
                                    len(analyzer.trace_file.get_xs(mode='overlay', sweep=i))
                                ),
                                0
                            )
                        )
                    for i in data_list
                    ]
                baseline = [np.mean(analyzer.trace_file.get_ys(mode='overlay',channel=c, sweep=i)[xlim_idx[i][0]:xlim_idx[i][1]])
                            for i in data_list]
                ##### Log #####
                log('Subtract mean of range ({}, {}){}'.format(xlim[0], xlim[1], analyzer.trace_file.x_unit), False)
                log('Average adjustment: {}{}'.format(np.mean(baseline), analyzer.trace_file.y_unit), False)
                ###############
        elif pymini.widgets['trace_mode'].get() == 'continuous':
            if pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
                messagebox.showwarning(title='Parameter error',
                                       message='No sweeps are highlighted (must be in Overlay mode)',
                                       icon=messagebox.WARNING)
            else:
                # all sweeps or all visible sweeps, doesn't matter on continuous mode
                ys = analyzer.trace_file.get_ys(mode='continuous', channel=c)  # get data for all ys for the channel
                baseline = [np.mean(ys)]
                ##### Log #####
                log('Subtract the mean value: {}{}'.format(baseline, analyzer.trace_file.y_unit), False)
                ###############

        else:
            return None

        if len(data_list) > len(baseline):
            baseline = [baseline[0]] * len(data_list)
        for i in data_list:
            ys = analyzer.trace_file.get_ys(mode='overlay', channel=c, sweep=i) - baseline[i]
            analyzer.trace_file.set_ydata(channel=c, sweep=i, data=ys)
            if c == analyzer.trace_file.channel:
                trace_display.get_sweep(i).set_ydata(ys)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))




    # log('Average traces using: {}'.format(pymini.widgets['adjust_target'].get()), True)
    # log('Traces {}'.format(analyzer.format_list_indices(data_list)), False)
    # log('Channels {}'.format(channels))
    # log('Result stored on sweep {}'.format(analyzer.trace_file.sweep_count - 1), False)


    pymini.pb['value'] = 0
    pymini.pb.update()

    mean_baseline = np.mean(baseline)
    trace_display.default_ylim = (trace_display.default_ylim[0] - mean_baseline, trace_display.default_ylim[1] - mean_baseline)
    print('updated ylim: {}'.format(trace_display.default_ylim))
    interface.add_undo([lambda f=temp_filename: _undo_baseline(f),
                        lambda val=mean_baseline:trace_display.adjust_default_ylim(val)
                       ])
    if pymini.widgets['adjust_baseline_ylim'].get():
        ylim=trace_display.ax.get_ylim()
        trace_display.ax.set_ylim(ylim[0] - mean_baseline, ylim[1] - mean_baseline)
    trace_display.canvas.draw()


def _undo_baseline(filename):
    analyzer.trace_file.load_ydata(filename)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))
    if pymini.widgets['trace_mode'].get() == 'overlay':
        for i in range(analyzer.trace_file.sweep_count):
            trace_display.get_sweep(i).set_ydata(analyzer.trace_file.get_ys(mode='overlay', sweep=i))
    trace_display.canvas.draw()
    log('Undo baseline adjustment', True)

#### Trace Averaging #####
def _average_trace(e=None):
    if analyzer.trace_file is None:
        return None
    pymini.pb['value'] = 5
    pymini.pb.update()
    if pymini.widgets['adjust_channel'].get():
        channels = [analyzer.trace_file.channel]
    else:
        channels = [i for i in range(analyzer.trace_file.channel_count)]

    ################### save undo file ####################
    temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(interface.get_temp_num()))

    analyzer.trace_file.save_ydata(filename=temp_filename,
                                   channels=channels,
                                   progress_bar=pymini.pb)
    sweep_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()]
    interface.add_undo(lambda e=temp_filename, l=sweep_list: _undo_average_trace(e, sweep_list=l))
    ########################################################

    data_list = []

    if pymini.widgets['trace_mode'].get() == 'continuous':
        messagebox.showwarning(title='Error',
                               message='Cannot average in continuous mode',
                               icon=messagebox.WARNING)
        return None

    if pymini.widgets['adjust_target'].get() == 'All sweeps':
        data_list = [i for i in range(analyzer.trace_file.sweep_count)]
        if not data_list:
            return None
    elif pymini.widgets['adjust_target'].get() == 'Visible sweeps':
        data_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if
                     v.get()]  # consider making a function for this in sweep_tab
        if not data_list:
            messagebox.showwarning(title='Error',
                                   message='No visible sweeps',
                                   icon=messagebox.WARNING)
            return None
    elif pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
        data_list = [i for i in trace_display.highlighted_sweep]
        if not data_list:
            messagebox.showwarning(title='Error',
                                   message='No highlighted sweeps',
                                   icon=messagebox.WARNING)
            return None

    task_length = len(channels)
    task_progress = 1
    min_avg = [0] * len(channels)
    min_std = [0] * len(channels)
    max_avg = [0] * len(channels)
    max_std = [0] * len(channels)
    xlim = trace_display.ax.get_xlim()

    for i, c in enumerate(channels):
        pymini.pb['value'] = task_progress / task_length * 90 + 10
        task_progress += 1
        pymini.pb.update()

        y_data = np.array([analyzer.trace_file.y_data[c][i] for i in data_list])
        min_data = [0]*len(y_data)
        max_data = [0]*len(y_data)
        if pymini.widgets['adjust_avg_min_max'].get():
            for j, a in enumerate(y_data):
                xlim_idx = (analyzer.search_index(xlim[0], analyzer.trace_file.x_data[i]),
                            analyzer.search_index(xlim[1], analyzer.trace_file.x_data[i]))
                min_data[j] = min(a[xlim_idx[0]:xlim_idx[1]])
                max_data[j] = max(a[xlim_idx[0]:xlim_idx[1]])
            min_avg[i] = np.mean(min_data)
            min_std[i] = np.std(min_data)

            max_avg[i] = np.mean(max_data)
            max_std[i] = np.std(max_data)

            results_display.table_frame.add({
                'filename':analyzer.trace_file.fname,
                'channel':c+1,#0 indexing
                'analysis':'trace averaging',
                'min':min_avg[i],
                'min_unit': analyzer.trace_file.channel_units[c],
                'min_std':min_std[i],
                'max':max_avg[i],
                'max_unit': analyzer.trace_file.channel_units[c],
                'max_std':max_std[i],
            })

        avg_data = y_data.mean(axis=0)
        # add new sweep to file
        analyzer.trace_file.add_sweep(c, avg_data)
    other_channels = [i for i in range(analyzer.trace_file.channel_count) if i not in channels]
    for c in other_channels:
        empty_data = np.empty(len(avg_data))
        empty_data.fill(0)
        analyzer.trace_file.add_sweep(channel=c, data=empty_data)


    # add sweep toggle box
    sweep_tab.populate_list(1, replace=False, prefix='Avg ')

    # display sweep
    trace_display.plot_trace(analyzer.trace_file.get_xs(mode='overlay', sweep=-1),
                             analyzer.trace_file.get_ys(mode='overlay', sweep=-1),
                             draw=True,
                             relim=False,
                             idx=analyzer.trace_file.sweep_count - 1)
    sweep_tab.hide_all()
    sweep_tab.checkbuttons[-1].invoke()

    log('Trace averaging performed on: {}'.format(pymini.widgets['adjust_target'].get()), True)
    log('Traces {}'.format(analyzer.format_list_indices(data_list)), False)
    log('Channels {}'.format(channels), False)
    if pymini.widgets['adjust_avg_min_max'].get():
        log('Average min values: {}, std: {}'.format(min_avg, min_std), False)
        log('Average max values: {}, std: {}'.format(max_avg, max_std), False)
    log('Result stored on sweep {}'.format(analyzer.trace_file.sweep_count - 1), False)

def _undo_average_trace(filename, sweep_list=None):
    analyzer.trace_file.load_ydata(filename)

    analyzer.trace_file.delete_last_sweep()
    sweep_tab.delete_last_sweep()
    trace_display.delete_last_sweep()
    if sweep_list:
        sweep_tab.show(sweep_list, False)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))
    if pymini.widgets['trace_mode'].get() == 'overlay':
        for i in range(analyzer.trace_file.sweep_count):
            trace_display.get_sweep(i).set_ydata(analyzer.trace_file.get_ys(mode='overlay', sweep=i))
    trace_display.canvas.draw()
    log('Undo trace averaging', header=True)

#### Filtering #####

def _filter(e=None):
    if analyzer.trace_file is None:
        return None

    if pymini.widgets['adjust_channel'].get():
        channels = [analyzer.trace_file.channel]
    else:
        channels = [i for i in range(analyzer.trace_file.channel_count)]

    if pymini.widgets['adjust_target'].get() == 'All sweeps' or pymini.widgets[
        'trace_mode'].get() == 'continuous':
        data_list = [i for i in range(analyzer.trace_file.sweep_count)]
        if not data_list:
            return None
    elif pymini.widgets['adjust_target'].get() == 'Visible sweeps':
        data_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if
                     v.get()]  # consider making a function for this in sweep_tab
        if not data_list:
            return None
    elif pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
        data_list = [i for i in trace_display.highlighted_sweep]
        if not data_list:
            return None

    ########### Save temp file ##############
    temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(interface.get_temp_num()))

    analyzer.trace_file.save_ydata(filename=temp_filename,
                                   channels=channels,
                                   progress_bar=pymini.pb)
    pymini.pb['value'] = 2
    pymini.pb.update()
    interface.add_undo([
        lambda e=temp_filename: _undo_filtering(e)
    ])
    task_length = len(channels)
    task_progress = 1
    ##########################################
    lohi = pymini.widgets['adjust_filter_lohi'].get()
    if pymini.widgets['adjust_filter_{}_algorithm'.format(lohi)].get() == 'Boxcar':
        print('starting lowpass filter!')
        kernel = int(pymini.widgets['adjust_filter_boxcar_kernel'].get())
        k = Box1DKernel(kernel)

        parameters = {'kernel': kernel}

        for c in channels:
            pymini.pb['value'] = task_progress/task_length * 100
            pymini.pb.update()
            task_progress += 1
            for d in data_list:
                ys = analyzer.trace_file.get_ys(mode='overlay', channel=c, sweep=d)
                analyzer.trace_file.set_ydata(channel=c, sweep=d, data=convolve(ys, k))
    if pymini.widgets['trace_mode'].get() == 'overlay':
        for d in data_list:
            trace_display.get_sweep(d).set_ydata(analyzer.trace_file.get_ys(mode='overlay', sweep=d))
    elif pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))

    log('Trace filtering performed on: {}'.format(pymini.widgets['adjust_target'].get()), header=True)
    log('Traces {}'.format(analyzer.format_list_indices(data_list)), False)
    log('Channels {}'.format(channels), False)

    log('Algorithm: {}'.format(pymini.widgets['adjust_filter_{}_algorithm'.format(lohi)].get()), False)
    log('Parameters: {}'.format(str(parameters)), False)

    pymini.pb['value'] = 0
    pymini.pb.update()
    trace_display.canvas.draw()


def _undo_filtering(filename):
    analyzer.trace_file.load_ydata(filename)
    if pymini.widgets['trace_mode'].get() == 'continuous':
        trace_display.get_sweep(0).set_ydata(analyzer.trace_file.get_ys(mode='continuous'))
    if pymini.widgets['trace_mode'].get() == 'overlay':
        for i in range(analyzer.trace_file.sweep_count):
            trace_display.get_sweep(i).set_ydata(analyzer.trace_file.get_ys(mode='overlay', sweep=i))
    trace_display.canvas.draw()
    log('Undo filtering', True)