import tkinter as Tk
from tkinter import ttk
from collections import OrderedDict  # Python 3.7+ can use dict
import pymini
from Backend import interface, interpreter



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
#    ('auc', 'data_display_auc'),#
#     ('t_start', 'data_display_start'),
#     ('t_end', 'data_display_end'),
    ('channel', 'data_display_channel'),
    ('direction', 'data_display_direction')
])

config2header = OrderedDict([(mini_header2config[key], key) for key in mini_header2config.keys()])

trace_header = [
    'sweep',
    'state'
]

def define_columns(columns):
    table.config(columns=columns, show='headings')
    global headers
    headers = columns
    for i, col in enumerate(columns):
        table.heading(i, text=col, command=lambda _col=col: _sort(table, _col, False))
        table.column(i, width=80, stretch=Tk.NO)

def setup_column_headers(mode):
    if mode == 'mini':
        define_columns([h for h in mini_header2config])
    else:
        define_columns([h for h in trace_header])
def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global table
    table = ttk.Treeview(frame)
    table.grid(column=0, row=0, sticky='news')
    table.bind('<<TreeviewSelect>>', select)

    # table.config(columns=[col for col in mini_header2config], show='headings')
    # for i, col in enumerate(mini_header2config):
    #     table.heading(i, text=col, command=lambda _col=col: _sort(table, _col, False))
    #     table.column(i, width=80, stretch=Tk.NO)
    # if config.analysis_mode == 'mini':
    # define_columns([col for col in mini_header2config])

    global selected
    selected = table.selection()

    # table.show_columns = show_columns
    # table.fit_columns = fit_columns

    vsb = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=table.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(frame, orient=Tk.HORIZONTAL, command=table.xview)
    hsb.grid(column=0, row=1, sticky='ew')
    table.configure(xscrollcommand=hsb.set)
    return frame

def add(data):
    table.insert("", 'end', iid=data.get('t', None), values=[data.get(i, None) for i in mini_header2config])
    unselect()

def append(data):
    # data is dataframe
    for i in data.index:
        try:
            table.insert("", 'end', iid=i, values=[data.loc[i][k] for k in mini_header2config])
        except:
            pass

def show_columns():
    if pymini.widgets['analysis_mode'].get() == 'mini':
        table.config(displaycolumns=tuple([
            i for i in mini_header2config
            if pymini.widgets[mini_header2config[i]].get()
        ]))
    else:
        pass


def fit_columns():
    print(table.tk)
    indices = headers
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
    selected = table.selection()
    if len(selected) == 1:
        interface.select_single_mini(float(selected[0]))
    if pymini.widgets['analysis_mode'].get() == 'mini':
        interface.highlight_selected_mini([float(i) for i in selected])
    try:
        table.see(selected[0])
    except:
        pass


def unselect(e=None):
    table.selection_remove(*table.selection())


def select_one(iid):
    table.see(str(iid))
    interface.highlight_selected_mini([float(iid)])
    print(selected)
    if selected == (str(iid),):
        return
    table.selection_set(str(iid))
    print(selected)

def toggle_one(iid):
    if interpreter.multi_select:
        table.selection_toggle(str(iid))
        table.see(str(iid))
        return
    table.selection_set(iid)
    table.see(str(iid))

def delete_one(iid):
    try:
        table.selection_remove(str(iid))
    except:
        pass
    interface.delete_event([iid])
    table.delete(str(iid))
