import tkinter as Tk
import tracemalloc
from tkinter import ttk
from utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from config import config
from Backend import interface
from DataVisualizer import trace_display
import pymini
import time
import gc

def load(parent):
    frame = OptionFrame(parent)#, scrollbar=False)
    frame.grid_columnconfigure(0, weight=1)


    frame.insert_title(
        name='sweep_title',
        text='Overlay Mode'
    )
    frame.insert_title(
        name='sweep_select',
        text='Select Sweeps'
    )
    frame.insert_button(
        text='Hide All',
        command=hide_all
    )
    frame.insert_button(
        text='Show All',
        command=show_all
    )
    frame.grid_rowconfigure(3, weight=1)
    global list_frame
    list_frame = ScrollableOptionFrame(frame)#, scrollbar=True)
    list_frame.grid(sticky='news')
    frame.insert_panel(list_frame, separator=False)

    pymini.widgets['sweep_picker_offset'] = frame.insert_label_entry(
        name='sweep_picker_offset',
        label='Sweep picker search radius (% of x-axis)', #might change to us
        validate_type=('float')
    )
    frame.insert_button(
        text='Delete added',
        command=delete_hidden
    )

    global sweep_vars
    sweep_vars = []
    global panels
    panels = []
    global checkbuttons
    checkbuttons = []
    global sweep_labels
    sweep_labels = []
    return frame


def show_all():
    for i, var in enumerate(sweep_vars):
        if var.get() == 0:
            var.set(1)
            interface.toggle_sweep(i, 1, False)
            pymini.pb['value'] = i / len(sweep_vars) * 100
            pymini.pb.update()
    trace_display.canvas.draw()
    pymini.pb['value'] = 0

def show(idx=None, draw=False):
    for i in idx:
        if sweep_vars[i].get() == 0:
            sweep_vars[i].set(1)
            interface.toggle_sweep(i, 1, False)
    if draw:
        trace_display.canvas.draw()

def delete_last_sweep():
    temp = panels.pop()
    temp.forget()
    temp.destroy()
    del temp

    temp = sweep_vars.pop()
    del temp

    temp = checkbuttons.pop()
    temp.forget()
    temp.destroy()
    del temp

    temp = sweep_labels.pop()
    temp.forget()
    temp.destroy()
    del temp

    gc.collect()

def hide_all():
    for i, var in enumerate(sweep_vars):
        if var.get() == 1:
            var.set(0)
            interface.toggle_sweep(i, 0, False)
            pymini.pb['value'] = i/len(sweep_vars) * 100
            pymini.pb.update()
    trace_display.canvas.draw()
    pymini.pb['value'] = 0

def delete_hidden():
    delete = [i for i, var in enumerate(sweep_vars) if not var.get()]
    # interface.delete_hidden(delete)

def populate_list(num, replace=True, prefix=""):
    frame = list_frame.get_frame()

    if replace:
        start = 0
    else:
        start = len(sweep_vars)
    for i in range(num):
        if i+start < len(sweep_vars):
            sweep_labels[i].config(text='{}Sweep {}'.format(prefix, i+start))
        else:
            f = Tk.Frame(frame)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(0, weight=1)
            f.grid(column=0, row=start+i, sticky='news')
            label = Tk.Label(f, text='{}Sweep {}'.format(prefix, len(sweep_vars)), justify=Tk.LEFT)
            label.grid(column=0, row=start+i, sticky='news')
            sweep_labels.append(label)
            var = Tk.IntVar(f, 1)
            button = ttk.Checkbutton(master=f,
                                     variable=var,
                                     command=lambda x=start+i, v=var.get:
                                     interface.toggle_sweep(x, v()))
            checkbuttons.append(button)
            button.grid(column=1, row=start+i, sticky='es')
            sweep_vars.append(var)
            panels.append(f)
    if replace:
        while len(sweep_vars) > num:
            temp = panels.pop()
            temp.forget()
            temp.destroy()
            del temp
            # frames are getting removed from the parent frame - memory leak is not caused by this
            temp = checkbuttons.pop()
            temp.forget()
            temp.destroy()
            del temp
            temp = sweep_labels.pop()
            temp.forget()
            temp.destroy()
            del temp
            temp = sweep_vars.pop()
            del temp











