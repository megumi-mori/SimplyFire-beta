import pandas
import numpy as np
from PyMini.utils.widget import DataTable
import tkinter as Tk
from PyMini.Backend import interface, analyzer2
from PyMini.DataVisualizer import results_display
from PyMini.Layout import evoked_tab

default_columns = [
    'sweep',
    'channel'
]

def load(parent=None):
    global frame
    frame = Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    global dataframe
    dataframe = DataTable(frame)
    dataframe.define_columns(tuple(default_columns))
    dataframe.grid(column=0, row=0, sticky='news')

    global table
    table = dataframe.table
    dataframe.set_iid('index')

    dataframe.menu.add_command(label='Copy selection (Ctrl+c)', command=dataframe.copy)
    dataframe.menu.add_command(label='Select all (Ctrl+a)', command=dataframe.select_all)
    dataframe.menu.add_command(label='Delete selected (Del)', command=delete_selected)
    dataframe.menu.add_separator()
    dataframe.menu.add_command(label='Clear data', command=dataframe.clear())
    dataframe.menu.add_command(label='Report stats', command=report, state=Tk.DISABLED)
    dataframe.menu.add_command(label='Fit columns', command=dataframe.fit_columns)
    return frame

def fit_columns():
    dataframe.fit_columns()

def clear():
    dataframe.clear()
    dataframe.menu.entryconfig('Report stats', state=Tk.DISABLED)
    evoked_tab.report_button.config(state='disabled')

def delete_selected():
    selection = dataframe.table.selection()
    dataframe.table.selection_remove(*selection)
    dataframe.table.delete(*selection)
    if len(dataframe.table.get_children()) == 0:
        dataframe.menu.entryconfig('Report stats', state=Tk.DISABLED)
        evoked_tab.report_button.config(state='disabled')

def add(data):
    dataframe.add(data)
    dataframe.menu.entryconfig('Report stats', state=Tk.NORMAL)
    evoked_tab.report_button.config(state='normal')

def append(data):
    dataframe.append(data)
    if data.shape[0]>0:
        dataframe.menu.entryconfig('Report stats', state=Tk.NORMAL)
        evoked_tab.report_button.config(state='normal')

def export_data(filename):
    global dataframe
    with open(filename, 'w') as f:
        items = dataframe.table.get_children()
        f.write(','.join(dataframe.columns))
        f.write('\n')
        for i in items:
            f.write(','.join(dataframe.table.item(i, 'values')))
            f.write('\n')
def reset():
    dataframe.clear()
    dataframe.define_columns(tuple(default_columns))


def clear():
    dataframe.clear()

def report(event=None):
    columns = dataframe.columns
    items = dataframe.table.get_children()
    df = {}
    # initiate dict
    # print(pandas.DataFrame.from_dict({'row1':{'col1':1, 'col2': 2}, 'row2':{'col1':3, 'col2':4}}, orient='index'))
    # make dataframe?
    for i in items:
        data = dataframe.table.set(i)
        for c in columns:
            if data[c] == 'None':
                data[c] = None
            elif c == 'sweep':
                data[c] = int(data[c])
            elif c == 'channel':
                data[c] == int(data[c])
            else:
                try:
                    data[c] = float(data[c])
                except:
                    pass
        df[i] = data
    if len(df) == 0:
        return None
    df = pandas.DataFrame.from_dict(df, orient='index')
    output = {'filename': interface.recordings[0].filename,
              'analysis': 'evoked'}
    for c in columns:
        if 'unit' in c:
            output[c] = summarize_column(df[c])
        elif 'sweep' in c:
            output[c] = analyzer2.format_list_indices(df[c])
        elif 'channels' in c:
            output[c] = analyzer2.format_list_indices(df[c])

        else:
            try:
                output[f'{c}_avg'] = average_column(df[c])
                output[f'{c}_std'] = std_column(df[c])
            except:
                output[c] = summarize_column(df[c])
    results_display.dataframe.add(output)


def summarize_column(data):
    output = []
    for d in data:
        if d is not None:
            if not d in output:
                output.append(d)
    return ','.join(output)

def average_column(data):
    return np.average(data)
    pass

def std_column(data):
    return np.std(data)
    pass

