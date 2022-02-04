from PyMini.Modules.base_module_control import BaseModuleControl
from PyMini import app
from PyMini.utils import custom_widgets
import tkinter as Tk
from tkinter import messagebox

from . import evoked_analysis
class ModuleControl(BaseModuleControl):
    def __init__(self, module):
        super().__init__(
            module=module,
            scrollbar=True,
        )

        self.index = 0
        self._load_layout()
        self._load_binding()
    def calculate_min_max(self, event=None):
        if len(app.interface.recordings) == 0:
            messagebox.showerror('Error', 'Please open a recording file first')
            return None
        target_sweeps = []
        if self.widgets['sweep_target'].get() == 'All sweeps':
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif self.widgets['sweep_target'].get() == 'Visible sweeps':
            target_sweeps = app.modules_dict['sweeps'].control_tab.get_visible_sweeps()
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get() == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        elif self.widgets['sweep_target'].get() == 'Highlighted sweeps':
            target_sweeps = app.modules_dict['sweeps'].control_tab.get_highlighted_sweeps()
            # account for more recordings being open (consider only the main file open)
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get() == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        if self.widgets['channel_target'].get():
            target_channels = [app.interface.channel]
        else:
            target_channels = range(app.interface.recordings[0].channel_count)

        xlim=None
        window = self.widgets['range_target'].get()
        if window == 'Visible sweeps':
            xlim = app.trace_display.ax.get_xlim()
        elif window == 'Defined range':
            xlim = (float(self.widgets['range_left'].get()), float(self.widgets['range_right'].get()))

        recording = app.interface.recordings[0]
        mins, mins_std = evoked_analysis.calculate_min_sweeps(recording,
                                                              plot_mode=app.widgets['trace_mode'].get(),
                                                              channels=target_channels,
                                                              sweeps=target_sweeps,
                                                              xlim=xlim)
        maxs, maxs_std = evoked_analysis.calculate_max_sweeps(recording,
                                                              plot_mode=app.widgets['trace_mode'].get(),
                                                              channels=target_channels,
                                                              sweeps=target_sweeps,
                                                              xlim=xlim)
        # report
        if app.widgets['trace_mode'].get() == 'continuous':
            target_sweeps = [0] # continuous mode only has 1 sweep
        for i,c in enumerate(target_channels):
            for j,s in enumerate(target_sweeps):
                self.module.data_tab.add({
                    'filename': recording.filename,
                    'channel': c,
                    'sweep': s,
                    'min': mins[i, j, 0],
                    'min_unit': recording.y_unit,
                    'max': maxs[i, j, 0],
                    'max_unit': recording.y_unit
                }, undo=False)
        if app.interface.is_accepting_undo():
            new_list = tuple(self.module.data_tab.table.get_children()[-len(target_sweeps)*len(target_channels):])
            self.module.add_undo([
                lambda l=new_list: self.module.data_tab.delete(l)
            ])
        # self.module.data_tab.select()

    def _select_xlim_mode(self, event=None):
        selection = self.widgets['range_target'].get()
        for key in self.range_option_panels:
            if key != selection:
                self.hide_widget(target=self.range_option_panels[key])
            else:
                self.show_widget(target=self.range_option_panels[key])
        app.interface.focus()

    def _load_layout(self):
        self.insert_title(
            text='Evoked Analysis',
            separator=True
        )
        self.insert_title(text='Target setting', separator=False)
        self.insert_title(text='Apply processing to the following sweeps', separator=False)

        self.insert_label_optionmenu(
            name='sweep_target',
            text='',
            options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
            separator=False
        )
        self.insert_label_checkbox(
            name='channel_target',
            text='Limit analysis to the current channel',
            onvalue='1',
            offvalue='',
            separator=False
        )
        self.insert_title(text='Limit x-axis for analysis to:', separator=False)

        self.insert_label_optionmenu(
            name='range_target',
            text='',
            options=['Entire sweep', 'Visible window', 'Defined range'],
            command=self._select_xlim_mode,
            separator=False
        )
        self.range_option_panels = {}
        self.range_option_panels['Entire sweep'] = self.make_panel(separator=False)
        self.range_option_panels['Visible window'] = self.make_panel(separator=False)
        self.range_option_panels['Defined range'] = self.make_panel(separator=False)

        panel = Tk.Frame(self.range_option_panels['Defined range'])
        panel.grid(row=0, column=0, sticky='news')
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

        self.widgets['range_left'] = custom_widgets.VarEntry(parent=panel, name='range_left',
                                                             validate_type='float',
                                                             value=self.values.get('range_left',
                                                                           self.default.get(
                                                                               'range_left', None)))
        self.widgets['range_left'].grid(column=0, row=0, sticky='news')
        self.widgets['range_right'] = custom_widgets.VarEntry(parent=panel, name='range_rigjt',
                                                              validate_type='float',
                                                              value=self.values.get('range_right',
                                                                                     self.default.get(
                                                                                         'range_right',
                                                                                         None)))
        self.widgets['range_right'].grid(column=1, row=0, sticky='news')
        self.insert_separator()

        self.insert_title(
            text='Min/Max',
            separator=False
        )
        self.insert_button(
            text='Calculate Min/Max',
            command=self.calculate_min_max
        )

    def _load_binding(self):
        app.root.bind('<<LoadCompleted>>', self.module.update_module_display, add='+')