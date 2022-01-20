import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
import os
from PyMini.config import config
from PyMini.utils.widget import VarWidget
from PyMini.Backend import interface
from PyMini.DataVisualizer import param_guide, data_display, trace_display, evoked_data_display, results_display
import gc
from PyMini import app
# from PyMini.Layout import keybind_popup

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
    file_menu.add_command(label='Open mini data file', command=open_events)
    # file_menu.add_command(label='Save event file', command=interface.save_events_dialogue)
    file_menu.add_command(label='Save mini data as...', command=interface.save_events_as_dialogue)

    file_menu.add_separator()
    file_menu.add_command(label='Export plot', command=ask_save_plot)
    file_menu.add_command(label='Export mini analysis table', command=export_events)
    file_menu.add_command(label='Export evoked analysis table', command=export_evoked)
    file_menu.add_command(label='Export results table', command=export_results)

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
    view_menu.add_radiobutton(label='Comparison', command=set_view_compare, variable=trace_var, value='compare')

    # Analysis menu
    global analysis_menu
    analysis_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Analysis', menu=analysis_menu)
    # track analysis_mode
    analysis_var = Tk.StringVar(parent, 0)
    widgets['analysis_mode'] = analysis_var
    analysis_menu.add_radiobutton(label='Mini', command=set_analysis_mini, variable=analysis_var,
                                       value='mini')
    analysis_menu.add_radiobutton(label='Evoked', command=set_analysis_evoked, variable=analysis_var,
                                       value='evoked')
    analysis_menu.add_separator()

    # Window menu
    window_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Window', menu=window_menu)
    widgets['window_param_guide'] = VarWidget(name='window_param_guide')
    window_menu.add_command(label='Parameter-guide', command=_show_param_guide)
    # window_menu.add_command(label='Key binder', command=_show_key_binder)
    if widgets['window_param_guide'].get() == '1':
        window_menu.invoke(window_menu.index('Parameter-guide'))

    widgets['analysis_mode'].set(config.analysis_mode)
    widgets['trace_mode'].set(config.trace_mode)
    view_menu.invoke({'continuous': 0, 'overlay': 1, 'compare':2}[config.trace_mode])
    analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])

    undo_disable()
    return menubar

def ask_open_recording():
    gc.collect()
    if ask_save_events() is None:
        return None
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('csv files', '*.csv'), ('All files', '*.*')])
    if not fname:
        return None
    interface.open_recording(fname)
    app.compare_tab.start_msg.grid_forget()
    interface.focus()
    return fname

def ask_save_events():
    if interface.al.mini_df.shape[0]>0:
        answer = messagebox.askyesnocancel(title='Save Events?', message='Save changes to the mini analysis data table?')
        # yes = True, no = False, cancel = None
        if answer is None:
            return None
        if answer:
            return interface.save_events_as_dialogue()
        return False
    return True

def ask_save_plot(e=None):
    app.trace_display.canvas.toolbar.save_figure()

def ask_save_recording(e=None, save_events=True):
    if len(interface.recordings)==0:
        messagebox.showerror(title='Error', message='No recording to export. Please open a recording first.')
        return None
    save = False
    if save_events:
        save = ask_save_events()
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

def export_events():
    if len(interface.recordings) == 0:
        messagebox.showerror(title='Save error', message='Please open a trace to analyze first')
        return None
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
                                            defaultextension='.csv',
                                            initialfile=interface.recordings[0].filename.split('.')[0] + '_mini.csv')
    if filename:
        data_display.dataframe.export(filename)
        return
    return

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

def open_events():
    if len(interface.recordings)==0:
        messagebox.showerror('Open error', message='Please open a trace first')
        return None
    filename = filedialog.askopenfilename(filetype=[('mini data files', '*.event *.minipy'), ('All files', "*.*")],
                                            defaultextension='.event')
    if filename:
        interface.open_events(filename)
        interface.focus()
        return
    return

def set_analysis_evoked():
    global widgets
    widgets['analysis_mode'].set('evoked')
    interface.config_cp_tab('evoked', state='normal')
    interface.config_data_tab('evoked', state='normal')
    trace_display.clear_markers()
    pass

def set_analysis_mini():
    global widgets
    widgets['analysis_mode'].set('mini')
    interface.config_cp_tab('mini', state='normal')
    interface.config_data_tab('mini', state='normal')
    if widgets['trace_mode'].get() != 'continuous':
        interface.config_cp_tab('mini', state='disabled')
        interface.config_data_tab('mini', state='disabled')
        pass
    interface.update_event_marker()
    app.pb['value'] = 0
    app.pb.update()
    pass

def set_view_compare(save_undo=True):
    global trace_mode
    global widgets
    if save_undo and trace_mode == 'overlay':
        interface.add_undo([
            lambda s=False: set_view_overlay(s)
        ])
    elif save_undo and trace_mode == 'continuous':
        interface.add_undo([
            lambda d=False: set_view_continuous(d)
        ])
    widgets['trace_mode'].set('compare')
    # switch to continuous mode tab
    interface.config_cp_tab('compare', state='normal')
    interface.config_cp_tab('adjust', state='disabled')
    interface.config_cp_tab(widgets['analysis_mode'].get(), state='disabled')
    interface.config_data_tab(widgets['analysis_mode'].get(), state='disabled')

    try:
        for i,r in enumerate(interface.recordings):
            interface.plot_overlay(i, fix_axis=True, append=(i!=0))
    except:
        pass
    trace_mode = 'compare'

def set_view_continuous(save_undo=True):
    global trace_mode
    global widgets
    if save_undo and trace_mode == 'overlay':
        interface.add_undo([
            lambda s=False: set_view_overlay(s),
        ])
    elif save_undo and trace_mode == 'compare':
        interface.add_undo([
            lambda s=False: set_view_compare(s)
        ])
    widgets['trace_mode'].set('continuous')

    # switch to continuous mode tab
    interface.config_cp_tab('continuous', state='normal')

    try:
        interface.plot_continuous(interface.recordings[0], fix_axis=True)
    except:
        pass
    if widgets['analysis_mode'].get() == 'mini':
        interface.config_cp_tab('mini', state='normal')
        interface.config_data_tab('mini', state='normal')
    interface.config_cp_tab('adjust', state='normal')
    trace_mode = 'continuous'
    pass

def set_view_overlay(save_undo=True):
    global trace_mode
    global widgets
    if save_undo and trace_mode == 'continuous':
        interface.add_undo([
            lambda d=False: set_view_continuous(d)
        ])
    elif save_undo and trace_mode == 'compare':
        interface.add_undo([
            lambda d=False: set_view_compare(d)
        ])
    widgets['trace_mode'].set('overlay')
    interface.config_cp_tab('overlay', state='normal')
    try:
        interface.plot_overlay(0, fix_axis=True)
    except:
        pass
    if widgets['analysis_mode'].get() == 'mini':
        interface.config_cp_tab('mini', state='disabled')
        interface.config_data_tab('mini', state='disabled')
    interface.config_cp_tab('adjust',state='normal')
    trace_mode = 'overlay'
    pass

def undo_disable():
    global edit_menu
    edit_menu.entryconfig(0, state='disabled')

def undo_enable():
    global edit_menu
    edit_menu.entryconfig(0, state='normal')

# def _show_key_binder(event=None):
#     keybind_popup.load()
def _show_param_guide(event=None):
    global widgets
    try:
        if widgets['window_param_guide'].get() == '1':
            param_guide.window.focus_set()
            pass
        else:
            widgets['window_param_guide'].set('1')
            param_guide.load()
    except:
        param_guide.load()

# class Menubar():
#     def __init__(self, parent):
#         self.widgets = {}
#         self.trace_mode = 'continuous'
#         self.menubar = Tk.Menu(parent)
#
#         ##################################
#         # add menu bar commands here
#         ##################################
#
#         # File menu
#         file_menu = Tk.Menu(self.menubar, tearoff=0)
#         self.menubar.add_cascade(label='File', menu=file_menu)
#
#         file_menu.add_command(label="Open trace \t Ctrl+o", command=self.ask_open_trace)
#         file_menu.add_separator()
#         file_menu.add_command(label='Open event file', command=self.open_events)
#         file_menu.add_command(label='Save event file', command=interface.save_events_dialogue)
#         file_menu.add_command(label='Save event file as...', command=interface.save_events_as_dialogue)
#         file_menu.add_command(label='Export events', command=self.export_events)
#
#         file_menu.add_separator()
#         file_menu.add_command(label='Export evoked analysis', command=self.export_evoked)
#
#         file_menu.add_command(label='Export results', command=self.export_results)
#
#         # Edit menu
#         self.edit_menu = Tk.Menu(self.menubar, tearoff=0)
#         self.menubar.add_cascade(label='Edit', menu=self.edit_menu)
#         self.edit_menu.add_command(label='Undo \t Ctrl+z', command=interface.undo, state='disabled')
#
#         # View menu
#         global view_menu
#         view_menu = Tk.Menu(self.menubar, tearoff=0)
#         self.menubar.add_cascade(label='View', menu=view_menu)
#         # track trace_mode
#         trace_var = Tk.StringVar(parent, 0)
#         self.widgets['trace_mode'] = trace_var
#         view_menu.add_radiobutton(label='Continous', command=self.set_view_continuous, variable=trace_var, value='continuous')
#         view_menu.add_radiobutton(label='Overlay', command=self.set_view_overlay, variable=trace_var, value='overlay')
#
#         # Analysis menu
#         self.analysis_menu = Tk.Menu(self.menubar, tearoff=0)
#         self.menubar.add_cascade(label='Analysis', menu=self.analysis_menu)
#         # track analysis_mode
#         analysis_var = Tk.StringVar(parent, 0)
#         self.widgets['analysis_mode'] = analysis_var
#         self.analysis_menu.add_radiobutton(label='Mini', command=self.set_analysis_mini, variable=analysis_var, value='mini')
#         self.analysis_menu.add_radiobutton(label='Evoked', command=self.set_analysis_evoked, variable=analysis_var, value='evoked')
#         self.analysis_menu.add_separator()
#
#         # Window menu
#         window_menu = Tk.Menu(self.menubar, tearoff=0)
#         self.menubar.add_cascade(label='Window', menu=window_menu)
#         self.widgets['window_param_guide'] = VarWidget(name='window_param_guide')
#         window_menu.add_command(label='Parameter-guide', command=self._show_param_guide)
#         if self.widgets['window_param_guide'].get() == '1':
#             window_menu.invoke(window_menu.index('Parameter-guide'))
#
#         view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
#         self.analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])
#
#
#     def ask_open_trace(self):
#         gc.collect()
#         fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('csv files', '*.csv'), ('All files', '*.*')])
#         if not fname:
#             return None
#         interface.open_trace(fname)
#         print('ask_open_trace')
#         print(app.compare_tab.start_msg)
#         app.compare_tab.start_msg.forget()
#
#     def export_events(self):
#         filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
#                                                 defaultextension='.csv',
#                                                 initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
#         if filename:
#             data_display.dataframe.export(filename)
#             return
#         return
#
#     def export_evoked(self):
#         filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
#                                                 defaultextension='.csv',
#                                                 initialfile=interface.al.recording.filename.split('.')[
#                                                                 0] + '_evoked.csv')
#         evoked_data_display.dataframe.export(filename)
#
#     def export_results(self):
#         filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
#                                                 defaultextension='.csv',
#                                                 initialfile='results.csv')
#         results_display.dataframe.export(filename)
#
#     def open_events(self):
#         filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
#                                                 defaultextension='.csv',
#                                                 initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
#         if filename:
#             data_display.dataframe.export(filename)
#             return
#         return
#
#     def set_analysis_evoked(self):
#         self.widgets['analysis_mode'].set('evoked')
#         interface.config_cp_tab('evoked', state='normal')
#         interface.config_data_tab('evoked', state='normal')
#         trace_display.clear_markers()
#         pass
#
#     def set_analysis_mini(self):
#         self.widgets['analysis_mode'].set('mini')
#         interface.config_cp_tab('mini', state='normal')
#         interface.config_data_tab('mini', state='normal')
#         if self.widgets['trace_mode'].get() != 'continuous':
#             interface.config_cp_tab('mini', state='disabled')
#             interface.config_data_tab('mini', state='disabled')
#             pass
#         interface.populate_data_display()
#         interface.update_event_marker()
#         app.pb['value'] = 0
#         app.pb.update()
#         pass
#
#
#     def set_view_continuous(self, save_undo=True):
#         if save_undo and self.trace_mode == 'overlay':
#             interface.add_undo([
#                 lambda s=False: self.set_view_overlay(s),
#             ])
#         self.widgets['trace_mode'].set('continuous')
#
#         # switch to continuous mode tab
#         interface.config_cp_tab('continuous', state='normal')
#
#         try:
#             interface.plot_continuous(fix_axis=True)
#         except:
#             pass
#         if self.widgets['analysis_mode'].get() == 'mini':
#             interface.config_cp_tab('mini', state='normal')
#             interface.config_data_tab('mini', state='normal')
#         self.trace_mode = 'continuous'
#         pass
#
#     def set_view_overlay(self, save_undo=True):
#         if save_undo and self.trace_mode == 'continuous':
#             interface.add_undo([
#                 lambda d=False: self.set_view_continuous(d)
#             ])
#         self.widgets['trace_mode'].set('overlay')
#         interface.config_cp_tab('overlay', state='normal')
#         try:
#             interface.plot_overlay(fix_axis=True)
#         except:
#             pass
#         print('set_view_overlay, before if statement')
#         print(self.widgets['analysis+mode'].get())
#         if self.widgets['analysis_mode'].get() == 'mini':
#             interface.config_cp_tab('mini', state='disabled')
#             print('set view overlay disable mini')
#             interface.config_data_tab('mini', state='disabled')
#         self.trace_mode = 'overlay'
#         pass
#
#     def undo_disable(self):
#         self.edit_menu.entryconfig(0, state='disabled')
#
#     def undo_enable(self):
#         self.edit_menu.entryconfig(0, state='normal')
#
#     def _show_param_guide(self,event=None):
#         try:
#             if self.widgets['window_param_guide'].get() == '1':
#                 param_guide.window.focus_set()
#                 pass
#             else:
#                 self.widgets['window_param_guide'].set('1')
#                 param_guide.load()
#         except:
#             param_guide.load()


