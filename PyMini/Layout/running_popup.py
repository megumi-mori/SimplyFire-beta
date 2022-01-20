import tkinter as Tk
from tkinter import ttk
from PyMini import app
from PyMini.Backend import interface

def load(process=''):
    global current_process
    current_process = process
    try:
        window_reload()

    except:
        # window not yet created
        window_create()

    window.lift()
    window.focus_set()
    window.protocol('WM_DELETE_WINDOW', disable)
    app.root.attributes('-disabled', True)

def disable():
    pass

def stop(event=None):
    stop_button.configure(state='disabled')
    interface.interrupt(current_process)

def window_reload():
    global stop_button
    stop_button.configure(state='normal')
    global window
    window.deiconify()

def window_close(event=None):
    global current_process
    current_process = ''
    app.root.attributes('-disabled', False)
    window.withdraw()

def window_create():
    global window
    window = Tk.Toplevel(app.root)
    # window.geometry('200x100')

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    frame = Tk.Frame(window)
    frame.grid(column=0, row=0, sticky='news')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    global label
    label = ttk.Label(master=frame, text='Running analysis... This window will close automatically.\n Press STOP to stop the process')
    label.grid(column=0, row=0, sticky='news')

    global stop_button
    stop_button = ttk.Button(master=frame, text='STOP', command=stop)
    stop_button.grid(column=0, row=1, sticky='news')

def _on_close(event=None):
    app.root.attributes('-disabled', False)
    window.withdraw()