import tkinter as Tk
from tkinter import ttk, filedialog
from config import config
from utils.widget import VarWidget
from Backend import interface
from DataVisualizer import param_guide, data_display, trace_display, evoked_data_display, results_display
from Layout import detector_tab
import gc
import app

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
        fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
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


