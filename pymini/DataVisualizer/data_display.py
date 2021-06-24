import tkinter as Tk
from tkinter import ttk
from DataVisualizer.table import InteractiveTable
# from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict #Python 3.7+ can use dict
import pymini

def load(parent, root):
    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global table
    table = ttk.Treeview
    table.grid(column=0, row=0, sticky='news')

    vsb = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=table.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(frame, orient=Tk.HORIZONTAL, command=table.xview)
    hsb.grid(column=0, row=1, sticky='ew')
    table.configure(xscrollcommand=hsb.set)

    columns = [
        # panel -- make sure this matches with the config2header dict
        't',  #
        'amp',  #
        'amp_unit',  #
        'decay_const',
        'decay_unit',
        'decay_t',
        'rise_const',  #
        'rise_unit',  #
        'halfwidth',
        'halfwidth_unit',
        'baseline',  #
        'baseline_unit',  #
        't_start',  #
        't_end',  #
        'channel',  #
        # plot
        'peak_coord_x',  # (x,y) #
        'peak_coord_y',  #
        'decay_coord_x',
        'decay_coord_y',
        'start_coord_x',  #
        'start_coord_y',  #
        'end_coord_x',  #
        'end_coord_y'  #
    ]

    table.config(columns=columns, show='headings')
    table.set_id('t')

    return frame











