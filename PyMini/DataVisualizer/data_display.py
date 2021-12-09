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
    # ('decay_func', 'data_display_decay_func'),
    # ('decay_t', 'data_display_decay_time'),
    ('rise_const', 'data_display_rise'),
    ('rise_unit', 'data_display_rise'),
    ('halfwidth', 'data_display_halfwidth'),
    ('halfwidth_unit', 'data_display_halfwidth'),
    ('baseline', 'data_display_baseline'),
    ('baseline_unit', 'data_display_baseline'),
    ('channel', 'data_display_channel'),
    ('direction', 'data_display_direction'),
    ('compound', 'data_display_compound')
])


config2header = OrderedDict([
    ('data_display_time', ('t')),
    ('data_display_amplitude', ('amp', 'amp_unit')),
    ('data_display_decay', ('decay_const', 'decay_unit')),
    ('data_display_rise', ('rise_const', 'rise_unit')),
    ('data_display_halfwidth', ('halfwidth', 'halfwidth_unit')),
    ('data_display_baseline', ('baseline','baseline_unit')),
    ('data_display_channel', ('channel')),
    ('data_display_direction', ('direction')),
    ('data_display_compound', ('compound'))
])

def load(parent):
    global frame
    frame = Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    global dataframe
    dataframe = DataTable(frame)

    global table
    table = dataframe.table

    dataframe.table.bind('<<TreeviewSelect>>', select)
    dataframe.define_columns(tuple([key for key in mini_header2config]), iid_header='t')
    dataframe.grid(column=0, row=0, sticky='news')

    return frame

def add(data):
    dataframe.add(data)

def append(data):
    dataframe.append(data)

def set(data):
    dataframe.set(data)

def show_columns(columns=None):
    dataframe.show_columns(tuple([
       i for i in mini_header2config
        if mini_header2config[i] in columns
    ]))
    # if app.widgets['analysis_mode'].get() == 'mini':
    #     dataframe.show_columns(tuple([
    #             i for i in mini_header2config
    #             if app.widgets[mini_header2config[i]].get()
    #         ]))
    #     pass
    # else:
    #     # dataframe.show_columns(tuple(trace_header))
    #     pass
    fit_columns()

def fit_columns():
    dataframe.fit_columns()

def define_columns(columns):
    dataframe.define_columns(columns)

def add_columns(columns):
    # tuple of column headers
    dataframe.add_columns(columns)
    for c in columns:
        trace_header.append(c)


def clear():
    dataframe.clear()

def hide():
    dataframe.hide()

def select(e=None):
    selected = table.selection()
    if app.widgets['analysis_mode'].get() == 'mini':
        if len(selected) == 1:
            interface.select_single_mini(float(selected[0]))
        interface.highlight_selected_mini([float(i) for i in selected])


def unselect(e=None):
    dataframe.unselect()

# def select_one(iid):
#     raise
#     interface.highlight_selected_mini([float(iid)])
#     dataframe.select(iid)

def delete_one(iid):
    print('data_Display delete one: {}'.format(iid))
    try:
        dataframe.delete([iid])
        interface.delete_event([iid])
    except Exception as e:
        print('data_display delete one error: {}'.format(e))
        pass
