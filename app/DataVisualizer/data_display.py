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

def load(parent):
    global datatable
    datatable = DataTable(parent)

    global table
    table = datatable.table

    datatable.table.bind('<<TreeviewSelect>>', select)
    datatable.define_columns(tuple([key for key in mini_header2config]))

    return datatable

def add(data):
    datatable.add(data)

def append(data):
    datatable.append(data)

def set(data):
    datatable.set(data)

def show_columns():
    if pymini.widgets['analysis_mode'].get() == 'mini':
        datatable.show_columns(tuple([
                i for i in mini_header2config
                if pymini.widgets[mini_header2config[i]].get()
            ]))
        pass
    else:
        # datatable.show_columns(tuple(trace_header))
        pass
    fit_columns()

def fit_columns():
    datatable.fit_columns()

def define_columns(columns):
    datatable.define_columns(columns)

def add_columns(columns):
    # tuple of column headers
    datatable.add_columns(columns)
    for c in columns:
        trace_header.append(c)


def clear():
    datatable.clear()


def select(e=None):
    selected = table.selection()
    if len(selected) == 1:
        interface.select_single_mini(float(selected[0]))
    if pymini.widgets['analysis_mode'].get() == 'mini':
        interface.highlight_selected_mini([float(i) for i in selected])


def unselect(e=None):
    datatable.unselect()

def select_one(iid):
    interface.highlight_selected_mini([float(iid)])
    datatable.select(iid)

def delete_one(iid):
    print('data_Display delete one: {}'.format(iid))
    try:
        datatable.delete([iid])
        interface.delete_event([iid])
    except Exception as e:
        print('data_display delete one error: {}'.format(e))
        pass
