# takes input from the Data Visualizers and takes appropriate action
import pymini
from tkinter import filedialog
from DataVisualizer import data_display

def open_trace():
    f = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    if f:
        pymini.trace_filename = f
        print(f)
    data_display.clear()

def configure(key, value):
    globals()[key] = value

def search_event_from_click(x):

    pass


