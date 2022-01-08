from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from tkinter import ttk, StringVar
import tkinter as Tk
from PyMini.config import config
from PyMini.utils import widget
from PyMini.Backend import interface
from PyMini.Layout.base_module import BaseModule
from PyMini import app
#### DEBUG
import tracemalloc

class AdjustTab(BaseModule):
    def __init__(self, parent, app, interface):
        super().__init__(parent, app, interface)

        self.frame.insert_title(text='Adjust Trace', separator=True)

        self.frame.insert_title(text='General Setting', separator=False)

        self.widgets['adjust_target'] = self.frame.insert_label_optionmenu(
            name='adjust_target',
            label='Apply adjustment to (overlay mode only):',
            options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
            separator=False
        )
        self.widgets['adjust_channel'] = self.frame.insert_label_checkbox(
            name='adjust_channel',
            label='Apply adjustment to visible channel only',
            onvalue='1',
            offvalue="",
            separator=False
        )
        self.frame.insert_separator()
        # -------
        # Baseline subtraction section

        self.frame.insert_title(text='Baseline Subtraction', separator=False)
        self.frame.insert_title(text='Perform baseline subtraction using:', separator=False)

        self.baseline_panel = OptionFrame(self.frame)
        self.baseline_panel.grid_columnconfigure(0, weight=1)
        self.frame.insert_widget(self.baseline_panel)

        self.widgets['adjust_baseline_mode'] = StringVar(self.baseline_panel, config.adjust_baseline_mode)
        self.baseline_option_buttons = {}

        self.baseline_option_buttons['mean'] = ttk.Radiobutton(
            self.baseline_panel,
            text='Mean of all target sweeps',
            value='mean',
            command=self._select_baseline_mode,
            variable=self.widgets['adjust_baseline_mode']
        )
        self.baseline_panel.insert_widget(self.baseline_option_buttons['mean'])

        self.baseline_option_buttons['range'] = ttk.Radiobutton(
            self.baseline_panel,
            text='Mean of range (x-axis) per sweep:',
            value='range',
            command=self._select_baseline_mode,
            variable=self.widgets['adjust_baseline_mode']
        )
        self.baseline_panel.insert_widget(self.baseline_option_buttons['range'])

        panel = Tk.Frame(self.baseline_panel)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)
        self.widgets['adjust_range_left'] = widget.VarEntry(parent=panel, name='adjust_range_left', validate_type='float')
        self.widgets['adjust_range_left'].grid(column=0, row=0, sticky='news')

        self.widgets['adjust_range_right'] = widget.VarEntry(parent=panel, name='adjust_range_right', validate_type='float')
        self.widgets['adjust_range_right'].grid(column=1, row=0, sticky='news')
        self.baseline_panel.insert_widget(panel)

        self.baseline_option_buttons['fixed'] = ttk.Radiobutton(
            self.baseline_panel,
            text='Fixed value:',
            value='fixed',
            command=self._select_baseline_mode,
            variable=self.widgets['adjust_baseline_mode']
        )
        self.baseline_panel.insert_widget(self.baseline_option_buttons['fixed'])

        self.widgets['adjust_fixed'] = widget.VarEntry(parent=self.baseline_panel, name='adjust_fixed', validate_type='float')
        self.baseline_panel.insert_widget(self.widgets['adjust_fixed'])

        self.frame.insert_button(
            text='Apply',
            command=self.adjust_baseline
        )

        # set baseline adjustment method to saved option
        self.baseline_option_buttons[config.adjust_baseline_mode].invoke()

        self.frame.insert_separator()
        # ------
        # Trace Averaging

        self.frame.insert_title(text='Trace Averaging', separator=False)
        self.widgets['adjust_avg_show_result'] = self.frame.insert_label_checkbox(
            name='adjust_avg_show_result',
            label='Only show resultant trace (hide original sweeps)',
            onvalue='1',
            offvalue="",
            separator=False
        )
        self.widgets['adjust_avg_min_max'] = self.frame.insert_label_checkbox(
            name='adjust_avg_min_max',
            label='Output min/max',
            onvalue='1',
            offvalue="",
            separator=False
        )
        self.widgets['adjust_avg_window'] = self.frame.insert_label_checkbox(
            name='adjust_avg_window',
            label='Limit min/max to within trace window',
            onvalue='1',
            offvalue='',
            separator=False
        )
        self.frame.insert_button(
            text='Apply',
            command=self.average_trace
        )
        self.frame.insert_separator()

        # -------
        # Filtering

        self.frame.insert_title(text='Trace Filtering', separator=False, justify=Tk.LEFT)


        self.widgets['adjust_filter_lohi'] = self.frame.insert_label_optionmenu(
            name='adjust_filter_lohi',
            label='Filtering method:',
            options=['Lowpass'],
            separator=False,
            command=self._populate_filter_algorithm_choices
        )

        # create algorithm choices for filtering

        self.filter_algorithm_panels = {}

        self.widgets['adjust_filter_Lowpass_algorithm'] = self.frame.insert_label_optionmenu(
            name='adjust_filter_Lowpass_algorithm',
            label='Lowpass algorithm:',
            options=['Boxcar'],
            separator=False,
            command=self._populate_filter_param_form  # populate widgets to
        )
        self.filter_algorithm_panels['Lowpass'] = widgets['adjust_filter_Lowpass_algorithm'].master.master  # get the frame
        self.filter_algorithm_panels['Lowpass'].grid_remove()

        # parameter inputs for each filtering
        self.filter_parameter_panels = {}

        self.widgets['adjust_filter_width'] = self.frame.insert_label_entry(
            name='adjust_filter_width',
            label='Filter width (kernel)',
            validate_type='int',
            separator=False
        )
        self.filter_parameter_panels['width'] = self.widgets['adjust_filter_width'].master.master
        self.filter_parameter_panels['width'].grid_remove()
        # note for future additions:
        # widgets that takes user input for filtering parameters should be named 'adjust_filter_<param name>'
        # the value of the widget must be retrievable using widget.get()
        # the same param name should be used in the algorithm's filter_param_list below

        # list the parameters that should be shown for each filtering method
        self.filter_param_list = {'Boxcar': ['width'], 'None': []}

        self.filter_apply_button = self.frame.insert_button(
            text='Apply',
            command=self.filter
        )

        self._populate_filter_algorithm_choices()

    def adjust_baseline(self, e=None):
        all_channels = True
        if self.widgets['adjust_channel'].get():
            all_channels = False

        try:
            xlim = (float(self.widgets['adjust_range_left'].get()),
                    float(self.widgets['adjust_range_right'].get()))
        except:
            xlim = None
        try:
            fixed_val = float(self.widgets['adjust_fixed'].get())
        except:
            fixed_val = None
        mode = self.widgets['adjust_baseline_mode'].get()
        interface.adjust_baseline(all_channels, target=self.widgets['adjust_target'].get(),
                                  mode=mode,
                                  xlim=xlim,
                                  fixed_val=fixed_val
                                  )

    def average_trace(self, e=None):
        if self.widgets['adjust_channel'].get():
            all_channels = False
        else:
            all_channels = True

        interface.average_y_data(all_channels=all_channels,
                                 target=self.widgets['adjust_target'].get(),
                                 report_minmax=self.widgets['adjust_avg_min_max'].get(),
                                 limit_minmax_window=self.widgets['adjust_avg_window'].get(),
                                 hide_all=self.widgets['adjust_avg_show_result'].get())

    def filter(self, e=None):
        if self.widgets['adjust_channel'].get():
            all_channels = False
        else:
            all_channels = True

        lohi = self.widgets['adjust_filter_lohi'].get()
        mode = self.widgets['adjust_filter_{}_algorithm'.format(lohi)].get()
        params = {}
        for key in self.filter_param_list[mode]:
            params[key] = self.widgets[f'adjust_filter_{key}'].get()

        interface.filter_y_data(all_channels, target=self.widgets['adjust_target'].get(),
                                mode=mode, params=params)

    def _populate_filter_algorithm_choices(self, e=None):
        for key in filter_algorithm_panels:
            filter_algorithm_panels[key].grid_remove()
        for key in filter_parameter_panels:
            filter_parameter_panels[key].grid_remove()

        lohi = widgets['adjust_filter_lohi'].get()  # user choice beween lowpass and highpass filtering
        filter_algorithm_panels[lohi].grid()  # place the appropriate algorithm optionmenu based on user choice

        algorithm = widgets[f'adjust_filter_{lohi}_algorithm'].get()  # algorithm chosen by the user
        _populate_filter_param_form(algorithm)

    def _populate_filter_param_form(self, algorithm=None):
        for param in filter_param_list[algorithm]:
            filter_parameter_panels[param].grid()

    def _select_baseline_mode(self):
        if self.widgets['adjust_baseline_mode'].get() == 'mean':
            self.widgets['adjust_range_left'].config(state='disabled')
            self.widgets['adjust_range_right'].config(state='disabled')
            self.widgets['adjust_fixed'].config(state='disabled')
            return
        if self.widgets['adjust_baseline_mode'].get() == 'range':
            self.widgets['adjust_range_left'].config(state='normal')
            self.widgets['adjust_range_right'].config(state='normal')
            self.widgets['adjust_fixed'].config(state='disabled')
            return
        if self.widgets['adjust_baseline_mode'].get() == 'fixed':
            self.widgets['adjust_range_left'].config(state='disabled')
            self.widgets['adjust_range_right'].config(state='disabled')
            self.widgets['adjust_fixed'].config(state='normal')
        pass

global widgets
widgets = {}


def load(parent):
    optionframe = ScrollableOptionFrame(parent)  # scrolling outer frame

    frame = optionframe.frame  # inner frame that will contain all the widgets

    frame.insert_title(text='Adjust Trace', separator=True)

    # ------
    frame.insert_title(text='General Setting', separator=False)
    global widgets
    widgets['adjust_target'] = frame.insert_label_optionmenu(
        name='adjust_target',
        label='Apply adjustment to (overlay mode only):',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )
    widgets['adjust_channel'] = frame.insert_label_checkbox(
        name='adjust_channel',
        label='Apply adjustment to visible channel only',
        onvalue='1',
        offvalue="",
        separator=False
    )
    frame.insert_separator()
    # -------
    # Baseline subtraction section

    frame.insert_title(text='Baseline Subtraction', separator=False)
    frame.insert_title(text='Perform baseline subtraction using:', separator=False)

    baseline_panel = OptionFrame(frame)
    baseline_panel.grid_columnconfigure(0, weight=1)
    frame.insert_widget(baseline_panel)

    widgets['adjust_baseline_mode'] = StringVar(baseline_panel, config.adjust_baseline_mode)
    global baseline_option_buttons
    baseline_option_buttons = {}

    baseline_option_buttons['mean'] = ttk.Radiobutton(
        baseline_panel,
        text='Mean of all target sweeps',
        value='mean',
        command=_select_baseline_mode,
        variable=widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_option_buttons['mean'])

    baseline_option_buttons['range'] = ttk.Radiobutton(
        baseline_panel,
        text='Mean of range (x-axis) per sweep:',
        value='range',
        command=_select_baseline_mode,
        variable=widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_option_buttons['range'])

    panel = Tk.Frame(baseline_panel)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_columnconfigure(1, weight=1)
    widgets['adjust_range_left'] = widget.VarEntry(parent=panel, name='adjust_range_left', validate_type='float')
    widgets['adjust_range_left'].grid(column=0, row=0, sticky='news')

    widgets['adjust_range_right'] = widget.VarEntry(parent=panel, name='adjust_range_right', validate_type='float')
    widgets['adjust_range_right'].grid(column=1, row=0, sticky='news')
    baseline_panel.insert_widget(panel)

    baseline_option_buttons['fixed'] = ttk.Radiobutton(
        baseline_panel,
        text='Fixed value:',
        value='fixed',
        command=_select_baseline_mode,
        variable=widgets['adjust_baseline_mode']
    )
    baseline_panel.insert_widget(baseline_option_buttons['fixed'])

    widgets['adjust_fixed'] = widget.VarEntry(parent=baseline_panel, name='adjust_fixed', validate_type='float')
    print(f'checking pre-set value: {config.adjust_fixed} for adjust_fixed')
    baseline_panel.insert_widget(widgets['adjust_fixed'])

    frame.insert_button(
        text='Apply',
        command=adjust_baseline
    )

    # set baseline adjustment method to saved option
    baseline_option_buttons[config.adjust_baseline_mode].invoke()

    frame.insert_separator()
    #------
    # Trace Averaging

    frame.insert_title(text='Trace Averaging', separator=False)
    widgets['adjust_avg_show_result'] = frame.insert_label_checkbox(
        name='adjust_avg_show_result',
        label='Only show resultant trace (hide original sweeps)',
        onvalue='1',
        offvalue="",
        separator=False
    )
    widgets['adjust_avg_min_max'] = frame.insert_label_checkbox(
        name='adjust_avg_min_max',
        label='Output min/max',
        onvalue='1',
        offvalue="",
        separator=False
    )
    widgets['adjust_avg_window'] = frame.insert_label_checkbox(
        name='adjust_avg_window',
        label='Limit min/max to within trace window',
        onvalue='1',
        offvalue='',
        separator=False
    )
    frame.insert_button(
        text='Apply',
        command=average_trace
    )
    frame.insert_separator()

    #-------
    # Filtering

    frame.insert_title(text='Trace Filtering', separator=False, justify=Tk.LEFT)
    # create low vs high pass option menu

    # lohi_panel = widget.create_label_var_widget(widget.VarOptionmenu, frame, label='Filtering method:',
    #                                             options=['Lowpass', 'Highpass'], command=print)
    # frame.insert_widget(lohi_panel)
    #
    # lowpass_algorithm_panel = widget.create_label_var_widget(widget.VarOptionmenu, frame, label='Filtering algorithm:',
    #                                                          options=['Boxcar'], command=print)
    # frame.insert_widget(lowpass_algorithm_panel)
    # lowpass_algorithm_panel.grid_remove()
    #
    # highpass_algorithm_panel = widget.create_label_var_widget(widget.VarOptionmenu, frame,
    #                                                           label='Filetering algorithm:',
    #                                                           options=[''], command=print)
    #
    # frame.insert_widget(highpass_algorithm_panel)
    # highpass_algorithm_panel.grid_remove()

    # algorithm specific panels

    widgets['adjust_filter_lohi'] = frame.insert_label_optionmenu(
        name='adjust_filter_lohi',
        label='Filtering method:',
        options=['Lowpass'],
        separator=False,
        command=_populate_filter_algorithm_choices
    )

    # create algorithm choices for filtering
    global filter_algorithm_panels
    filter_algorithm_panels = {}
    global lowpass_options

    widgets['adjust_filter_Lowpass_algorithm'] = frame.insert_label_optionmenu(
        name='adjust_filter_Lowpass_algorithm',
        label='Lowpass algorithm:',
        options=['Boxcar'],
        separator=False,
        command=_populate_filter_param_form # populate widgets to
    )
    filter_algorithm_panels['Lowpass'] = widgets['adjust_filter_Lowpass_algorithm'].master.master # get the frame
    filter_algorithm_panels['Lowpass'].grid_remove()

    # parameter inputs for each filtering
    global filter_parameter_panels
    filter_parameter_panels = {}

    widgets['adjust_filter_width'] = frame.insert_label_entry(
        name='adjust_filter_width',
        label='Filter width (kernel)',
        validate_type='int',
        separator=False
    )
    filter_parameter_panels['width'] = widgets['adjust_filter_width'].master.master
    filter_parameter_panels['width'].grid_remove()
    # note for future additions:
    # widgets that takes user input for filtering parameters should be named 'adjust_filter_<param name>'
    # the value of the widget must be retrievable using widget.get()
    # the same param name should be used in the algorithm's filter_param_list below

    # list the parameters that should be shown for each filtering method
    global filter_param_list
    filter_param_list = {'Boxcar':['width'], 'None':[]}

    global filter_apply_button
    filter_apply_button = frame.insert_button(
        text='Apply',
        command=filter
    )

    _populate_filter_algorithm_choices()

    return optionframe


def _populate_filter_algorithm_choices(e=None):
    for key in filter_algorithm_panels:
        filter_algorithm_panels[key].grid_remove()
    for key in filter_parameter_panels:
        filter_parameter_panels[key].grid_remove()

    lohi = widgets['adjust_filter_lohi'].get() # user choice beween lowpass and highpass filtering
    filter_algorithm_panels[lohi].grid() # place the appropriate algorithm optionmenu based on user choice

    algorithm = widgets[f'adjust_filter_{lohi}_algorithm'].get() # algorithm chosen by the user
    _populate_filter_param_form(algorithm)


def _populate_filter_param_form(algorithm=None):
    for param in filter_param_list[algorithm]:
        filter_parameter_panels[param].grid()


######### Baseline Adjust
def _select_baseline_mode(e=None, undo=True):
    if widgets['adjust_baseline_mode'].get() == 'mean':
        print('mean')
        widgets['adjust_range_left'].config(state='disabled')
        widgets['adjust_range_right'].config(state='disabled')
        widgets['adjust_fixed'].config(state='disabled')
        return
    if widgets['adjust_baseline_mode'].get() == 'range':
        print('range')
        widgets['adjust_range_left'].config(state='normal')
        widgets['adjust_range_right'].config(state='normal')
        widgets['adjust_fixed'].config(state='disabled')
        return
    if widgets['adjust_baseline_mode'].get() == 'fixed':
        print('fixed')
        widgets['adjust_range_left'].config(state='disabled')
        widgets['adjust_range_right'].config(state='disabled')
        widgets['adjust_fixed'].config(state='normal')


def adjust_baseline(e=None):
    if app.widgets['trace_mode'].get() == 'compare':
        return None
    all_channels = True
    if widgets['adjust_channel'].get():
        all_channels = False

    try:
        xlim = (float(widgets['adjust_range_left'].get()),
                float(widgets['adjust_range_right'].get()))
    except:
        xlim = None
    try:
        fixed_val = float(widgets['adjust_fixed'].get())
    except:
        fixed_val = None
    mode = widgets['adjust_baseline_mode'].get()
    interface.adjust_baseline(all_channels, target=widgets['adjust_target'].get(),
                              mode=mode,
                              xlim=xlim,
                              fixed_val=fixed_val
                              )


#### Trace Averaging #####
def average_trace(e=None):
    if app.widgets['trace_mode'].get() != 'overlay':
        return None
    if widgets['adjust_channel'].get():
        all_channels = False
    else:
        all_channels = True

    interface.average_y_data(all_channels=all_channels,
                             target=widgets['adjust_target'].get(),
                             report_minmax=widgets['adjust_avg_min_max'].get(),
                             limit_minmax_window=widgets['adjust_avg_window'].get(),
                             hide_all=widgets['adjust_avg_show_result'].get())


#### Filtering #####
def filter(e=None):
    if app.widgets['trace_mode'].get() == 'compare':
        return None
    if widgets['adjust_channel'].get():
        all_channels = False
    else:
        all_channels = True

    lohi = widgets['adjust_filter_lohi'].get()
    mode = widgets['adjust_filter_{}_algorithm'.format(lohi)].get()
    params = {}
    for key in filter_param_list[mode]:
        params[key] = widgets[f'adjust_filter_{key}'].get()

    interface.filter_y_data(all_channels, target=widgets['adjust_target'].get(),
                            mode=mode, params=params)
