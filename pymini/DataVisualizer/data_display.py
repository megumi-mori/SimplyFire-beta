import tkinter as Tk
from tkinter import ttk
from DataVisualizer.table import InteractiveTable
# from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict  # Python 3.7+ can use dict
import pymini

# just use this to add something:
# try:
#     self.insert("", 'end',
#                 values=[data[i] for i in self.columns],
#                 iid=data[self.id])  # should have error if already exists
# use this to remove something(s)
# def delete(self, *items):
#     super().delete(*items)

header2config = OrderedDict([
    ('t', 'data_display_time'),
    ('amp', 'data_display_amplitude'),
    ('amp_unit', 'data_display_amplitude'),
    ('decay_const', 'data_display_decay'),
    ('decay_unit', 'data_display_decay'),
    ('decay_t', 'data_display_decay_time'),
    ('rise_const', 'data_display_rise'),
    ('rise_unit', 'data_display_rise'),
    ('halfwidth', 'data_display_halfwidth'),
    ('halfwidth_unit', 'data_display_halfwidth'),
    ('baseline', 'data_display_baseline'),
    ('baseline_unit', 'data_display_baseline'),
    ('t_start', 'data_display_start'),
    ('t_end', 'data_display_end'),
    ('channel', 'data_display_channel',)
])
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
    'end_coord_y',  #

    # data
    'datetime'  #
]
config2header = OrderedDict([(header2config[key], key) for key in header2config.keys()])


def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global table
    table = ttk.Treeview(frame)
    table.grid(column=0, row=0, sticky='news')

    table.config(columns=columns, show='headings')
    for i, col in enumerate(columns):
        table.heading(i, text=col, command=lambda _col=col: _sort(table, _col, False))
        table.column(i, width=80, stretch=Tk.NO)

    table.show_columns = show_columns
    table.fit_columns = fit_columns

    vsb = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=table.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(frame, orient=Tk.HORIZONTAL, command=table.xview)
    hsb.grid(column=0, row=1, sticky='ew')
    table.configure(xscrollcommand=hsb.set)
    return frame


add = lambda x: table.insert("", 'end', iid=x.get('t', None), values=[x.get(i, None) for i in columns])


def show_columns():
    table.config(displaycolumns=tuple([
        i for i in header2config
        if pymini.get_value(header2config[i])
    ]))


def fit_columns():
    indices = [i for i in header2config
               if pymini.get_value(header2config[i])]
    w = int(table.winfo_width() / len(indices))
    for i in indices:
        table.column(i, width=w)


def clear():
    table.selection_remove(*table.selection())
    table.delete(*table.get_children())

def _sort(tv, col, reverse):
    try:
        l = [(float(tv.set(k, col)), k) for k in tv.get_children('')]
    except:
        l = [(tv.set(k, col), l) for k in tv.get_chidlren('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda _col=col: _sort(_col, not reverse))
