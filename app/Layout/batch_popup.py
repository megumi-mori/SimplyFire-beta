import tkinter as Tk
from tkinter import ttk
import pymini
from utils.widget import DataTable

def load():
    try:
        window.deiconify()
        print('recalling window')
    except:
        create_window()

def create_window():
    global window
    window = Tk.Toplevel(pymini.root)
    window.geometry('400x400')
    pymini.root.attributes('-disabled', True)
    window.focus_set()
    window.protocol('WM_DELETE_WINDOW', _on_close)


    #######################################
    # Populate batch processing window
    #######################################
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_rowconfigure(0, weight=1)
    operation_frame = Tk.Frame(window)
    operation_frame.grid(row=0, column=0, sticky='news')

    protocol_frame = Tk.Frame(window, bg='blue')
    protocol_frame.grid(row=0, column=1, sticky='news')
    protocol_frame.grid_columnconfigure(0, weight=1)
    protocol_frame.grid_rowconfigure(0, weight=1)
    protocol_table = DataTable(protocol_frame)
    protocol_table.grid(column=0, row=0, sticky='news')

    protocol_table.define_columns(['Protocol'], sort=False, iid_header=None, stretch=Tk.NO)

    file_frame = Tk.Frame(window)
    file_frame.grid(row=0, column=2, sticky='news')
    file_frame.grid_columnconfigure(0, weight=1)
    file_frame.grid_rowconfigure(0, weight=1)
    file_table = DataTable(file_frame)
    file_table.grid(column=0, row=0, sticky='news')

    file_table.define_columns(['Directory', 'Filename'], sort=False, iid_header=None, stretch=Tk.NO)
    window.update()
    protocol_table.fit_columns()
    file_table.fit_columns()





def _on_close(event=None):
    pymini.root.attributes('-disabled', False)
    window.withdraw()


