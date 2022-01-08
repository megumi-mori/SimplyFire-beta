import tkinter as Tk
from tkinter import ttk, filedialog

from PyMini.utils import scrollable_option_frame
from PyMini.Backend import interface, analyzer2
from PyMini.DataVisualizer import trace_display
from PyMini import app

def load(parent):
    global frame
    frame = scrollable_option_frame.OptionFrame(parent)
    frame.grid_columnconfigure(0, weight=1)

    frame.insert_title(
        name='compare_title',
        text='Comparison Mode'
    )

    global widgets
    widgets = {}

    global add_button
    add_button = frame.insert_button(
        text='Add Trace',
        command=add_trace
    )

    global list_frame
    list_frame = scrollable_option_frame.ScrollableOptionFrame(frame)
    list_frame.grid(sticky='news')
    list_frame.columnconfigure(0, weight=1)
    frame.grid_rowconfigure(3, weight=1)

    global start_msg
    start_msg = list_frame.frame.insert_title(
        text='Open a trace file to start'
    )

    global trace_list
    trace_list = []

    frame.insert_button(
        text='Apply',
        command=apply
    )

    return frame

def refresh_list():
    while len(trace_list) > 1:
        temp = trace_list.pop()
        temp.forget()
        temp.destroy()
        del temp
    global frame
    f = Tk.Frame(frame.master)


def add_trace(e=None):
    if len(interface.recordings)==0:
        fname = app.menubar.ask_open_trace()
    else:
        fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', '*.abf'), ('csv files', '*.csv'), ('All files', '*.*')])
        interface.open_trace(fname, append=True)
    if not fname:
        return None

def increase_trace_list(fname):
    global trace_list
    num = len(trace_list)
    panel = list_frame.frame.make_panel()
    entry_panel = scrollable_option_frame.OptionFrame(panel)
    entry_panel.grid_columnconfigure(0, weight=1)
    entry_panel.grid(row=0, column=0, sticky='news')

    if len(interface.recordings) == 1:
        default_sweeps = range(interface.recordings[0].sweep_count)
    else:
        default_sweeps = range(interface.recordings[-1].sweep_count)
    default_sweeps = analyzer2.format_list_indices(default_sweeps)
    trace_list.append({
        'title': entry_panel.insert_title(
            text=f'File {num+1}:',
            separator=False
        ),
        'sweep_entry': entry_panel.insert_label_entry(
            value="",
            default=default_sweeps,
            label='Sweep indices',
            validate_type='indices',
            separator=False,
        ),
        'color_entry': entry_panel.insert_label_entry(
            value='Black',
            default="Black",
            label='Plot color',
            validate_type='color',
            separator=False
        )
    })

def apply(e=None):
    pass

def get_sweep_list(num):
    global trace_list
    return analyzer2.translate_indices(trace_list[num]['sweep_entry'].get().strip())
