"""
SimplyFire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from tkinter import filedialog

from SimplyFire.utils import scrollable_option_frame
from SimplyFire.backend import interface, analyzer2
from SimplyFire import app

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
    interface.open_recording(fname, append=True)

def get_color(idx):
    try:
        return var_list[idx].get()
    except:
        return app.config.default_compare_color_list[-1]

def get_sweep_list(num):
    global trace_list
    return analyzer2.translate_indices(trace_list[num]['sweep_entry'].get().strip())
