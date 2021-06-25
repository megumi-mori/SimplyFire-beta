# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog
from DataVisualizer import data_display, log_display, trace_display
import os
from utils import recording
import matplotlib as mpl
from Backend import analyzer


### this module connects the analyzer and the gui

def ask_open_trace():
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    if fname:
        pymini.trace_filename = fname
    else:
        return None
    data_display.clear()
    open_trace(fname)

def open_trace(fname):

    #trace stored in analyzer
    analyzer.open_trace(fname)

    log_display.open_update(fname)

    # update save file directory
    if pymini.widgets['config_file_autodir'].get() == '1':
        mpl.rcParams['savefig.directory'] = os.path.split(fname)[0]

    # check if channel number is specified by user:
    if pymini.widgets['force_channel'].get() == '1':
        try:
            analyzer.trace.set_channel(int(pymini.widgets['force_channel_id'].get()) - 1) #1 indexing
        except Exception as e:
            print(e)
            pass

    trace_display.clear()
    trace_display.ax.set_xlabel(analyzer.trace.x_label)
    trace_display.ax.set_ylabel(analyzer.trace.y_label)
    trace_display.canvas.draw()

def configure(key, value):
    globals()[key] = value

def search_event_from_click(x):

    pass


