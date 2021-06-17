import tkinter as Tk
from tkinter import ttk
from config import config
import pymini

def _setting_window(event=None):
    window = Tk.Toplevel()

    frame = Tk.Frame(window, bg='purple')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(frame)
    notebook.grid(column=0, row=0, sticky='news')

def load_menubar(parent):
    menubar = Tk.Menu(parent)
    # FILE
    file_menu = Tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=pymini.open_trace)

    menubar.add_cascade(label='File', menu=file_menu)

    options_menu = Tk.Menu(menubar, tearoff=0)
    options_menu.add_command(label="Setting", command=_setting_window)

    menubar.add_cascade(label="Options", menu=options_menu)

    return menubar





