from utils.widget import DataTable
import tkinter as Tk
from Backend import interface

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
    return frame

def fit_columns():
    print('fit columns evoked ')
    dataframe.fit_columns()

def clear():
    dataframe.clear()
    # dataframe.menu.entryconfig('Report statistics', state=Tk.DISABLED)

def delete_selected():
    selection = dataframe.table.selection()
    dataframe.table.selection_remove(*selection)
    dataframe.table.delete(*selection)
    # if len(dataframe.table.get_children()) == 0:
    #     dataframe.menu.entryconfig('Report statistics', state=Tk.DISABLED)

def add(data):
    dataframe.add(data)
    # dataframe.menu.entryconfig('Report statistics', state=Tk.NORMAL)

def append(data):
    dataframe.append(data)
    # if data.shape[0]>0:
    #     dataframe.menu.entryconfig('Report statistics', state=Tk.NORMAL)

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

