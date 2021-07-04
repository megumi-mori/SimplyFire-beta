import tkinter as Tk
from tkinter import ttk
from utils.scrollable_option_frame import ScrollableOptionFrame
from config import config
from Backend import interface
from DataVisualizer import trace_display
import pymini
import time
def load(parent):
    frame = ScrollableOptionFrame(parent, scrollbar=False)
    frame.grid_columnconfigure(0, weight=1)

    frame.insert_title(
        name='sweep_title',
        text='Overlay Configurations'
    )
    # frame.insert_label_checkbox(
    #     name='export_sweep',
    #     label='Export sweep numbers when exporting image?',
    #     value=config.export_sweep,
    #     default=config.default_export_sweep
    # )

    frame.insert_title(
        name='sweep_select',
        text='Select Sweeps'
    )
    frame.grid_rowconfigure(3, weight=1)

    frame.insert_button(
        text='Hide All',
        command=hide_all
    )
    frame.insert_button(
        text='Show All',
        command=show_all
    )
    global list_frame
    list_frame = ScrollableOptionFrame(frame, scrollbar=True)
    list_frame.grid(sticky='news')
    frame.insert_panel(list_frame, separator=False)

    global sweep_vars
    sweep_vars = []
    global panels
    panels = []
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


def hide_all():
    length = pymini.pb.winfo_width()
    for i, var in enumerate(sweep_vars):
        if var.get() == 1:
            var.set(0)
            interface.toggle_sweep(i, 0, False)
            pymini.pb['value'] = i/len(sweep_vars) * 100
            pymini.pb.update()
    trace_display.canvas.draw()
    pymini.pb['value'] = 0

def populate_list(num):
    print('populating sweep list: {}'.format(num))
    frame = list_frame.get_frame()
    for i in range(num):
        if i < len(sweep_vars):
            panels[i].grid(column=0, row=i)
        else:
            f = Tk.Frame(frame)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(0, weight=1)
            f.grid(column=0, row=i, sticky='news')
            label = Tk.Label(f, text='Sweep {}'.format(i), justify=Tk.LEFT)
            label.grid(column=0, row=i, sticky='news')
            var = Tk.IntVar(f,1)
            button = ttk.Checkbutton(master=f,
                                     variable=var,
                                     command=lambda x=i, v=var.get:
                                     interface.toggle_sweep(x, v()))
            button.grid(column=1, row=i, sticky='es')
            sweep_vars.append(var)
            panels.append(f)
            print(var.get())
    while num < len(sweep_vars):
        temp = panels.pop(num)
        temp.forget()
        temp.destroy()
    print([var.get() for var in sweep_vars])








