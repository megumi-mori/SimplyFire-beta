from PyMini import app
from PyMini.Modules.base_control_module import BaseControlModule
from . import recording_processor
import tkinter as Tk
from tkinter import ttk
from PyMini.utils import widget
class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
                 name='post_processing',
                 menu_label = 'Process Recording',
                 tab_label = 'Process',
                 parent=app.root,
                 scrollbar=True,
                 filename=__file__,
                 has_table=False
                 )
        self._load_layout()
    def average_sweeps(self, event=None):
        print(app.interface.recordings[0].y_data.dtype)
        if app.widgets['trace_mode'].get() == 'continuous':
            return
        if self.widgets['channel_target'].get():
            target_channels = [app.interface.channel]
        else:
            target_channels = range(app.interface.recordings[0].channel_count)
        target_sweeps = []
        if self.widgets['sweep_target'].get() == 'All sweeps':
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif self.widgets['sweep_target'].get() == 'Visible sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweeps_tab'].get_visible_sweeps()
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get () == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        elif self.widgets['sweep_target'].get() == 'Highlighted sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweep_tab'].get_highlighted_sweeps()
            # account for more recordings being open (consider only the main file open)
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get () == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        avg_sweep = recording_processor.average_sweeps(app.interface.recordings[0],
                                                       channels=target_channels,
                                                       sweeps=target_sweeps)
        app.interface.recordings[0].append_sweep(avg_sweep)
        app.interface.plot()
        app.modules_dict['sweeps']['sweeps_tab'].synch_sweep_list()
        if self.widgets['average_show_result'].get():
            app.modules_dict['sweeps']['sweeps_tab'].hide_all()
            app.modules_dict['sweeps']['sweeps_tab'].sweep_buttons[app.interface.recordings[0].sweep_count-1].invoke()
        pass
    def subtract_baseline(self, event=None):
        if len(app.interface.recordings)==0:
            return None # nothing to process
        if self.widgets['channel_target'].get():
            target_channels = [app.interface.channel]
        else:
            target_channels = range(app.interface.recordings[0].channel_count)
        xlim = None
        if self.widgets['baseline_mode'].get() == 'Mean of x-axis range':
            try:
                xlim = (float(self.widgets['baseline_range_left'].get()),
                        float(self.widgets['baseline_range_right'].get()))
            except:
                pass

        shift = None
        if self.widgets['baseline_mode'].get() == 'Fixed value':
            shift = float(self.widgets['baseline_fixed'].get())

        target_sweeps = []
        if self.widgets['sweep_target'].get() == 'All sweeps':
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif self.widgets['sweep_target'].get() == 'Visible sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweeps_tab'].get_visible_sweeps()
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get () == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        elif self.widgets['sweep_target'].get() == 'Highlighted sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweep_tab'].get_highlighted_sweeps()
            # account for more recordings being open (consider only the main file open)
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get () == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        if len(target_sweeps) == 0:
            return

        recording_processor.subtract_baseline(app.interface.recordings[0],
                                              plot_mode=app.widgets['trace_mode'].get(),
                                              channels=target_channels,
                                              sweeps=target_sweeps,
                                              xlim=xlim,
                                              shift=shift)

        #['All sweeps', 'Visible sweeps', 'Highlighted sweeps']
        # deal with undo later

        app.interface.plot(fix_x=True)
        pass

    def filter_data(self, event=None):
        if len(app.interface.recordings)==0:
            return None # nothing to process
        if self.widgets['channel_target'].get():
            target_channels = [app.interface.channel]
        else:
            target_channels = range(app.interface.recordings[0].channel_count)

        target_sweeps = []
        if self.widgets['sweep_target'].get() == 'All sweeps':
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif self.widgets['sweep_target'].get() == 'Visible sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweeps_tab'].get_visible_sweeps()
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get() == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
        elif self.widgets['sweep_target'].get() == 'Highlighted sweeps':
            target_sweeps = app.modules_dict['sweeps']['sweep_tab'].get_highlighted_sweeps()
            # account for more recordings being open (consider only the main file open)
            if app.widgets['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
                target_sweeps = range(app.interface.recordings[0].sweep_count)
            elif app.widgets['trace_mode'].get() == 'overlay':
                # account for more recordings being open (consider only the main file open)
                target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]

        filter_choice = self.widgets['filter_algorithm'].get()
        filter_algorithm = self.widgets[f'filter_{filter_choice}_algorithm'].get()
        params = {}
        for key in self.default[f'{filter_algorithm}_params']:
            params[key] = self.widgets[key].get()

        # deal with undo later

        getattr(recording_processor, f'filter_{filter_algorithm}')(app.interface.recordings[0],
                                                                   params,
                                                                   target_channels,
                                                                   target_sweeps)
        app.interface.plot(fix_x=True, fix_y=True)


    def _load_layout(self):
        self.insert_title(text='Adjust Trace')

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
            text='Limit process to the current channel',
            onvalue='1',
            offvalue='',
            separator=True
        )
        self.insert_title(text='Baseline Subtraction', separator=False)
        self.insert_title(text='Calculate baseline using:', separator=False)

        self.insert_label_optionmenu(
            name='baseline_mode',
            text='',
            options=['Mean of all targets', 'Mean of x-axis range', 'Fixed value'],
            command=self._select_baseline_mode,
            separator=False
        )
        self.baseline_option_panels={}
        self.baseline_option_panels['Mean of all targets'] = self.make_panel(separator=False)
        self.baseline_option_panels['Mean of x-axis range'] = self.make_panel(separator=False)

        panel = Tk.Frame(self.baseline_option_panels['Mean of x-axis range'])
        panel.grid(row=0, column=0, sticky='news')
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

        self.widgets['baseline_range_left'] = widget.VarEntry(parent=panel, name='baseline_range_left',
                                                            validate_type='float',
                                                              value=self.values.get('baseline_range_left',
                                                                                    self.default.get(
                                                                                        'baseline_range_left', None)))
        self.widgets['baseline_range_left'].grid(column=0, row=0, sticky='news')
        self.widgets['baseline_range_right'] = widget.VarEntry(parent=panel, name='baseline_range_rigjt',
                                                            validate_type='float',
                                                            value=self.values.get('baseline_range_right',
                                                                                  self.default.get('baseline_range_right',
                                                                                                   None)))
        self.widgets['baseline_range_right'].grid(column=1, row=0, sticky='news')
        self.baseline_option_panels['Fixed value'] = self.make_panel(separator=False)
        panel = Tk.Frame(self.baseline_option_panels['Fixed value'])
        panel.grid_columnconfigure(0, weight=1)
        panel.grid(row=0, column=0, sticky='news')

        self.widgets['baseline_fixed'] = widget.VarEntry(parent=panel, name='baseline_fixed',
                                                            validate_type='float',
                                                            value=self.values.get('baseline_fixed',
                                                                                  self.default.get('baseline_fixed',
                                                                                                   None)))
        self.widgets['baseline_fixed'].grid(row=0, column=0, sticky='news')

        self._select_baseline_mode()

        self.insert_button(text='Apply', command=self.subtract_baseline)
        self.insert_button(text='Default', command=self._default_baseline_params)

        self.insert_separator()

        self.insert_title(
            text='Average sweeps',
            separator=False,
        )
        self.insert_label_checkbox(
            name='average_show_result',
            text='Hide original sweeps',
            onvalue='1',
            offvalue='',
            separator=False
        )
        self.insert_button(
            text='Apply',
            command=self.average_sweeps
        )
        self.insert_button(
            text='Default',
            command=self._default_averaging_params
        )
        self.insert_separator()
        self.insert_title(
            text='Filtering',
            separator=False
        )
        self.filter_choices = ['Highpass', 'Lowpass']
        self.insert_label_optionmenu(
            name='filter_algorithm',
            text="Select low or high pass:",
            options=self.filter_choices,
            separator=False,
            command=self._select_filter_mode
        )

        self.lowpass_algorithms = ['Boxcar', 'Test']
        self.insert_label_optionmenu(
            name='filter_Lowpass_algorithm',
            text='Algorithm:',
            options=self.lowpass_algorithms,
            separator=False,
            command=self._select_lowpass_algorithm
        )

        # algorithm specific parameters
        self.filter_params = {}
        self.filter_params['width'] = self.insert_label_entry(
            name='width',
            text='Width',
            validate_type='int'
        )
        self.widgets['width'].bind('<Return>', app.interface.focus)

        self.highpass_algorithms = ['Not yet supported']
        self.insert_label_optionmenu(
            name='filter_Highpass_algorithm',
            text='Algorithm:',
            options=self.highpass_algorithms,
            separator=False,
            command=self._select_highpass_algorithm
        )
        self._select_filter_mode()
        self.insert_button(text='Apply', command=self.filter_data)
        self.insert_button(text='Default', command=self._default_filter_params)
        #
    def _default_averaging_params(self, event=None):
        self.set_to_default(filter='average')
        app.interface.focus()
    def _default_baseline_params(self, event=None):
        self.set_to_default(filter='baseline')
        self._select_baseline_mode()
        app.interface.focus()
    def _default_filter_params(self, event=None):
        self.set_to_default(filter='filter')
        self._select_filter_mode()
        app.interface.focus()
    def _select_baseline_mode(self, event=None):
        selection = self.widgets['baseline_mode'].get()
        for key in self.baseline_option_panels:
            if key != selection:
                self.baseline_option_panels[key].grid_remove()
            else:
                self.baseline_option_panels[key].grid()
        app.interface.focus()
    def _select_filter_mode(self, event=None):
        choice = self.widgets['filter_algorithm'].get()
        non_choices = [i for i in self.filter_choices if i!= choice]
        # show all or hide all relevant widgets to the filter mode
        for w in self.widgets.keys():
            if choice in w:
                self.show_widget(w)
            else:
                for other in non_choices:
                    if other in w:
                        self.hide_widget(w)
        # hide all parameter related frames
        for w in self.filter_params:
            self.hide_widget(w)

        getattr(self, f'_select_{choice.lower()}_algorithm')()
        app.interface.focus()
    def _select_lowpass_algorithm(self, event=None):
        choice = self.widgets['filter_Lowpass_algorithm'].get()
        for key in self.default[f'{choice}_params']:
            self.show_widget(key)
        pass

    def _select_highpass_algorithm(self, event=None):
        pass