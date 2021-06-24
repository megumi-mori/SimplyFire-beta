import tkinter as Tk
from tkinter import ttk
from config import config

def load(parent):
    frame = Tk.Frame(parent, bg='red')
    frame.grid_columnconfigure(0, weight=1)
    label = ttk.Label(frame,text="Font Size")
    label.grid(column=0, row=0, sticky='news')
    w = ttk.Scale(
        frame,
        from_=9,
        to_=20,
        command=lambda e: config.set_fontsize(int(float(e))))
    w.grid(column=0, row=1, sticky='news')
    # config.change_fontsize(e))
    return frame



