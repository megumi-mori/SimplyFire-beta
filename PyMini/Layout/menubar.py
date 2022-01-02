import tkinter as Tk
from tkinter import ttk, filedialog, messagebox
from PyMini.config import config
from PyMini.utils.widget import VarWidget
from PyMini.Backend import interface
from PyMini.DataVisualizer import param_guide, data_display, trace_display, evoked_data_display, results_display
import gc
from PyMini import app

def load(parent):
    print(app.data_notebook)
    global widgets
    widgets = {}
    global trace_mode
    trace_mode = 'continuous'

    menubar = Tk.Menu(parent)

    ##################################
    # add menu bar commands here
    ##################################

    # File menu
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)

    file_menu.add_command(label="Open trace \t Ctrl+o", command=ask_open_trace)
    file_menu.add_command(label='Save channel as...', command=export_recording)
    file_menu.add_separator()
    file_menu.add_command(label='Open event file', command=open_events)
    file_menu.add_command(label='Save event file', command=interface.save_events_dialogue)
    file_menu.add_command(label='Save event file as...', command=interface.save_events_as_dialogue)

    file_menu.add_separator()
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
    view_menu.add_radiobutton(label='Continous', command=set_view_continuous, variable=trace_var,
                              value='continuous')
    view_menu.add_radiobutton(label='Overlay', command=set_view_overlay, variable=trace_var, value='overlay')

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
    if widgets['window_param_guide'].get() == '1':
        window_menu.invoke(window_menu.index('Parameter-guide'))

    view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
    analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])

    return menubar

def ask_open_trace():
    gc.collect()
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('csv files', '*.csv'), ('All files', '*.*')])
    if not fname:
        return None
    interface.open_trace(fname)

def export_events():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
                                            defaultextension='.csv',
                                            initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
    if filename:
        data_display.dataframe.export(filename)
        return
    return

def export_evoked():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                            defaultextension='.csv',
                                            initialfile=interface.al.recording.filename.split('.')[
                                                            0] + '_evoked.csv')
    evoked_data_display.dataframe.export(filename)

def export_recording():
    if interface.al.recording is None:
        messagebox.showerror('Write error', message='No recording to export. Please open a recording first.')
        return None
    initialfname = interface.al.recording.filename.split('.')[0] + '_PyMini'
    try:
        filename = filedialog.asksaveasfilename(filetype=[('abf files', '*.abf'), ('csv files', '*.csv'), ('All files', '*.*')],
                                                defaultextension='.abf',
                                                initialfile=initialfname)

        if filename is not None:
            interface.al.recording.save(filename)
    except (FileExistsError):
        messagebox.showerror('Write error', message='Cannot overwrite an existing ABF file')

def export_results():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                            defaultextension='.csv',
                                            initialfile='results.csv')
    results_display.dataframe.export(filename)

def open_events():
    filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
                                            defaultextension='.csv',
                                            initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
    if filename:
        data_display.dataframe.export(filename)
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
    if widgets['trace_mode'].get() != 'continuous':
        interface.config_cp_tab('mini', state='disabled')
        pass
    interface.config_data_tab('mini', state='normal')
    interface.populate_data_display()
    interface.update_event_marker()
    app.pb['value'] = 0
    app.pb.update()
    pass


def set_view_continuous(save_undo=True):
    global trace_mode
    global widgets
    if save_undo and trace_mode == 'overlay':
        interface.add_undo([
            lambda s=False: set_view_overlay(s),
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
    pass

def set_view_overlay(save_undo=True):
    global trace_mode
    global widgets
    if save_undo and trace_mode == 'continuous':
        interface.add_undo([
            lambda d=False: set_view_continuous(d)
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
    pass

def undo_disable():
    global edit_menu
    edit_menu.entryconfig(0, state='disabled')

def undo_enable():
    global edit_menu
    edit_menu.entryconfig(0, state='normal')

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

class Menubar():
    def __init__(self, parent):
        self.widgets = {}
        self.trace_mode = 'continuous'
        self.menubar = Tk.Menu(parent)

        ##################################
        # add menu bar commands here
        ##################################

        # File menu
        file_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=file_menu)

        file_menu.add_command(label="Open trace \t Ctrl+o", command=self.ask_open_trace)
        file_menu.add_separator()
        file_menu.add_command(label='Open event file', command=self.open_events)
        file_menu.add_command(label='Save event file', command=interface.save_events_dialogue)
        file_menu.add_command(label='Save event file as...', command=interface.save_events_as_dialogue)
        file_menu.add_command(label='Export events', command=self.export_events)

        file_menu.add_separator()
        file_menu.add_command(label='Export evoked analysis', command=self.export_evoked)

        file_menu.add_command(label='Export results', command=self.export_results)

        # Edit menu
        self.edit_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Edit', menu=self.edit_menu)
        self.edit_menu.add_command(label='Undo \t Ctrl+z', command=interface.undo, state='disabled')

        # View menu
        global view_menu
        view_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='View', menu=view_menu)
        # track trace_mode
        trace_var = Tk.StringVar(parent, 0)
        self.widgets['trace_mode'] = trace_var
        view_menu.add_radiobutton(label='Continous', command=self.set_view_continuous, variable=trace_var, value='continuous')
        view_menu.add_radiobutton(label='Overlay', command=self.set_view_overlay, variable=trace_var, value='overlay')

        # Analysis menu
        self.analysis_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Analysis', menu=self.analysis_menu)
        # track analysis_mode
        analysis_var = Tk.StringVar(parent, 0)
        self.widgets['analysis_mode'] = analysis_var
        self.analysis_menu.add_radiobutton(label='Mini', command=self.set_analysis_mini, variable=analysis_var, value='mini')
        self.analysis_menu.add_radiobutton(label='Evoked', command=self.set_analysis_evoked, variable=analysis_var, value='evoked')
        self.analysis_menu.add_separator()

        # Window menu
        window_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Window', menu=window_menu)
        self.widgets['window_param_guide'] = VarWidget(name='window_param_guide')
        window_menu.add_command(label='Parameter-guide', command=self._show_param_guide)
        if self.widgets['window_param_guide'].get() == '1':
            window_menu.invoke(window_menu.index('Parameter-guide'))

        view_menu.invoke({'continuous': 0, 'overlay': 1}[config.trace_mode])
        self.analysis_menu.invoke({'mini': 0, 'evoked': 1}[config.analysis_mode])


    def ask_open_trace(self):
        gc.collect()
        fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('csv files', '*.csv'), ('All files', '*.*')])
        if not fname:
            return None
        interface.open_trace(fname)

    def export_events(self):
        filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
                                                defaultextension='.csv',
                                                initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
        if filename:
            data_display.dataframe.export(filename)
            return
        return

    def export_evoked(self):
        filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                                defaultextension='.csv',
                                                initialfile=interface.al.recording.filename.split('.')[
                                                                0] + '_evoked.csv')
        evoked_data_display.dataframe.export(filename)

    def export_results(self):
        filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('ALl files', '*.*')],
                                                defaultextension='.csv',
                                                initialfile='results.csv')
        results_display.dataframe.export(filename)

    def open_events(self):
        filename = filedialog.asksaveasfilename(filetype=[('csv files', '*.csv'), ('All files', "*.*")],
                                                defaultextension='.csv',
                                                initialfile=interface.al.recording.filename.split('.')[0] + '_mini.csv')
        if filename:
            data_display.dataframe.export(filename)
            return
        return

    def set_analysis_evoked(self):
        self.widgets['analysis_mode'].set('evoked')
        interface.config_cp_tab('evoked', state='normal')
        interface.config_data_tab('evoked', state='normal')
        trace_display.clear_markers()
        pass

    def set_analysis_mini(self):
        self.widgets['analysis_mode'].set('mini')
        interface.config_cp_tab('mini', state='normal')
        if self.widgets['trace_mode'].get() != 'continuous':
            interface.config_cp_tab('mini', state='disabled')
            pass
        interface.config_data_tab('mini', state='normal')
        interface.populate_data_display()
        interface.update_event_marker()
        app.pb['value'] = 0
        app.pb.update()
        pass


    def set_view_continuous(self, save_undo=True):
        if save_undo and self.trace_mode == 'overlay':
            interface.add_undo([
                lambda s=False: self.set_view_overlay(s),
            ])
        self.widgets['trace_mode'].set('continuous')

        # switch to continuous mode tab
        interface.config_cp_tab('continuous', state='normal')

        try:
            interface.plot_continuous(fix_axis=True)
        except:
            pass
        if self.widgets['analysis_mode'].get() == 'mini':
            interface.config_cp_tab('mini', state='normal')
        self.trace_mode = 'continuous'
        pass

    def set_view_overlay(self, save_undo=True):
        if save_undo and self.trace_mode == 'continuous':
            interface.add_undo([
                lambda d=False: self.set_view_continuous(d)
            ])
        self.widgets['trace_mode'].set('overlay')
        interface.config_cp_tab('overlay', state='normal')
        try:
            interface.plot_overlay(fix_axis=True)
        except:
            pass
        if self.widgets['analysis_mode'].get() == 'mini':
            interface.config_cp_tab('mini', state='disabled')
        self.trace_mode = 'overlay'
        pass

    def undo_disable(self):
        self.edit_menu.entryconfig(0, state='disabled')

    def undo_enable(self):
        self.edit_menu.entryconfig(0, state='normal')

    def _show_param_guide(self,event=None):
        try:
            if self.widgets['window_param_guide'].get() == '1':
                param_guide.window.focus_set()
                pass
            else:
                self.widgets['window_param_guide'].set('1')
                param_guide.load()
        except:
            param_guide.load()


