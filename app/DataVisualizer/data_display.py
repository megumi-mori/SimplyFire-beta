import tkinter as Tk
from tkinter import ttk
from collections import OrderedDict  # Python 3.7+ can use dict
import pymini
from Backend import interface, interpreter
from utils.widget import DataTable



# just use this to add something:
# try:
#     self.insert("", 'end',
#                 values=[data[i] for i in self.columns],
#                 iid=data[self.id])  # should have error if already exists
# use this to remove something(s)
# def delete(self, *items):
#     super().delete(*items)
saved = True
mini_header2config = OrderedDict([
    ('t', 'data_display_time'),
    ('amp', 'data_display_amplitude'),
    ('amp_unit', 'data_display_amplitude'),
    ('decay_const', 'data_display_decay'),
    ('decay_unit', 'data_display_decay'),
    ('decay_func', 'data_display_decay_func'),
    # ('decay_t', 'data_display_decay_time'),
    ('rise_const', 'data_display_rise'),
    ('rise_unit', 'data_display_rise'),
    ('halfwidth', 'data_display_halfwidth'),
    ('halfwidth_unit', 'data_display_halfwidth'),
    ('baseline', 'data_display_baseline'),
    ('baseline_unit', 'data_display_baseline'),
    ('channel', 'data_display_channel'),
    ('direction', 'data_display_direction')
])

config2header = OrderedDict([(mini_header2config[key], key) for key in mini_header2config.keys()])

trace_header = [
    'sweep',
    'state'
]

def load(parent):
    global frame
    frame = DataTable(parent)

    global table
    table = frame.table

    frame.table.bind('<<TreeviewSelect>>', select)

    return frame

def add(data):
    frame.add(data)

def append(data):
    frame.append(data)

def set(data):
    frame.set(data)

def show_columns():
    if pymini.widgets['analysis_mode'].get() == 'mini':
        frame.show_columns(tuple([
                i for i in mini_header2config
                if pymini.widgets[mini_header2config[i]].get()
            ]))
        pass
    else:
        # frame.show_columns(tuple(trace_header))
        pass
    fit_columns()

def fit_columns():
    frame.fit_columns()

def define_columns(columns):
    frame.define_columns(columns)

def add_columns(columns):
    # tuple of column headers
    frame.add_columns(columns)
    for c in columns:
        trace_header.append(c)


def clear():
    frame.clear()


def select(e=None):
    selected = table.selection()
    if len(selected) == 1:
        interface.select_single_mini(float(selected[0]))
    if pymini.widgets['analysis_mode'].get() == 'mini':
        interface.highlight_selected_mini([float(i) for i in selected])


def unselect(e=None):
    frame.unselect()

def select_one(iid):
    interface.highlight_selected_mini([float(iid)])
    frame.select(iid)

def delete_one(iid):
    frame.delete_one(iid)
    interface.delete_event([iid])
