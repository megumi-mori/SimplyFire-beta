from utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from tkinter import ttk, StringVar, messagebox
import tkinter as Tk
import pymini
from config import config
from utils import widget
from Backend import analyzer, interface
from Layout import sweep_tab
from DataVisualizer import log_display
import numpy as np
# from scipy.signal import convolve
import os
# from astropy.convolution import Box1DKernel, convolve
from scipy.signal import boxcar, convolve

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

#
# def log(msg, header=True):
#     if header:
#         log_display.log('@ {}: {}'.format(name, msg), header)
#     else:
#         log_display.log("   {}".format(msg), header)


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

    all_channels = True
    if pymini.widgets['adjust_channel'].get():
        all_channels = False

    try:
        xlim = (float(pymini.widgets['adjust_range_left'].get()),
                                float(pymini.widgets['adjust_range_right'].get()))
    except:
        xlim = None
    try:
        fixed_val = float(pymini.widgets['adjust_fixed'].get())
    except:
        fixed_val = None
    mode = pymini.widgets['adjust_baseline_mode'].get()
    interface.adjust_baseline(all_channels, target=pymini.widgets['adjust_target'].get(),
                              mode=mode,
                              xlim=xlim,
                              fixed_val=fixed_val
                              )

#### Trace Averaging #####
def _average_trace(e=None):
    if analyzer.trace_file is None:
        return None
    pymini.pb['value'] = 5
    pymini.pb.update()
    if pymini.widgets['adjust_channel'].get():
        all_channels=False
    else:
        all_channels=True

    interface.average_y_data(all_channels=all_channels,
                                      target=pymini.widgets['adjust_target'].get(),
                                      report_minmax=pymini.widgets['adjust_avg_min_max'].get(),
                                      limit_minmax_window=pymini.widgets['adjust_avg_window'].get(),
                                      hide_all=pymini.widgets['adjust_avg_show_result'].get())

#### Filtering #####
def _filter(e=None):
    if pymini.widgets['adjust_channel'].get():
        all_channels = False
    else:
        all_channels=True

    lohi = pymini.widgets['adjust_filter_lohi'].get()
    mode = pymini.widgets['adjust_filter_{}_algorithm'.format(lohi)].get()
    params={}
    if mode == 'Boxcar':
        params['kernel'] = int(pymini.widgets['adjust_filter_boxcar_kernel'].get())
    interface.filter_y_data(all_channels, target=pymini.widgets['adjust_target'].get(),
                            mode=mode, params=params)

