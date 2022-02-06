import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os
from SimplyFire.config import config
from SimplyFire.utils.custom_widgets import VarWidget
from SimplyFire.utils import abfWriter
from SimplyFire.Backend import interface
from SimplyFire.DataVisualizer import trace_display, results_display
import gc
from SimplyFire import app
# from PyMini.Layout import keybind_popup
from SimplyFire.utils import formatting

import time
def load(menubar):
    global widgets
    widgets = {}
    global prev_trace_mode
    prev_trace_mode = config.trace_mode

    parent=menubar.master

    ##################################
    # add menu bar commands here
    ##################################

    # File menu
    global file_menu
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open recording \t Alt+o", command=ask_open_recording)
    file_menu.add_command(label='Save recording data as...', command=ask_save_recording)
    file_menu.add_separator()

    file_menu.add_command(label='Export plot', command=ask_save_plot)
    # file_menu.add_command(label='Export mini analysis table', command=export_events)
    # file_menu.add_command(label='Export evoked analysis table', command=export_evoked)
    file_menu.add_command(label='Export results table', command=ask_export_results)
    file_menu.add_separator()
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

    # Analysis menu
    global analysis_menu
    analysis_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Analysis', menu=analysis_menu)

    # Window menu
    global module_menu
    module_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Modules', menu=module_menu)
    widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    if widgets['window_param_guide'].get() == '1':
        module_menu.invoke(module_menu.index('Parameter-guide'))

    global settings_menu
    settings_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Settings', menu=settings_menu)


    # widgets['analysis_mode'].set(config.analysis_mode)
    widgets['trace_mode'].set(config.trace_mode)
    # view_menu.invoke({'continuous': 0, 'overlay': 1, 'compare':2}[config.trace_mode])
    # analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])

    undo_disable()
    return menubar

def ask_open_recording():
    gc.collect()
    app.root.event_generate('<<AskOpenRecording>>')
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    app.root.update()
    if not fname:
        return None
    interface.open_recording(fname)
    # app.compare_tab.start_msg.grid_forget()
    interface.focus()
    app.root.event_generate('<<AskedOpenRecording>>')
    return fname

def ask_save_plot(e=None):
    app.trace_display.canvas.toolbar.save_figure()

def ask_save_recording(e=None):
    if len(interface.recordings)==0:
        messagebox.showerror(title='Error', message='No recording to export. Please open a recording first.')
        return None
    app.root.event_generate('<<AskSaveRecording>>')
    initialfname = formatting.format_save_filename(os.path.splitext(interface.recordings[0].filename)[0] + '_Modified', False)
    filename = filedialog.asksaveasfilename(filetype=[('abf files', '*.abf'), ('All files', '*.*')],
                                            defaultextension='.abf',
                                            initialfile=initialfname)
    try:
        if filename:
            save_recording(filename)
    except (FileExistsError):
        messagebox.showerror(title='Error', message='ABF files cannot be overwritten. Please choose another filename.')
        ask_save_recording(save_events=False)
    app.root.event_generate('<<AskedSaveRecording>>')

def save_recording(filename):
    abfWriter.writeABF1(app.interface.recordings[0], filename)
    interface.open_recording(filename, xlim=app.trace_display.ax.get_xlim(),
                             ylim=app.trace_display.ax.get_ylim(),
                             channel=app.interface.current_channel)

def ask_export_results():
    app.root.event_generate('<<AskExportResults>>')
    if len(app.results_display.dataframe.get_children()) == 0:
        answer = messagebox.askyesno('Warning', 'No entries in results table. Proceed?')
        if answer:
            filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                                    defaultextension='.csv',
                                                    initialfile='results.csv')
            if filename:
                results_display.dataframe.export(filename)
    app.root.event_generate('<<AskedExportResults>>')
def set_view_continuous(save_undo=True):
    global widgets
    global prev_trace_mode
    if prev_trace_mode == 'continuous':
        print('stays in continuous')
        return
    app.root.event_generate('<<ChangeToContinuousView>>')
    if save_undo and prev_trace_mode == 'overlay':
        interface.add_undo([
            lambda s=False: set_view_overlay(s),
        ])
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
    prev_trace_mode = 'continuous'
    app.root.event_generate('<<ChangedToContinuousView>>')
    pass

def set_view_overlay(save_undo=True):
    global prev_trace_mode
    global widgets
    if prev_trace_mode == 'overlay':
        print('stays in overlay')
        return
    app.root.event_generate('<<ChangeToOverlayView>>')
    if save_undo and prev_trace_mode == 'continuous':
        interface.add_undo([
            lambda d=False: set_view_continuous(d)
        ])
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
    prev_trace_mode = 'overlay'
    app.root.event_generate('<<ChangedToOverlayView>>')
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
