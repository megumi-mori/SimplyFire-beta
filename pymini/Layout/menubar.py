import tkinter as Tk
from tkinter import ttk, filedialog
from config import config
import pymini

def _setting_window(event=None):
    window = Tk.Toplevel()

    frame = Tk.Frame(window, bg='purple')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(frame)
    notebook.grid(column=0, row=0, sticky='news')

def open_trace():
    f = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files','*.*')])
    if f:
        pymini.plot_area.open_trace(f)

def load_menubar(parent):
    menubar = Tk.Menu(parent)
    # FILE
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open", command=open_trace)
    # file_menu.add_command(label='Close', command=pymini.plot_area.close)

    # options_menu = Tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label="Options", menu=options_menu)
    #
    # options_menu.add_command(label="Setting", command=_setting_window)

    view_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='View', menu=view_menu)

    view_menu.add_radiobutton(label='Continous', command=_continuous_mode)
    view_menu.add_radiobutton(label='Overlay', command=_overlay_mode)
    view_menu.invoke({'continuous':0,'overlay':1}[config.trace_mode])

    return menubar

def _continuous_mode():
    pymini.tabs['menu'].set_value('trace_mode', 'continuous')
    try:
        cur_id = pymini.cp_notebook.index(pymini.cp_notebook.select())
        tab_id=pymini.cp_notebook.index(pymini.tabs['sweep'])
        pymini.cp_notebook.forget(pymini.cp_notebook.index(pymini.tabs['sweep']))
        pymini.cp_notebook.insert(tab_id, pymini.tabs['detector'], text='Detector')
        pymini.cp_notebook.select(cur_id)
    except:
        pass

def _overlay_mode(e=None):
    pymini.tabs['menu'].set_value('trace_mode', 'overlay')
    try:
        cur_id = pymini.cp_notebook.index(pymini.cp_notebook.select())
        tab_id = pymini.cp_notebook.index(pymini.tabs['detector'])
        pymini.cp_notebook.forget(pymini.cp_notebook.index(pymini.tabs['detector']))
        pymini.cp_notebook.insert(tab_id, pymini.tabs['sweep'], text='Sweep')
        pymini.cp_notebook.select(cur_id)
    except:
        pass





