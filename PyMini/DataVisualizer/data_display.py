import tkinter as Tk
from tkinter import ttk
from collections import OrderedDict  # Python 3.7+ can use dict
import app
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
    global table_frame
    table_frame = DataTable(parent)

    global table
    table = table_frame.table

    table_frame.table.bind('<<TreeviewSelect>>', select)
    table_frame.define_columns(tuple([key for key in mini_header2config]), iid_header='t')

    return table_frame

def add(data):
    table_frame.add(data)

def append(data):
    table_frame.append(data)

def set(data):
    table_frame.set(data)

def show_columns():
    if app.widgets['analysis_mode'].get() == 'mini':
        table_frame.show_columns(tuple([
                i for i in mini_header2config
                if app.widgets[mini_header2config[i]].get()
            ]))
        pass
    else:
        # table_frame.show_columns(tuple(trace_header))
        pass
    fit_columns()

def fit_columns():
    table_frame.fit_columns()

def define_columns(columns):
    table_frame.define_columns(columns)

def add_columns(columns):
    # tuple of column headers
    table_frame.add_columns(columns)
    for c in columns:
        trace_header.append(c)


def clear():
    table_frame.clear()


def select(e=None):
    selected = table.selection()
    if app.widgets['analysis_mode'].get() == 'mini':
        if len(selected) == 1:
            interface.select_single_mini(float(selected[0]))
        interface.highlight_selected_mini([float(i) for i in selected])


def unselect(e=None):
    table_frame.unselect()

def select_one(iid):
    interface.highlight_selected_mini([float(iid)])
    table_frame.select(iid)

def delete_one(iid):
    print('data_Display delete one: {}'.format(iid))
    try:
        table_frame.delete([iid])
        interface.delete_event([iid])
    except Exception as e:
        print('data_display delete one error: {}'.format(e))
        pass
