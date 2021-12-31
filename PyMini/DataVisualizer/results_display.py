from utils.widget import DataTable
import tkinter as Tk
from tkinter import ttk

default_columns = ['filename', 'analysis','channel']

def load(parent):

    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global dataframe
    dataframe = DataTable(frame)
    dataframe.grid(row=0, column=0, sticky='news')

    global table
    table = dataframe.table

    dataframe.define_columns(tuple(default_columns), sort=False)

    button_frame=Tk.Frame(frame)
    button_frame.grid(row=1, column=0, sticky='news')

    ttk.Button(button_frame, text='clear data (keep columns)', command=dataframe.clear).grid(column=0, row=0)
    ttk.Button(button_frame, text='Reset columns', command=erase).grid(column=1, row=0)
    ttk.Button(button_frame, text='Fit columns', command=dataframe.fit_columns).grid(column=2, row=0)

    dataframe.menu.add_command(label='Copy selection (Ctrl+c)', command=dataframe.copy)
    dataframe.menu.add_command(label='Select all (Ctrl+a)', command=dataframe.select_all)
    dataframe.menu.add_command(label='Delete (Del)', command = delete_selected)
    dataframe.menu.add_separator()
    dataframe.menu.add_command(label='Clear data', command=dataframe.clear)
    dataframe.menu.add_command(label='Reset columns', command=erase)
    dataframe.menu.add_command(label='Fit columns', command=dataframe.fit_columns)
    return frame

def erase(event=None):
    dataframe.clear()
    dataframe.define_columns(tuple(default_columns), sort=False)

def delete_selected(e=None):
    dataframe.delete_selected()
    # if len(dataframe.table.get_children()) == 0:
    #     dataframe.menu.entryconfig(0, state=Tk.DISABLED)