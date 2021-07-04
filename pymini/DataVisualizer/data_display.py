import tkinter as Tk
from tkinter import ttk
from DataVisualizer import trace_display
# from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict  # Python 3.7+ can use dict
import pymini
from Backend import interface
from config import config
from Layout import graph_panel


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


def stop(e=None):
    global press
    press = False
    global turbo
    turbo = False
    pymini.root.after_cancel(jobid)
    trace_display.update_x_scrollbar()
    trace_display.update_y_scrollbar()

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
    table.bind('q', unselect)
    table.bind('o', unselect)
    table.bind('<Delete>', delete_selected)
    table.bind('<BackSpace>', delete_selected)
    table.bind('e', delete_selected)
    table.bind('u', delete_selected)
    table.bind('<Control-a>', select_all)

    # focus is almost always on data_display - navigation keys for trace_display

    def scroll_x(dir):
        global press
        if not press:
            scroll_x_repeat(
                dir * int(pymini.widgets['navigation_mirror_x_scroll'].get()),
                int(pymini.widgets['navigation_fps'].get()),
                float(pymini.widgets['navigation_scroll_percent'].get())
            )
        press = True
    def scroll_y(dir):
        global press
        if not press:
            scroll_y_repeat(
                dir * int(pymini.widgets['navigation_mirror_y_scroll'].get()),
                int(pymini.widgets['navigation_fps'].get()),
                float(pymini.widgets['navigation_scroll_percent'].get())
            )
        press = True
    def scroll_x_repeat(dir, fps, percent):
        global jobid
        jobid = pymini.root.after(int(1000 / fps), scroll_x_repeat, dir, fps, percent)
        if turbo:
            trace_display.scroll_x_by(dir * 2, percent)
        else:
            trace_display.scroll_x_by(dir, percent)
        pass

    def scroll_y_repeat(dir, fps, percent):
        global jobid
        jobid = pymini.root.after(int(1000 / fps), scroll_y_repeat, dir, fps, percent)
        if turbo:
            trace_display.scroll_y_by(dir*2, percent)
        else:
            trace_display.scroll_y_by(dir, percent)
        pass

    def do_turbo(e=None):
        global turbo
        turbo = True

    def remove_turbo(e=None):
        global turbo
        turbo = False

    global press
    press = False
    global turbo
    turbo = False

    table.bind('<Shift_L>', do_turbo, add='+')
    table.bind('<KeyRelease-Shift_L>', remove_turbo, add="+")
    table.bind('<Shift_R>', do_turbo, add='+')
    table.bind('<KeyRelease-Shift_R>', remove_turbo, add="+")

    for k in config.pan_left:
        table.bind(k, lambda e, d=-1:scroll_x(d))
        table.bind(k.upper(), lambda e, d=-1: scroll_x(d))
        table.bind('<KeyRelease-{}>'.format(k), stop)
        table.bind('<KeyRelease-{}>'.format(k.upper()), stop)

    for k in config.pan_right:
        table.bind(k, lambda e, d=1:scroll_x(d))
        table.bind(k.upper(), lambda e, d=2: scroll_x(d))
        table.bind('<KeyRelease-{}>'.format(k), stop)
        table.bind('<KeyRelease-{}>'.format(k.upper()), stop)

    for k in config.pan_up:
        table.bind(k, lambda e, d=1:scroll_y(d))
        table.bind(k.upper(), lambda e, d=2: scroll_y(d))
        table.bind('<KeyRelease-{}>'.format(k), stop)
        table.bind('<KeyRelease-{}>'.format(k.upper()), stop)

    for k in config.pan_down:
        table.bind(k, lambda e, d=-1:scroll_y(d))
        table.bind(k.upper(), lambda e, d=-2: scroll_y(d))
        table.bind('<KeyRelease-{}>'.format(k), stop)
        table.bind('<KeyRelease-{}>'.format(k.upper()), stop)
    # for k in config.pan_up:
    #     table.bind('<Key-{}>'.format(k), lambda e, d=1, p=25: scroll_y_by(d, p))
    #     table.bind('<Key-{}>'.format(k.upper()), lambda e, d=1, p=100: scroll_y_by(d, p))
    #     table.bind('<KeyRelease-{}>'.format(k), stop)
    #     table.bind('<KeyRelease-{}>'.format(k.upper()), stop)
    #
    # for k in config.pan_down:
    #     table.bind('<Key-{}>'.format(k), lambda e, d=-1, p=25: scroll_y_by(d, p))
    #     table.bind('<Key-{}>'.format(k.upper()), lambda e, d=-1, p=100: scroll_y_by(d, p))
    #     table.bind('<KeyRelease-{}>'.format(k), stop)
    #     table.bind('<KeyRelease-{}>'.format(k.upper()), stop)

    # table.bind('<KeyRelease-a>', lambda e, d=-1, p=100:scroll_x_by(d, p))
    # table.bind('<KeyRelease-j>', lambda e, d=-1, p=100: scroll_x_by(d, p))
    # table.bind('<KeyRelease-d>', lambda e, d=1, p=100: scroll_x_by(d, p))
    # table.bind('<KeyRelease-l>', lambda e, d=1, p=100: scroll_x_by(d, p))
    # table.bind('<KeyRelease-w>', lambda e, d=1, p=10: scroll_y_by(d, p))
    # table.bind('<KeyRelease-i>', lambda e, d=1, p=10: scroll_y_by(d, p))
    # table.bind('<KeyRelease-s>', lambda e, d=-1, p=10: scroll_y_by(d, p))
    # table.bind('<KeyRelease-k>', lambda e, d=-1, p=10: scroll_y_by(d, p))



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

def navigate_list(idx):
    if len(table.selection()) == 0:
        select_one(table.get_children()[idx])

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
    print('selected: {}, temp: {}'.format(selected, temp))
    if len(temp) > 0 and selected == temp:
        print('toggling')
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
    table.selection_remove(*table.selection())

def select_all(e=None):
    global selected
    if len(selected) == len(table.get_children()):
        return
    table.selection_set(table.get_children())

def select_one(iid):
    table.see(str(iid))
    interface.highlight_selected([float(iid)])
    print(selected)
    if selected == (str(iid),):
        return
    table.selection_set(str(iid))
    print(selected)

def select_one_by_index(idx):
    select_one(table.get_children()[idx])

def toggle_one(iid):
    table.selection_set(iid)
    table.see(str(iid))

def delete_one(iid):
    try:
        table.selection_remove(str(iid))
    except:
        pass
    interface.delete_event([iid])
    table.delete(str(iid))

def delete_selected(e=None):
    sel = table.selection()
    table.selection_remove(*sel)
    interface.delete_event([i for i in sel])
    table.update()
    try:
        table.selection_set(table.next(sel[-1]))
    except Exception as e:
        pass
    table.delete(*sel)

