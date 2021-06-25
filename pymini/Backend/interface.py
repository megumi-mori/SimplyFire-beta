# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog
from DataVisualizer import data_display, log_display, trace_display
import os
from utils import recording
import matplotlib as mpl
from Backend import analyzer
import gc


### this module connects the analyzer and the gui

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

    if pymini.widgets['apply_axis_limit'].get() == '1':
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
                          analyzer.trace.get_ys(mode='continuous'))
    trace_display.default_xlim = trace_display.ax.get_xlim()
    trace_display.default_ylim = trace_display.ax.get_ylim()
    trace_display.ax.set_xlim(xlim)
    trace_display.canvas.draw()


def plot_continuous():
    trace_display.plot_trace(analyzer.trace.get_xs(mode='continuous'),
                             analyzer.trace.get_ys(mode='continuous'))
    trace_display.ax.relim()
    trace_display.default_xlim = trace_display.ax.get_xlim()
    trace_display.default_ylim = trace_display.ax.get_ylim()
    pass


def plot_overlay():
    print('overlay currently not supported')
    pass


def configure(key, value):
    globals()[key] = value


def search_event_from_click(x):
    pass


#######################################

def point_click(x):
    dir = 1
    if pymini.widgets['detector_direction'].get() == 'negative':
        dir = -1

    xlim = trace_display.ax.get_xlim()

    ylim = trace_display.ax.get_ylim()

    lag = int(pymini.widgets['detector_points_baseline'].get())
    points_search = int(pymini.widgets['detector_points_search'].get())
    max_points_baseline = int(pymini.widgets['detector_max_points_baseline'].get())
    max_points_decay = int(pymini.widgets['detector_max_points_decay'].get())
    min_amp = float(pymini.widgets['detector_min_amp'].get())
    min_decay = float(pymini.widgets['detector_min_decay'].get())
    min_hw = float(pymini.widgets['detector_min_hw'].get())
    min_rise = float(pymini.widgets['detector_min_rise'].get())

    data = analyzer.find_single_event(x, xlim, ylim, dir, lag, points_search, max_points_baseline, max_points_decay,
                                      min_amp, min_decay, min_hw, min_rise)
    log_display.search_update('manual search centered on x:{}. Parameters: {}'.format(
        x,
        [(i, pymini.widgets[i].get()) for i in pymini.widgets.keys() if 'detector_' in i]
    ))

    pass