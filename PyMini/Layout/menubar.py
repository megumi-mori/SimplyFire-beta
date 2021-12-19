import tkinter as Tk
from tkinter import ttk, filedialog
from config import config
from utils.widget import VarWidget
from Backend import interface
from DataVisualizer import param_guide, data_display, trace_display
from Layout import detector_tab, batch_popup
import gc
import app

# initialize variable
global trace_mode
trace_mode = 'continuous'

global widgets
widgets = {}

def _setting_window(event=None):
    """
    currently not in use, but use this function to create a pop-up option settings window
    """
    window = Tk.Toplevel()

    frame = Tk.Frame(window, bg='purple')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(frame)
    notebook.grid(column=0, row=0, sticky='news')

def _show_param_guide(event=None):
    try:
        if widgets['window_param_guide'].get() == '1':
            param_guide.window.focus_set()
            pass
        else:
            widgets['window_param_guide'].set('1')
            param_guide.load()
    except:
        param_guide.load()

def ask_open_trace():
    gc.collect()
    # first time filedialog is taking a while (even when canceling out of dialog)
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])

    if not fname:
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
    global widgets

    menubar = Tk.Menu(parent)

    ##################################
    # add menu bar commands here
    ##################################

    # File menu
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open trace \t Ctrl+o", command=ask_open_trace)
    file_menu.add_separator()
    file_menu.add_command(label='Open event file', command=open_events)
    file_menu.add_command(label='Save event file', command=interface.save_events_dialogue)
    file_menu.add_command(label='Save event file as...', command=interface.save_events_as_dialogue)
    file_menu.add_separator()
    file_menu.add_command(label='Export events', command=export_events)

    # Edit menu
    global edit_menu
    edit_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Edit', menu=edit_menu)
    edit_menu.add_command(label='Undo \t Ctrl+z', command=interface.undo, state='disabled')

    # View menu
    global view_menu
    view_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='View', menu=view_menu)
    # track trace_mode
    trace_var = Tk.StringVar(parent, 0)
    widgets['trace_mode'] = trace_var
    view_menu.add_radiobutton(label='Continous', command=_continuous_mode, variable=trace_var, value='continuous')
    view_menu.add_radiobutton(label='Overlay', command=_overlay_mode, variable=trace_var, value='overlay')

    # Analysis menu
    analysis_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Analysis', menu=analysis_menu)
    # track analysis_mode
    analysis_var = Tk.StringVar(parent, 0)
    widgets['analysis_mode'] = analysis_var
    analysis_menu.add_radiobutton(label='Mini', command=_mini_mode, variable=analysis_var, value='mini')
    analysis_menu.add_radiobutton(label='Evoked', command=_evoked_mode, variable=analysis_var, value='evoked')
    analysis_menu.add_separator()
    analysis_menu.add_command(label='Batch Processing', command=batch_popup.load)

    # Window menu
    window_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Window', menu=window_menu)
    widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    window_menu.add_command(label='Parameter-guide', command=_show_param_guide)
    if widgets['window_param_guide'].get() == '1':
        window_menu.invoke(window_menu.index('Parameter-guide'))

    view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
    analysis_menu.invoke({'mini':0, 'evoked':1}[config.analysis_mode])
    return menubar

def disable_undo():
    edit_menu.entryconfig(0, state='disabled')
def enable_undo():
    edit_menu.entryconfig(0, state='normal')

def _continuous_mode(save_undo=True):
    global trace_mode
    if save_undo and trace_mode == 'overlay':
        interface.add_undo([
            lambda s=False:_overlay_mode(s),
        ])
    widgets['trace_mode'].set('continuous')

    # switch to continuous mode tab
    interface.config_cp_tab('continuous', state='normal')

    try:
        interface.plot_continuous(fix_axis=True)
    except:
        pass
    if widgets['analysis_mode'].get() == 'mini':
        interface.config_cp_tab('mini', state='normal')
    trace_mode = 'continuous'


def _overlay_mode(save_undo=True):
    global trace_mode
    if save_undo and trace_mode == 'continuous':
        interface.add_undo([
            lambda d=False:_continuous_mode(d)
        ])
    widgets['trace_mode'].set('overlay')
    interface.config_cp_tab('overlay', state='normal')
    try:
        interface.plot_overlay(fix_axis=True)
    except:
        pass
    if widgets['analysis_mode'].get() == 'mini':
        interface.config_cp_tab('mini', state='disabled')
    trace_mode = 'overlay'

def _mini_mode(e=None):
    widgets['analysis_mode'].set('mini')
    interface.config_cp_tab('mini', state='normal')
    if widgets['trace_mode'].get() != 'continuous':
        interface.config_cp_tab('mini', state='disabled')
        pass
    interface.config_data_tab('mini', state='normal')
    interface.populate_data_display()
    interface.update_event_marker()


def _evoked_mode(e=None):
    widgets['analysis_mode'].set('evoked')
    interface.config_cp_tab('evoked', state='normal')
    interface.config_data_tab('evoked', state='normal')
    trace_display.clear_markers()


