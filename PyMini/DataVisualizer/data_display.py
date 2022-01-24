import tkinter
import tkinter as Tk
from tkinter import ttk
from collections import OrderedDict  # Python 3.7+ can use dict
from PyMini import app
from PyMini.Backend import interface, interpreter
from PyMini.Layout import detector_tab
from PyMini.utils.widget import DataTable
from PyMini.DataVisualizer import results_display, param_guide
from PyMini.config import config



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
    ('stdev', 'data_display_std'),
    ('stdev_unit', 'data_display_std'),
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

    for key in config.key_delete:
        table.bind(key, delete_selected, add=None)

    dataframe.table.bind('<<TreeviewSelect>>', select)
    dataframe.define_columns(tuple([key for key in mini_header2config]), iid_header='t')
    dataframe.grid(column=0, row=0, sticky='news')

    dataframe.menu.add_command(label='Copy selection (Ctrl+c)', command=dataframe.copy)
    dataframe.menu.add_command(label='Select all (Ctrl+a)', command=dataframe.select_all)
    dataframe.menu.add_command(label='Delete selected (Del)', command=delete_selected)
    dataframe.menu.add_separator()
    dataframe.menu.add_command(label='Clear data', command=interface.delete_all_events)
    dataframe.menu.add_command(label='Report stats', command=report, state=Tk.DISABLED)
    dataframe.menu.add_command(label='Fit columns', command=dataframe.fit_columns)

    table.bind('<Up>', select_prev)
    table.bind('<Down>', select_next)
    return frame

def add(data, index='end'):
    interface.config_data_tab('mini', state='disabled')
    dataframe.add(data, index=index)
    dataframe.menu.entryconfig('Report stats', state=Tk.NORMAL)
    detector_tab.report_button.config(state='normal')
    detector_tab.report_button2.config(state='normal')
    global saved
    saved = False
    interface.config_data_tab('mini', state='normal')
    # detector_tab.filter_all_button.config(state='normal')
    # detector_tab.filter_in_window_button.config(state='normal')

def append(data):
    # app.data_notebook.tab(app.data_tab_details['mini']['tab'], state='disabled')
    interface.config_data_tab('mini', state='disabled')
    try:
        dataframe.append(data)
    except Exception as e:
        print(f'data_display append error: {e}')
    interface.config_data_tab('mini', state='normal')
    # app.data_notebook.tab(app.data_tab_details['mini']['tab'], state='normal')
    if data.shape[0]>0:
        dataframe.menu.entryconfig('Report stats', state=Tk.NORMAL)
        detector_tab.report_button.config(state='normal')
        detector_tab.report_button2.config(state='normal')
        # detector_tab.filter_all_button.config(state='normal')
        # detector_tab.filter_in_window_button.config(state='normal')
    global saved
    saved = False


def set(data):
    dataframe.clear()
    append(data)
        # detector_tab.filter_all_button.config(state='normal')
        # detector_tab.filter_in_window_button.config(state='normal')
    global saved
    saved = False



def show_columns(columns=None):
    global dataframe
    columns = tuple([
       i for i in mini_header2config
        if mini_header2config[i] in columns
    ])
    dataframe.show_columns(columns)
    dataframe.columns=columns
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
    dataframe.menu.entryconfig('Report stats', state=Tk.DISABLED)
    detector_tab.report_button.config(state='disabled')
    detector_tab.report_button2.config(state='disabled')
    # detector_tab.filter_all_button.config(state='disabled')
    # detector_tab.filter_in_window_button.config(state='disabled')
    global saved
    saved = False

def delete_selected(e=None):
    if app.widgets['analysis_mode'].get() == 'mini':
        sel = dataframe.table.selection()
        interface.delete_event([i for i in sel])
    global saved
    saved = False


def hide():
    dataframe.hide()

def select(e=None):
    selected = table.selection()
    if len(selected)>0:
        table.see(selected[0])
    if app.widgets['analysis_mode'].get() == 'mini':
        if len(selected) == 1:
            interface.select_single_mini(float(selected[0]))
        interface.highlight_selected_mini([float(i) for i in selected])


def select_next(e=None):
    if len(table.get_children()) == 0:
        return None
    selection = table.selection()
    if len(selection)>0:
        if table.next(selection[-1]):
            table.selection_set(table.next(selection[-1]))
            return None
    table.selection_set(table.get_children()[0])

def select_prev(e=None):
    if len(table.get_children()) == 0:
        return None
    selection = table.selection()
    if len(selection) > 0:
        if table.prev(selection[0]) != "":
            table.selection_set(table.prev(selection[0]))
            return None
    table.selection_set(table.get_children()[-1])
def unselect(e=None):
    dataframe.unselect()
    try:
        param_guide.clear()
    except Exception as e:
        print(f'data_display unselect error {e}')
        pass


# def select_one(iid):
#     raise
#     interface.highlight_selected_mini([float(iid)])
#     dataframe.select(iid)

def delete_one(iid):
    print('data_Display delete one: {}'.format(iid))
    try:
        # dataframe.delete([iid])
        interface.delete_event([iid])
    except Exception as e:
        print('data_display delete one error: {}'.format(e))
        pass
    global saved
    saved = False

def delete(selection):
    global table
    table.selection_remove(*selection)
    table.delete(*selection)
    if len(dataframe.table.get_children()) == 0:
        dataframe.menu.entryconfig('Report stats', state=Tk.DISABLED)
        detector_tab.report_button.config(state='disabled')
        detector_tab.report_button2.config(state='disabled')
        # detector_tab.filter_all_button.config(state='disabled')
        # detector_tab.filter_in_window_button.config(state='disabled')
    global saved
    saved = False

def report(event=None):
    global table
    if len(table.get_children())==0:
        results_display.dataframe.add({
            'filename':interface.recordings[0].filename,
            'analysis': 'mini',
            'num_minis': 0,
        })
        return None
    mini_df = interface.mini_df[interface.mini_df['channel']==interface.recordings[0].channel]
    if mini_df.shape[0] == 0:
        return None
    data = {
        'filename': interface.recordings[0].filename,
        'analysis': 'mini',
        'num_minis': mini_df.shape[0]
    }
    if 'amp' in dataframe.columns:
        data['amp'] = mini_df['amp'].mean()
        data['amp_unit']= mini_df['amp_unit'].iloc[0]
        data['amp_std']= mini_df['amp'].std()
    if 'decay_const' in dataframe.columns:
        data['decay_const'] = mini_df['decay_const'].mean()
        data['decay_unit'] = mini_df['decay_unit'].iloc[0]
        data['decay_std'] = mini_df['decay_const'].std()
    if 'rise_const' in dataframe.columns:
        data['rise_const'] = mini_df['rise_const'].mean()
        data['rise_unit'] = mini_df['rise_unit'].iloc[0]
        data['decay_std'] = mini_df['rise_const'].std()
    if 'halfwidth' in dataframe.columns:
        data['halfwidth'] = mini_df['halfwidth'].mean()
        data['halfwidth_unit'] = mini_df['halfwidth_unit'].iloc[0]
        data['halfwidth_std'] = mini_df['halfwidth'].std()
    if 'baseline' in dataframe.columns:
        data['baseline'] = mini_df['baseline'].mean()
        data['baseline_unit'] = mini_df['baseline_unit'].iloc[0]
        data['baseline_std'] = mini_df['baseline'].std()
    if 'channel' in dataframe.columns:
        data['channel'] = interface.recordings[0].channel
    if 'compound' in dataframe.columns:
        data['num_compound'] = mini_df['compound'].sum()
    # calculate frequency
    data['Hz'] = interface.al.calculate_frequency(mini_df, interface.recordings[0].channel)


    results_display.dataframe.add(data)
