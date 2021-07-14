import tkinter as Tk
from tkinter import ttk, filedialog
from config import config
import pymini
from utils.widget import VarWidget
from Backend import interface
from DataVisualizer import param_guide, data_display, trace_display
from Layout import detector_tab
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
            param_guide.window.focus_set()
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

def ask_save_trace():
    gc.collect()
    fname = filedialog.asksaveasfilename(title='Save recording as', filetypes=[('abf files', '*.abf'),
                                                                               ('All files', '*.*')])
    if fname:
        interface.save_trace_as(fname)
        pass
    else:
        return None

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

    ##################################
    # add menu bar commands here
    ##################################

    # File menu
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open trace", command=ask_open_trace)
    file_menu.add_separator()
    file_menu.add_command(label='Open event file', command=open_events)
    file_menu.add_command(label='Save event file', command=save_events)
    file_menu.add_command(label='Save event file as...', command=save_events_as)
    file_menu.add_separator()
    file_menu.add_command(label='Export events', command=export_events)


    # View menu
    global view_menu
    view_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='View', menu=view_menu)
    # track trace_mode
    trace_var = Tk.StringVar(parent, 0)
    pymini.widgets['trace_mode'] = trace_var
    view_menu.add_radiobutton(label='Continous', command=_continuous_mode, variable=trace_var, value='continuous')
    view_menu.add_radiobutton(label='Overlay', command=_overlay_mode, variable=trace_var, value='overlay')

    # Analysis menu
    analysis_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Analysis', menu=analysis_menu)
    # track analysis_mode
    analysis_var = Tk.StringVar(parent, 0)
    pymini.widgets['analysis_mode'] = analysis_var
    analysis_menu.add_radiobutton(label='Mini', command=_mini_mode, variable=analysis_var, value='mini')
    analysis_menu.add_radiobutton(label='Evoked', command=_evoked_mode, variable=analysis_var, value='evoked')

    # Window menu
    window_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Window', menu=window_menu)
    pymini.widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    window_menu.add_command(label='Parameter-guide', command=_show_param_guide)
    if pymini.widgets['window_param_guide'].get() == '1':
        window_menu.invoke(window_menu.index('Parameter-guide'))

    view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
    analysis_menu.invoke({'mini':0, 'evoked':1}[config.analysis_mode])
    return menubar

def display_cp_tab(tab_name):
    # call this function if a menu command is associated with switching out tabs
    # indicate the partner of the tab in the pymini tab setting section
    idx = pymini.cp_notebook.index('current')
    # check if current tab would be replaced by the new tab being displayed
    if idx in [pymini.tab_details[tab]['index'] for tab in pymini.tab_details[tab_name]['partner']]:
        idx = pymini.tab_details[tab_name]['index']
    for partner in pymini.tab_details[tab_name]['partner']:
        pymini.cp_notebook.hide(pymini.tab_details[partner]['index'])
    pymini.cp_notebook.add(pymini.tab_details[tab_name]['tab'])
    pymini.cp_notebook.select(idx)


def _continuous_mode(save_undo=True):
    pymini.widgets['trace_mode'].set('continuous')
    display_cp_tab('continuous')
    try:
        interface.plot_continuous(fix_axis=True)
    except:
        pass
    if pymini.widgets['analysis_mode'].get() == 'mini':
        pymini.cp_notebook.tab(pymini.tab_details['mini']['index'], state='normal')
    if save_undo:
        interface.add_undo([
            lambda s=False:_continuous_mode(s),
        ])


def _overlay_mode(e=None):
    pymini.widgets['trace_mode'].set('overlay')
    display_cp_tab('overlay')
    try:
        interface.plot_overlay(fix_axis=True)
    except:
        pass
    if pymini.widgets['analysis_mode'].get() == 'mini':
        pymini.cp_notebook.tab(pymini.tab_details['mini']['index'], state='disabled')
    interface.add_undo(lambda i=0: view_menu.invoke(i))


def _mini_mode(e=None):
    pymini.widgets['analysis_mode'].set('mini')
    display_cp_tab('mini')
    if pymini.widgets['trace_mode'].get() != 'continuous':
        pymini.cp_notebook.tab(pymini.tab_details['mini']['index'], state='disabled')
    data_display.clear()
    detector_tab.populate_data_display()
    interface.update_event_marker()


def _evoked_mode(e=None):
    pymini.widgets['analysis_mode'].set('evoked')
    display_cp_tab('evoked')
    trace_display.clear_markers()
    data_display.clear()
    data_display.show_columns()


