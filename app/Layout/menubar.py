import tkinter as Tk
from tkinter import ttk, filedialog
from config import config
import pymini
from utils.widget import VarWidget
from Backend import interface
from DataVisualizer import param_guide
import gc

def _setting_window(event=None):
    window = Tk.Toplevel()

    frame = Tk.Frame(window, bg='purple')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(frame)
    notebook.grid(column=0, row=0, sticky='news')

def _show_param_guide(event=None):
    try:
        if pymini.widgets['window_param_guide'].get() == '1':
            pass
        else:
            pymini.widgets['window_param_guide'].set('1')
            param_guide.load()
    except:
        param_guide.load()

def ask_open_trace():
    gc.collect()
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    if fname:
        pymini.trace_filename = fname
    else:
        return None

    interface.open_trace(fname)

def save_events():
    if not pymini.event_filename:
        save_events_as()
        return
    interface.save_events(pymini.event_filename)

def save_events_as():
    filename = filedialog.asksaveasfilename(filetypes=[('event files', '*.event'), ('All files', '*.*')], defaultextension='.csv')
    if filename:
        interface.save_events(filename)
        return
    return

def open_events():
    filename = filedialog.askopenfilename(filetypes=[('event files', '*.event'), ("All files", '*.*')])
    if filename:
        interface.open_events(filename)
        return
    return

def export_events():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")])
    if filename:
        interface.export_events(filename)
        return
    return

def load_menubar(parent):
    menubar = Tk.Menu(parent)
    # FILE
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open trace", command=ask_open_trace)
    file_menu.add_separator()
    file_menu.add_command(label='Open event file', command=open_events)
    file_menu.add_command(label='Save event file', command=save_events)
    file_menu.add_command(label='Save event file as...', command=save_events_as)
    file_menu.add_separator()
    file_menu.add_command(label='Export events', command=export_events)
    # file_menu.add_command(label='Close', command=pymini.plot_area.close)

    # options_menu = Tk.Menu(menubar, tearoff=0)
    # menubar.add_cascade(label="Options", menu=options_menu)
    #
    # options_menu.add_command(label="Setting", command=_setting_window)

    view_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='View', menu=view_menu)
    trace_var = Tk.StringVar(parent, 0)
    pymini.widgets['trace_mode'] = trace_var
    view_menu.add_radiobutton(label='Continous', command=_continuous_mode, variable=trace_var, value='continuous')
    view_menu.add_radiobutton(label='Overlay', command=_overlay_mode, variable=trace_var, value='overlay')
    view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
    view_menu.add_separator()
    pymini.widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    view_menu.add_command(label='Show parameter-guide', command=_show_param_guide)

    analysis_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Analysis', menu=analysis_menu)
    analysis_var = Tk.StringVar(parent, 0)
    pymini.widgets['analysis_mode'] = analysis_var
    analysis_menu.add_radiobutton(label='Mini', command=_mini_mode, variable=analysis_var, value='mini')
    analysis_menu.add_radiobutton(label='Evoked', command=_evoked_mode, variable=analysis_var, value='evoked')
    analysis_menu.invoke({'mini':0, 'evoked':1}[config.analysis_mode])
    print(analysis_var.get())
    # try:
    #     analysis_menu.invoke({'mini':0, 'evoked':1}[config.analysis_mode])
    # except:
    #     analysis_menu.invoke(0)
    # analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])

    if pymini.widgets['window_param_guide'].get() == '1':
        param_guide.load()



    return menubar

def _continuous_mode():
    pymini.widgets['trace_mode'].set('continuous')
    try:
        pymini.cp_notebook.forget(pymini.cp_notebook.index(pymini.tabs['sweep_tab']))
        interface.plot_continuous(fix_axis=True)
        pymini.cp_notebook.tab(pymini.cp_notebook.index(pymini.tabs['detector_tab']), state='normal')
        pass
    except:
        pass

def _overlay_mode(e=None):
    pymini.widgets['trace_mode'].set('overlay')
    try:
        pymini.cp_notebook.insert(1, pymini.tabs['sweep_tab'], text='Sweep')
        interface.plot_overlay(fix_axis=True)
        pymini.cp_notebook.tab(pymini.cp_notebook.index(pymini.tabs['detector_tab']), state='disabled')
    except Exception as e:
        print(e)
        pass


def _mini_mode(e=None):
    pymini.widgets['analysis_mode'].set('mini')
    try:
        pymini.cp_notebook.insert(0, pymini.tabs['detector_tab'], text='Mini')
        if pymini.widgets['trace_mode'].get() != 'continuous':
            pymini.cp_notebook.tab(pymini.cp_notebook.index(pymini.tabs['detector_tab']), state='disabled')
    except:
        pass

def _evoked_mode(e=None):
    pymini.widgets['analysis_mode'].set('evoked')
    try:
        pymini.cp_notebook.forget(pymini.cp_notebook.index(pymini.tabs['detector_tab']))
    except:
        pass


