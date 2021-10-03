from utils.widget import DataTable
import tkinter as Tk

trace_header = [
    'sweep',
    'state'
]

def load(parent=None):
    global frame
    frame = Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    global datatable
    datatable = DataTable(frame)
    datatable.define_columns(tuple(trace_header))
    datatable.grid(column=0, row=0, sticky='news')

    return frame