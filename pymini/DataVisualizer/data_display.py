import tkinter as Tk
from tkinter import ttk
from DataVisualizer.table import InteractiveTable
# from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict  # Python 3.7+ can use dict
import pymini
from Backend import interface

# just use this to add something:
# try:
#     self.insert("", 'end',
#                 values=[data[i] for i in self.columns],
#                 iid=data[self.id])  # should have error if already exists
# use this to remove something(s)
# def delete(self, *items):
#     super().delete(*items)
saved = True
header2config = OrderedDict([
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
#    ('auc', 'data_display_auc'),#
#     ('t_start', 'data_display_start'),
#     ('t_end', 'data_display_end'),
    ('channel', 'data_display_channel'),
    ('direction', 'data_display_direction')
])

config2header = OrderedDict([(header2config[key], key) for key in header2config.keys()])


def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)



    global table
    table = ttk.Treeview(frame)
    table.grid(column=0, row=0, sticky='news')
    table.bind('<<TreeviewSelect>>', select)

    table.config(columns=[col for col in header2config], show='headings')
    for i, col in enumerate(header2config):
        table.heading(i, text=col, command=lambda _col=col: _sort(table, _col, False))
        table.column(i, width=80, stretch=Tk.NO)

    table.bind('<Escape>', unselect)
    table.bind('<Delete>', delete)
    table.bind('<BackSpace>', delete)
    table.bind('<Control-a>', select_all)

    global selected
    selected = table.selection()

    table.show_columns = show_columns
    table.fit_columns = fit_columns

    vsb = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=table.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(frame, orient=Tk.HORIZONTAL, command=table.xview)
    hsb.grid(column=0, row=1, sticky='ew')
    table.configure(xscrollcommand=hsb.set)
    return frame


def add(data):
    table.insert("", 'end', iid=data.get('t', None), values=[data.get(i, None) for i in header2config])
    unselect()

def append(data):
    # data is dataframe
    for i in data.index:
        try:
            table.insert("", 'end', iid=i, values=[data.loc[i][k] for k in header2config])
        except:
            pass

def show_columns():
    table.config(displaycolumns=tuple([
        i for i in header2config
        if pymini.widgets[header2config[i]].get()
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
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda _col=col: _sort(tv, _col, not reverse))
    try:
        tv.see(tv.selection()[0])
    except:
        pass

def select(e=None):
    global selected
    temp = table.selection()
    if len(temp) > 0 and selected == temp:
        selected = ()
        table.selection_toggle(*temp)
    selected = table.selection()
    if len(selected) == 1:
        interface.select_single(float(selected[0]))
    interface.highlight_selected([float(i) for i in selected])

def _on_key(e=None):
    if e.keysym == 'Escape':
        unselect()

def unselect(e=None):
    global selected
    table.selection_remove(*table.selection())

def select_all(e=None):
    global selected
    table.selection_set(table.get_children())

def select_one(iid):
    table.see(str(iid))
    interface.highlight_selected([float(iid)])
    if selected == (str(iid),):
        return
    table.selection_set(str(iid))

def toggle_one(iid):
    table.selection_set(iid)
    table.see(str(iid))

def delete_one(iid):
    try:
        table.selection_remove(str(iid))
    except:
        pass
    table.delete(str(iid))
    interface.delete_event([iid])

def delete(e=None):
    sel = table.selection()
    min = table.index(sel[0])
    interface.delete_event([i for i in sel])
    table.selection_remove(*sel)
    table.delete(*sel)
    table.update()
    children = table.get_children()
    for c in children:
        if table.index(c) == min:
            table.selection_set(c)
            break


