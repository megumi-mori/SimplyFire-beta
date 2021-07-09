from utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from tkinter import ttk, StringVar, messagebox
import tkinter as Tk
import pymini
from config import config
from utils import widget
from Backend import analyzer
from Layout import sweep_tab
from DataVisualizer import trace_display
import numpy as np
# from scipy.signal import convolve
from astropy.convolution import Box1DKernel, convolve

def load(parent):
    optionframe = ScrollableOptionFrame(parent)

    frame = optionframe.frame

    frame.insert_title(
        name='adjust_title',
        text='Adjust Trace'
    )
    frame.insert_title(
        name='baseline_subtraction',
        text='Perform baseline subtraction using:',
        separator=False,
        justify=Tk.LEFT
    )
    baseline_panel = OptionFrame(frame)
    baseline_panel.grid_columnconfigure(0, weight=1)
    frame.insert_panel(baseline_panel)
    pymini.widgets['adjust_baseline_mode'] = StringVar(baseline_panel, config.adjust_baseline_mode)
    baseline_options = {
        'mean': {'name': 'mean',
         'text': 'Mean of:',
         'value': 'mean'
         },
        'range': {
            # 'name': 'range',
            # 'text': 'Mean of range per sweep:',
            'value': 'range'
        },
        'fixed': {
            # 'name': 'fixed',
            # 'text': 'Specified value:',
            'value': 'fixed'
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

    pymini.widgets['adjust_baseline_signal'] = baseline_panel.insert_label_optionmenu(
        name='adjust_baseline_signal',
        label='Calculate mean of:',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )

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

    pymini.widgets['adjust_baseline_target'] = frame.insert_label_optionmenu(
        name='adjust_baseline_target',
        label='Adjust baseline for:',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )
    pymini.widgets['adjust_baseline_channel'] = frame.insert_label_checkbox(
        name='adjust_baseline_channel',
        label='Apply to visible channel only',
        onvalue='1',
        offvalue="",
        separator=False
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

    pymini.widgets['adjust_avg_signal'] = frame.insert_label_optionmenu(
        name='adjust_avg_signal',
        label='Average:',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )
    pymini.widgets['adjust_avg_show_result'] = frame.insert_label_checkbox(
        name='adjust_avg_show_result',
        label='Only show resultant trace (hide original sweeps)',
        onvalue='1',
        offvalue="",
        separator=False
    )
    pymini.widgets['adjust_avg_channel'] = frame.insert_label_checkbox(
        name='adjust_avg_channel',
        label='Apply to visible channel only',
        onvalue='1',
        offvalue='',
        separator=False
    )
    frame.insert_button(
        text='Apply',
        command=None
    )
    frame.insert_separator()
    pymini.widgets
    frame.insert_title(
        name='filtering',
        text='Test Box2DKernel:',
        separator=False,
        justify=Tk.LEFT
    )
    pymini.widgets['filter_kernel'] = frame.insert_label_entry(
        name='filter_kernel',
        label='Filter kernel:',
        validate_type='int'
    )

    # add a filtered count here!

    # handle other types of filtering
    frame.insert_button(
        text='Apply',
        command=_test_filtering
    )
    return optionframe

def _select_baseline_mode(e=None):
    if pymini.widgets['adjust_baseline_mode'].get() == 'mean':
        print('mean')
        pymini.widgets['adjust_range_left'].config(state='disabled')
        pymini.widgets['adjust_range_right'].config(state='disabled')
        pymini.widgets['adjust_fixed'].config(state='disabled')
        pymini.widgets['adjust_baseline_signal'].config(state='normal')
        return
    if pymini.widgets['adjust_baseline_mode'].get() == 'range':
        print('range')
        pymini.widgets['adjust_range_left'].config(state='normal')
        pymini.widgets['adjust_range_right'].config(state='normal')
        pymini.widgets['adjust_fixed'].config(state='disabled')
        pymini.widgets['adjust_baseline_signal'].config(state='disabled')
        return
    if pymini.widgets['adjust_baseline_mode'].get() == 'fixed':
        print('fixed')
        pymini.widgets['adjust_range_left'].config(state='disabled')
        pymini.widgets['adjust_range_right'].config(state='disabled')
        pymini.widgets['adjust_fixed'].config(state='normal')
        pymini.widgets['adjust_baseline_signal'].config(state='disabled')


def _adjust_baseline(e=None):
    signal_list = None
    if pymini.widgets['adjust_baseline_channel'].get():
        channels = [analyzer.trace_file.channel]
    else:
        channels = [i for i in range(analyzer.trace_file.channel_count)]
    if pymini.widgets['adjust_baseline_mode'].get() == 'mean':
        if pymini.widgets['adjust_baseline_target'].get() == 'All sweeps':
            ys = np.array([])
            for s in trace_display.sweeps:
                ys = np.concatenate((ys, trace_display.sweeps[s].get_ydata()))
            if len(ys) == 0:
                print(ys)
                return None
            baseline = [np.mean(ys)]
        elif pymini.widgets['adjust_baseline_target'].get() == 'Visible sweeps':
            if pymini.widgets['trace_mode'].get() == 'overlay':
                signal_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()]
            else:
                signal_list = [0]
            if not signal_list:
                messagebox.showwarning(title='Parameter error',
                                       message='No visible sweeps',
                                       icon=messagebox.WARNING)
                return None
            ys = np.array([])
            for i in signal_list:
                ys = np.concatenate((ys, trace_display.sweeps['sweep_{}'.format(i)].get_ydata()))
            baseline = [np.mean(ys)]
        elif pymini.widgets['adjust_baseline_target'].get() == 'Highlighted sweeps':
            signal_list = trace_display.highlighted_sweep
            if len(signal_list) > 0:
                ys = np.array([])
                for i in signal_list:
                    ys = np.concatenate((ys, trace_display.sweeps['sweep_{}'.format(i)].get_ydata()))
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
                                                  trace_display.sweeps['sweep_{}'.format(i)].get_xdata(),
                                                  analyzer.trace_file.sampling_rate
                                                  ),
                            0
                        ),
                        0
                    ),
                    max(
                        min(
                            analyzer.search_index(xlim[1],
                                                  trace_display.sweeps['sweep_{}'.format(i)].get_xdata(),
                                                  analyzer.trace_file.sampling_rate
                                                  ),
                            len(analyzer.trace_file.get_xs(mode='overlay', sweep=i))
                        ),
                        0
                    )
                )
            for i in range(len(trace_display.sweeps))
            ]
        baseline = [np.mean(trace_display.sweeps[s].get_ydata()[xlim_idx[i][0]:xlim_idx[i][1]])
                    for i, s in enumerate(trace_display.sweeps)]
    elif pymini.widgets['adjust_baseline_mode'].get() == 'fixed':
        baseline = [float(pymini.widgets['adjust_fixed'].get())]

    else:
        print('baseline adjust - unkonwn selection made')
        return None
    print(baseline)
    data_list = []
    if pymini.widgets['adjust_baseline_target'].get() == 'All sweeps':
        data_list = [i for i in range(len(trace_display.sweeps))]
        if not data_list:
            return None
    elif pymini.widgets['adjust_baseline_target'].get() == 'Visible sweeps':
        data_list = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()] # consider making a function for this in sweep_tab
        if not data_list:
            return None
    elif pymini.widgets['adjust_baseline_target'].get() == 'Highlighted sweeps':
        data_list = [i for i in trace_display.highlighted_sweep]
        if not data_list:
            return None
        if pymini.widgets['trace_mode'].get() == 'overlay':
            if len(baseline) == 1:
                pass
    if len(data_list) > len(baseline):
        baseline = [baseline[0]] * len(data_list)

    for i in data_list:
        trace_display.get_sweep(i).set_ydata(np.array(trace_display.get_sweep(i).get_ydata()) - baseline[i])

    trace_display.canvas.draw()



    # calculate offset:

    print(signal_list)

def _test_filtering(e=None):
    kernel = int(pymini.widgets['filter_kernel'].get())
    k = Box1DKernel(kernel)
    ys = trace_display.ax.lines[0].get_ydata()
    print(convolve(ys, k))

    trace_display.ax.lines[0].set_ydata(convolve(ys, k))
    trace_display.canvas.draw()
