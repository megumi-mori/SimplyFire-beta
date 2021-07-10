from utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from tkinter import ttk, StringVar, messagebox
import tkinter as Tk
import pymini
from config import config
from utils import widget
from Backend import analyzer, interface
from Layout import sweep_tab
from DataVisualizer import trace_display, log_display
import numpy as np
# from scipy.signal import convolve
import os
from astropy.convolution import Box1DKernel, convolve


#### DEBUG
import tracemalloc

def load(parent):
    optionframe = ScrollableOptionFrame(parent)

    frame = optionframe.frame

    frame.insert_title(
        name='adjust_title',
        text='Adjust Trace'
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
    frame.insert_title(
        name='baseline_subtraction',
        text='Perform baseline subtraction using:',
        separator=True,
        justify=Tk.LEFT
    )
    baseline_panel = OptionFrame(frame)
    baseline_panel.grid_columnconfigure(0, weight=1)
    frame.insert_panel(baseline_panel)
    pymini.widgets['adjust_baseline_mode'] = StringVar(baseline_panel, config.adjust_baseline_mode)
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

    frame.insert_title(
        name='baseline_signal_data',
        text='Signal/Data',
        separator=False,
        justify=Tk.LEFT
    )

    frame.insert_button(
        text='Apply',
        command=_adjust_baseline
    )
    baseline_options[config.adjust_baseline_mode]['button'].invoke()

    frame.insert_separator()

    frame.insert_title(
        name='averaging',
        text='Average trace:',
        separator=False
    )
    pymini.widgets['adjust_avg_show_result'] = frame.insert_label_checkbox(
        name='adjust_avg_show_result',
        label='Only show resultant trace (hide original sweeps)',
        onvalue='1',
        offvalue="",
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
        text='Filtering (experimental):',
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
    global Lowpass_list
    Lowpass_list = ['Boxcar', 'Gaussian (X)']

    global Highpass_list
    Highpass_list = ['???', '???']
    if pymini.widgets['adjust_filter_lohi'].get() == 'Lowpass':
        filtering_methods = Lowpass_list
    else:
        filtering_methods = Highpass_list

    pymini.widgets['adjust_filter_algorithm'] = frame.insert_label_optionmenu(
        name='adjust_filter_algorithm',
        label='Filtering algorithm:',
        options=filtering_methods,
        separator=False,
        command=None
    )


    # handle other types of filtering

    global filter_parameter_frame
    filter_parameter_frame = OptionFrame(frame)
    frame.insert_panel(filter_parameter_frame, separator=False)
    filter_parameter_frame.grid_columnconfigure(0, weight=1)

    frame.insert_button(
        text='Apply',
        command=_test_filtering
    )

    global filter_form
    filter_form = {}
    filter_form['Boxcar'] = OptionFrame(filter_parameter_frame)
    filter_form['Boxcar'].grid_columnconfigure(0, weight=1)
    pymini.widgets['adjust_filter_boxcar_kernel'] = filter_form['Boxcar'].insert_label_entry(
        name='adjust_filter_boxcar_kernel',
        label='Filter kernel',
        validate_type='int',
        separator=False
    )

    filter_form['Gaussian (X)'] = OptionFrame(filter_parameter_frame)
    filter_form['Gaussian (X)'].grid_columnconfigure(0, weight=1)
    filter_form['Gaussian (X)'].insert_title(
        name='gaussian',
        text='Not yet supported!'
    )
    filter_form['???'] = OptionFrame(filter_parameter_frame)
    filter_form['???'].grid_columnconfigure(0, weight=1)
    filter_form['???'].insert_title(
        name='???',
        text='Not yet supported!'
    )
    _populate_filter_algorithm_choices()
    _populate_filter_form()

    return optionframe

def _populate_filter_algorithm_choices(e=None):
    pymini.widgets['adjust_filter_algorithm'].clear_options()
    for m in globals()['{}_list'.format(pymini.widgets['adjust_filter_lohi'].get())]:
            pymini.widgets['adjust_filter_algorithm'].add_option(
                label=m,
                command=lambda e=m:_populate_filter_form(e))
    if e is not None:
        _populate_filter_form(globals()['{}_list'.format(e)][0])

def _populate_filter_form(e=None): ################# not working!!!
    print(e)
    filter_form[pymini.widgets['adjust_filter_algorithm'].get()].grid_forget()
    if e is not None:
        pymini.widgets['adjust_filter_algorithm'].set(e)
        filter_form[e].grid(column=0, row=0, sticky='news')
    else:
        filter_form[pymini.widgets['adjust_filter_algorithm'].get()].grid(column=0, row=0, sticky='news')


def _test_filtering(e=None):
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
    interface.add_undo(lambda e=temp_filename:
                       undo_trace_adjust_changes(e))
    task_length = len(channels)
    task_progress = 1
    ##########################################

    if pymini.widgets['adjust_filter_algorithm'].get() == 'Boxcar':
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

    log('Filter traces {}, channels {}'.format(analyzer.format_list_indices(data_list), channels), True)
    log('   Filtering algorithm: {}'.format(pymini.widgets['adjust_filter_algorithm'].get()), False)
    log('   Filtering parameters: {}'.format(str(parameters)), False)

    pymini.pb['value'] = 0
    pymini.pb.update()
    trace_display.canvas.draw()


def log(msg, header=True):
    if header:
        log_display.log('@ adjust: {}'.format(msg), header)
    else:
        log_display.log(msg, header)

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
    log('Undo trace adjustment', True)


def _select_baseline_mode(e=None):
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
    interface.add_undo(lambda e=temp_filename, d=True, l=sweep_list:
                       undo_trace_adjust_changes(e, delete_sweep=d, sweep_list=l))
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
    stdev = []
    for c in channels:
        pymini.pb['value'] = task_progress / task_length * 90 + 10
        task_progress += 1
        pymini.pb.update()

        y_data = np.array([analyzer.trace_file.y_data[c][i] for i in data_list])
        avg_data = y_data.mean(axis=0)
        stdev.append(y_data.std(axis=0).mean())

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

    log('Average traces {}, channels {}'.format(analyzer.format_list_indices(data_list), channels), True)
    log('   Standard deviation: {}'.format(stdev), False)
    log('   Average trace stored on sweep {}'.format(analyzer.trace_file.sweep_count - 1), False)


def _adjust_baseline(e=None):
    if analyzer.trace_file is None:
        return None
    pymini.pb['value'] = 5
    pymini.pb.update()
    if pymini.widgets['adjust_channel'].get():
        channels = [analyzer.trace_file.channel]
    else:
        channels = [i for i in range(analyzer.trace_file.channel_count)]

    temp_filename = os.path.join(config.DIR, *config.default_temp_path, 'temp_{}.temp'.format(interface.get_temp_num()))

    analyzer.trace_file.save_ydata(filename=temp_filename,
                                   channels=channels,
                                   progress_bar=pymini.pb)

    interface.add_undo(lambda e=temp_filename:undo_trace_adjust_changes(e))

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

    task_length = len(channels)
    task_progress = 1

    for c in channels:
        pymini.pb['value'] = task_progress/task_length * 90 + 10
        task_progress += 1
        pymini.pb.update()
        if pymini.widgets['adjust_baseline_mode'].get() == 'fixed':
            baseline = [float(pymini.widgets['adjust_fixed'].get())]
        elif pymini.widgets['trace_mode'].get() == 'overlay':
            if pymini.widgets['adjust_baseline_mode'].get() == 'mean':
                if pymini.widgets['adjust_target'].get() == 'All sweeps':
                    ys = analyzer.trace_file.get_ys(mode='continuous', channel=c)#get data for all ys for the channel
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
                print(baseline)

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
                                0
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
                    for i in range(len(trace_display.sweeps))
                    ]
                baseline = [np.mean(analyzer.trace_file.get_ys(mode='overlay',channel=c, sweep=i)[xlim_idx[i][0]:xlim_idx[i][1]])
                            for i, s in enumerate(trace_display.sweeps)]
        elif pymini.widgets['trace_mode'].get() == 'continuous':
            if pymini.widgets['adjust_target'].get() == 'Highlighted sweeps':
                messagebox.showwarning(title='Parameter error',
                                       message='No sweeps are highlighted (must be in Overlay mode)',
                                       icon=messagebox.WARNING)
            else:
                # all sweeps or all visible sweeps, doesn't matter on continuous mode
                ys = analyzer.trace_file.get_ys(mode='continuous', channel=c)  # get data for all ys for the channel
                baseline = [np.mean(ys)]

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

    log('Baseline adjustment traces {}, channels {}'.format(analyzer.format_list_indices(data_list), channels), True)
    pymini.pb['value'] = 0
    pymini.pb.update()


    trace_display.canvas.draw()
