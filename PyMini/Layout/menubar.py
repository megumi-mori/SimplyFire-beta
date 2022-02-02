import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os
from PyMini.config import config
from PyMini.utils.custom_widgets import VarWidget
from PyMini.Backend import interface
from PyMini.DataVisualizer import param_guide, data_display, trace_display, evoked_data_display, results_display
import gc
from PyMini import app
# from PyMini.Layout import keybind_popup

import time
def load(menubar):
    global widgets
    widgets = {}
    global trace_mode
    trace_mode = 'continuous'

    parent=menubar.master

    ##################################
    # add menu bar commands here
    ##################################

    # File menu
    global file_menu
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open recording \t Ctrl+o", command=ask_open_recording)
    file_menu.add_command(label='Save recording data as...', command=ask_save_recording)
    file_menu.add_separator()

    file_menu.add_separator()
    file_menu.add_command(label='Export plot', command=ask_save_plot)
    # file_menu.add_command(label='Export mini analysis table', command=export_events)
    # file_menu.add_command(label='Export evoked analysis table', command=export_evoked)
    file_menu.add_command(label='Export results table', command=export_results)
    file_menu.add_separator()

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
    view_menu.add_radiobutton(label='Continuous', command=set_view_continuous, variable=trace_var,
                              value='continuous')
    view_menu.add_radiobutton(label='Overlay', command=set_view_overlay, variable=trace_var, value='overlay')

    # Window menu
    global window_menu
    window_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Window', menu=window_menu)
    widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    if widgets['window_param_guide'].get() == '1':
        window_menu.invoke(window_menu.index('Parameter-guide'))

    global settings_menu
    settings_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Settings', menu=settings_menu)


    # widgets['analysis_mode'].set(config.analysis_mode)
    widgets['trace_mode'].set(config.trace_mode)
    view_menu.invoke({'continuous': 0, 'overlay': 1, 'compare':2}[config.trace_mode])
    # analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])

    undo_disable()
    return menubar

def ask_open_recording():
    gc.collect()
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    app.root.update()
    if not fname:
        return None
    interface.open_recording(fname)
    # app.compare_tab.start_msg.grid_forget()
    interface.focus()
    return fname

def ask_save_plot(e=None):
    app.trace_display.canvas.toolbar.save_figure()

def ask_save_recording(e=None, save_events=True):
    if len(interface.recordings)==0:
        messagebox.showerror(title='Error', message='No recording to export. Please open a recording first.')
        return None
    save = False
    if save is not None:
        initialfname = os.path.splitext(interface.recordings[0].filename)[0] + '_Modified'
        try:
            filename = filedialog.asksaveasfilename(filetype=[('abf files', '*.abf'), ('All files', '*.*')],
                                                    defaultextension='.abf',
                                                    initialfile=initialfname)
            if filename:
                interface.save_recording(filename)
                interface.open_recording(filename, xlim=app.trace_display.ax.get_xlim(),
                             ylim=app.trace_display.ax.get_ylim()) #move this to interface?
        except (FileExistsError):
            messagebox.showerror(title='Error', message='ABF files cannot be overwritten. Please choose another filename.')
            ask_save_recording(save_events=False)

def export_evoked():
    if len(interface.recordings) == 0:
        messagebox.showerror(title='Save error', message='Please open a trace to analyze first')
        return None
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                            defaultextension='.csv',
                                            initialfile=interface.recordings[0].filename.split('.')[
                                                            0] + '_evoked.csv')
    evoked_data_display.dataframe.export(filename)


def export_results():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                            defaultextension='.csv',
                                            initialfile='results.csv')
    if filename:
        results_display.dataframe.export(filename)

def set_view_continuous(save_undo=True):
    global trace_mode
    global widgets
    app.root.event_generate('<<ContinuousView>>')
    # if save_undo and trace_mode == 'overlay':
    #     interface.add_undo([
    #         lambda s=False: set_view_overlay(s),
    #     ])
    # elif save_undo and trace_mode == 'compare':
    #     interface.add_undo([
    #         lambda s=False: set_view_compare(s)
    #     ])
    widgets['trace_mode'].set('continuous')

    # switch to continuous mode tab
    # interface.config_cp_tab('continuous', state='normal')

    try:
        # interface.plot_continuous(interface.recordings[0], fix_axis=True)
        interface.plot()
    except:
        pass
    # if widgets['analysis_mode'].get() == 'mini':
    #     interface.config_cp_tab('mini', state='normal')
    #     interface.config_data_tab('mini', state='normal')
    # interface.config_cp_tab('adjust', state='normal')
    trace_mode = 'continuous'
    pass

def set_view_overlay(save_undo=True):
    global trace_mode
    global widgets
    app.root.event_generate('<<OverlayView>>')
    # if save_undo and trace_mode == 'continuous':
    #     interface.add_undo([
    #         lambda d=False: set_view_continuous(d)
    #     ])
    # elif save_undo and trace_mode == 'compare':
    #     interface.add_undo([
    #         lambda d=False: set_view_compare(d)
    #     ])
    widgets['trace_mode'].set('overlay')
    # interface.config_cp_tab('overlay', state='normal')
    try:
        interface.plot()
    except:
        pass
    # if widgets['analysis_mode'].get() == 'mini':
    #     interface.config_cp_tab('mini', state='disabled')
    #     interface.config_data_tab('mini', state='disabled')
    # interface.config_cp_tab('adjust',state='normal')
    trace_mode = 'overlay'
    pass

def undo_disable():
    global edit_menu
    edit_menu.entryconfig(0, state='disabled')

def undo_enable():
    global edit_menu
    edit_menu.entryconfig(0, state='normal')

def make_file_menu_cascade(label):
    cascade = Tk.Menu(file_menu, tearoff=0)
    file_menu.add_cascade(label=label, menu=cascade)
    return cascade
