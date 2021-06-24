# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog

def open_trace():
    f = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    if f:
        pymini.trace_filename = f
        print(f)

def configure(key, value):
    globals()[key] = value

def search_event_from_click(x):

    pass


