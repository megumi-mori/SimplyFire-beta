import tkinter as Tk
from tkinter import ttk, filedialog

from PyMini.utils import scrollable_option_frame
from PyMini.Backend import interface, analyzer2
from PyMini.DataVisualizer import trace_display
from PyMini import app

import os

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
    add_button.config(state='disabled')

    global list_frame
    list_frame = scrollable_option_frame.ScrollableOptionFrame(frame)
    list_frame.grid(sticky='news')
    frame.insert_panel(list_frame)
    list_frame.columnconfigure(0, weight=1)
    frame.grid_rowconfigure(2, weight=1)

    global start_msg
    start_msg = list_frame.frame.insert_title(
        text='Open a trace file to start'
    )

    global trace_list
    trace_list = []
    global var_list
    var_list = []
    global apply_button
    apply_button = frame.insert_button(
        text='Apply',
        command=apply
    )
    apply_button.config(state='disabled')
    global num_visible
    num_visible = 0

    return frame

# def refresh_list():
#     while len(trace_list) > 1:
#         temp = trace_list.pop()
#         temp.forget()
#         temp.destroy()
#         del temp
#     global frame
#     f = Tk.Frame(frame.master)


def add_trace(e=None):
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', '*.abf'), ('csv files', '*.csv'), ('All files', '*.*')])
    if not fname:
        return None
    interface.open_trace(fname, append=True)


def reset_trace_list(fname):
    global trace_list
    global num_visible
    if len(trace_list)>0:
        for t in trace_list[1:]:
            t['panel'].grid_remove()
        trace_list[0]['title'].config(text=f'File {os.path.split(fname)[1]}'),
        trace_list[0]['sweep_entry'].set(analyzer2.format_list_indices(range(interface.recordings[0].sweep_count)))
        num_visible = 1
    else:
        increase_trace_list(fname)
    global apply_button
    apply_button.config(state='normal')

    global add_button
    add_button.config(state='normal')

    pass
def get_color(idx):
    try:
        return var_list[idx].get()
    except:
        return app.config.default_compare_color_list[-1]

def increase_trace_list(fname):
    global trace_list
    global num_visible
    global list_frame
    if len(trace_list) > num_visible:
        trace_list[num_visible]['panel'].grid()
    else:
        entry_panel = scrollable_option_frame.OptionFrame(list_frame.frame)
        entry_panel.grid_columnconfigure(0, weight=1)
        list_frame.frame.insert_panel(entry_panel)

        if len(interface.recordings) == 1:
            default_sweeps = range(interface.recordings[0].sweep_count)
        else:
            default_sweeps = range(interface.recordings[-1].sweep_count)
        default_sweeps = analyzer2.format_list_indices(default_sweeps)
        try:
            default_color = app.config.compare_color_list[len(interface.recordings)-1]
        except:
            default_color = app.config.default_compare_color_list[-1]
        trace_list.append({
            'title': entry_panel.insert_title(
                text=f'File {os.path.split(fname)[1]}',
                separator=False
            ),
            'sweep_entry': entry_panel.insert_label_entry(
                value=default_sweeps,
                default=0,
                label='Sweep indices',
                validate_type='indices',
                separator=False,
            ),
            'color_entry': entry_panel.insert_label_entry(
                value=default_color,
                default="Black",
                label='Plot color',
                validate_type='color',
                separator=False
            ),
            'panel':entry_panel
        })
        trace_list[-1]['color_entry'].bind('<Return>', apply, add='+')
        trace_list[-1]['sweep_entry'].bind('<Return>', apply, add='+')
        global var_list
        var_list.append(trace_list[-1]['color_entry'].var)
        num_visible += 1

def apply(e=None):
    app.trace_display.apply_styles(['compare_color_list'], draw=False)
    idx_offset = 0
    for i,r  in enumerate(interface.recordings):
        for idx in range(r.sweep_count):
            app.trace_display.hide_sweep(idx+idx_offset)
        for idx in get_sweep_list(i):
            app.trace_display.show_sweep(idx+idx_offset)
        idx_offset += r.sweep_count
    pass
    app.trace_display.canvas.get_tk_widget().focus_set()
    app.trace_display.canvas.draw()

def get_sweep_list(num):
    global trace_list
    return analyzer2.translate_indices(trace_list[num]['sweep_entry'].get().strip())