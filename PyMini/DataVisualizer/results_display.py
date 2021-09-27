from utils.widget import DataTable
import tkinter as Tk
from tkinter import ttk

columns = ['filename', 'analysis','channel']

def load(parent):

    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global table_frame
    table_frame = DataTable(frame)
    table_frame.grid(row=0, column=0, sticky='news')

    global table
    table = table_frame.table

    table_frame.define_columns(tuple(columns), sort=False)

    button_frame=Tk.Frame(frame)
    button_frame.grid(row=1, column=0, sticky='news')

    ttk.Button(button_frame, text='clear data (keep columns)', command=table_frame.clear).grid(column=0, row=0)
    ttk.Button(button_frame, text='clear data (erase columns)', command=erase).grid(column=1, row=0)
    ttk.Button(button_frame, text='fit columns', command=table_frame.fit_columns).grid(column=2, row=0)

    return frame


def fit_columns():

    pass

def erase(event=None):
    table_frame.clear()
    table_frame.define_columns(tuple(columns), sort=False)