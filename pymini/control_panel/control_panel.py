import tkinter as Tk
from tkinter import ttk
from control_panel import detector

from utils import scrollable_frame
notebook = None
print('control panel loaded')
def load(parent):
    frame = Tk.Frame(parent, bg='purple')
    frame.grid_columnconfigure(0, weight =1)
    frame.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(frame)
    notebook.grid(column=0, row=0, sticky='news')
    tabs={}
    tabs['detector'] = detector.Detector(frame)

    # notebook.add(tabs['detector'].get_frame(), text='Mini')
    notebook.add(tabs['detector'].get_frame(), text='Mini')
    # notebook.add(detector.load(notebook), text='Detector')

    # sf = scrollable_frame.ScrollableFrame(frame)
    # notebook.add(sf.container, text='test')
    return frame, tabs

def update_width(fontsize):
    detector.update_width(fontsize)