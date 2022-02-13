from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire.utils import custom_widgets
from . import process_recording
from simplyfire import app
import os
import tkinter as Tk

name = 'process_recording'
menu_label = 'Process Recording'
tab_label = 'Process'

baseline_option_panels={}
filter_choices = ['Highpass', 'Lowpass']
lowpass_algorithms = ['Boxcar', 'Test']
filter_param_set = {'Boxcar':['width']} # list the parameters required for each algorithm
filter_params = {} # populate parameters and widgets requried for different filtering options

#### default values ####
baseline_range_left = 0
baseline_range_right= 1
baseline_fixed = 0
sweep_target = 'All sweeps'
channel_target = '1'
baseline_mode = 'Mean of all targets'
filter_algorithm = 'Lowpass'
average_show_result = '1'
width = 11
filter_Lowpass_algorithm = 'Boxcar'
filter_Highpass_algorithm = 'Not yet supported'



#### define functions ####
# private functions
def _default_averaging_params(event=None):
    form.set_to_default(filter='average')
    app.interface.focus()

def _default_baseline_params(event=None):
    form.set_to_default(filter='baseline')
    _select_baseline_mode()
    app.interface.focus()

def _default_filter_params(event=None):
    form.set_to_default(filter='filter')
    _select_filter_mode()
    app.interface.focus()

def _select_baseline_mode(event=None):
    selection = form.inputs['baseline_mode'].get()
    for key in baseline_option_panels:
        if key != selection:
            baseline_option_panels[key].grid_remove()
        else:
            baseline_option_panels[key].grid()
    app.interface.focus()

def _select_filter_mode(event=None):
    choice = form.inputs['filter_algorithm'].get()
    non_choices = [i for i in filter_choices if i != choice]
    # show all or hide all relevant widgets to the filter mode
    for w in form.inputs.keys():
        if choice in w:
            form.show_widget(widgetname=w)
        else:
            for other in non_choices:
                if other in w:
                    form.hide_widget(widgetname=w)
    # hide all parameter related frames
    for w in filter_params:
        form.hide_widget(w)

    if choice.lower() == 'highpass':
        _select_highpass_algorithm()
    else:
        _select_lowpass_algorithm()
    app.interface.focus()


def _select_lowpass_algorithm(event=None):
    choice = form.inputs['filter_Lowpass_algorithm'].get()
    for w in filter_params:
        form.hide_widget(w)
    if choice == 'Boxcar':
        for key in filter_param_set[choice]:
            form.show_widget(key)



def _select_highpass_algorithm(event=None):
    pass

# processing functions
def average_sweeps(event=None):
    if app.inputs['trace_mode'].get() == 'continuous':
        return
    if form.inputs['channel_target'].get():
        target_channels = [app.interface.current_channel]
    else:
        target_channels = range(app.interface.recordings[0].channel_count)
    target_sweeps = []
    if form.inputs['sweep_target'].get() == 'All sweeps':
        target_sweeps = range(app.interface.recordings[0].sweep_count)
    # elif form.inputs['sweep_target'].get() == 'Visible sweeps':
    #     target_sweeps = app.plugin_manager.sweeps.sweeps_GUI.get_visible_sweeps()
    #     if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
    #         target_sweeps = range(app.interface.recordings[0].sweep_count)
    #     elif app.inputs['trace_mode'].get() == 'overlay':
    #         # account for more recordings being open (consider only the main file open)
    #         target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    elif form.inputs['sweep_target'].get() == 'Highlighted sweeps':
        target_sweeps = app.modules['sweeps'].control_tab.get_highlighted_sweeps()
        # account for more recordings being open (consider only the main file open)
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get() == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    avg_sweep = process_recording.average_sweeps(app.interface.recordings[0],
                                       channels=target_channels,
                                       sweeps=target_sweeps)
    if app.interface.is_accepting_undo():
        sweep_list = tuple(app.plugin_manager.sweeps.sweep_GUI.get_visible_sweeps())
        controller.add_undo(
            [
                app.interface.recordings[0].delete_last_sweep,
                app.interface.plot,
                app.plugin_manager.sweeps.sweep_GUI.synch_sweep_list,
                'test tentry string!',
                lambda l=sweep_list, u=False: app.modules['sweeps'].control_tab.show_list(selection=l, undo=u)
            ]
        )
    app.interface.recordings[0].append_sweep(avg_sweep)
    app.interface.plot(fix_x=True, fix_y=True)
    app.modules['sweeps'].control_tab.synch_sweep_list()
    if form.inputs['average_show_result'].get():
        app.modules['sweeps'].control_tab.hide_all(undo=False)
        app.modules['sweeps'].control_tab.show_list(selection=[app.interface.recordings[0].sweep_count - 1], undo=False)

def subtract_baseline(event=None):
    if len(app.interface.recordings)==0:
        return None # nothing to process
    if form.inputs['channel_target'].get():
        target_channels = [app.interface.current_channel]
    else:
        target_channels = range(app.interface.recordings[0].channel_count)
    xlim = None
    if form.inputs['baseline_mode'].get() == 'Mean of x-axis range':
        try:
            xlim = (float(form.inputs['baseline_range_left'].get()),
                    float(form.inputs['baseline_range_right'].get()))
        except:
            pass

    shift = None
    if form.inputs['baseline_mode'].get() == 'Fixed value':
        shift = float(form.inputs['baseline_fixed'].get())

    target_sweeps = []
    if form.inputs['sweep_target'].get() == 'All sweeps':
        target_sweeps = range(app.interface.recordings[0].sweep_count)
    elif form.inputs['sweep_target'].get() == 'Visible sweeps':
        target_sweeps = app.plugin_manager.sweeps.sweeps_GUI.get_visible_sweeps()
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get () == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    elif form.inputs['sweep_target'].get() == 'Highlighted sweeps':
        target_sweeps = app.plugin_manager.sweeps.sweeps_GUI.get_highlighted_sweeps()
        # account for more recordings being open (consider only the main file open)
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get () == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    if len(target_sweeps) == 0:
        return
    plot_mode = app.inputs['trace_mode'].get()
    result, baseline = process_recording.subtract_baseline(app.interface.recordings[0],
                                                 plot_mode=plot_mode,
                                                 channels=target_channels,
                                                 sweeps=target_sweeps,
                                                 xlim=xlim,
                                                 shift=shift)

    #['All sweeps', 'Visible sweeps', 'Highlighted sweeps']
    # deal with undo later
    if app.interface.is_accepting_undo():
        controller.add_undo([
            lambda r=app.interface.recordings[0], s=baseline, m=plot_mode, c=target_channels,
                   t=target_sweeps: process_recording.shift_y_data(r, s, m, c, t),
            app.interface.plot
        ])

    app.interface.plot(fix_x=True)
    pass

def filter_data(event=None):
    if len(app.interface.recordings)==0:
        return None # nothing to process
    if form.inputs['channel_target'].get():
        target_channels = [app.interface.current_channel]
    else:
        target_channels = range(app.interface.recordings[0].channel_count)

    target_sweeps = []
    if form.inputs['sweep_target'].get() == 'All sweeps':
        target_sweeps = range(app.interface.recordings[0].sweep_count)
    elif form.inputs['sweep_target'].get() == 'Visible sweeps':
        target_sweeps = app.plugin_manager.sweeps.sweeps_GUI.get_visible_sweeps()
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get() == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    elif form.inputs['sweep_target'].get() == 'Highlighted sweeps':
        target_sweeps = app.plugin_manager.sweeps.sweeps_GUI.get_highlighted_sweeps()
        # account for more recordings being open (consider only the main file open)
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get() == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]

    if app.interface.is_accepting_undo():
        temp_filename = app.interface.get_temp_filename()
        app.interface.recordings[0].save_y_data(filename=temp_filename,
                                                channels=target_channels,
                                                sweeps=target_sweeps)
        controller.add_undo([
            lambda f=temp_filename, c=target_channels, s=target_sweeps: app.interface.recordings[0].load_y_data(f,c,s),
            app.interface.plot,
            lambda f=temp_filename:os.remove(f)
        ])
    filter_choice = form.inputs['filter_algorithm'].get()
    filter_algorithm = form.inputs[f'filter_{filter_choice}_algorithm'].get()
    params = {}
    for key in filter_param_set[filter_algorithm]:
        params[key] = form.inputs[key].get()

    # deal with undo later

    getattr(process_recording, f'filter_{filter_algorithm}')(app.interface.recordings[0],
                                                   params,
                                                   target_channels,
                                                   target_sweeps)
    app.interface.plot(fix_x=True, fix_y=True)



#### Make GUI Components ####
controller = PluginController(name=name,
                              menu_label=menu_label)
form = PluginForm(plugin_controller=controller,
                  tab_label=tab_label,
                  scrollbar=True,
                  notebook=app.cp_notebook)

#### Set up Form GUI ####
form.insert_title(text='Process Recording')
form.insert_title(text='Target setting', separator=False)
form.insert_title(text='Apply processing to the following sweeps', separator=False)

form.insert_label_optionmenu(
    name='sweep_target',
    text='',
    options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
    separator=False,
    default=sweep_target
)
form.insert_label_checkbox(
    name='channel_target',
    text='Limit process to the current channel',
    onvalue='1',
    offvalue='',
    separator=True,
    default=channel_target
)
form.insert_title(text='Baseline Subtraction', separator=False)
form.insert_title(text='Calculate baseline using:', separator=False)

form.insert_label_optionmenu(
    name='baseline_mode',
    text='',
    options=['Mean of all targets', 'Mean of x-axis range', 'Fixed value'],
    command=_select_baseline_mode,
    separator=False,
    default=baseline_mode
)

baseline_option_panels['Mean of all targets'] = form.make_panel(separator=False)
baseline_option_panels['Mean of x-axis range'] = form.make_panel(separator=False)

panel = Tk.Frame(baseline_option_panels['Mean of x-axis range'])
panel.grid(row=0, column=0, sticky='news')
panel.grid_columnconfigure(0, weight=1)
panel.grid_columnconfigure(1, weight=1)

form.inputs['baseline_range_left'] = custom_widgets.VarEntry(parent=panel, name='baseline_range_left',
                                                              validate_type='float',
                                                              default=baseline_range_left)
form.inputs['baseline_range_left'].grid(column=0, row=0, sticky='news')
form.inputs['baseline_range_right'] = custom_widgets.VarEntry(parent=panel, name='baseline_range_rigjt',
                                                               validate_type='float',
                                                               default=baseline_range_right)
form.inputs['baseline_range_right'].grid(column=1, row=0, sticky='news')

baseline_option_panels['Fixed value'] = form.make_panel(separator=False)
panel = Tk.Frame(baseline_option_panels['Fixed value'])
panel.grid_columnconfigure(0, weight=1)
panel.grid(row=0, column=0, sticky='news')

form.inputs['baseline_fixed'] = custom_widgets.VarEntry(parent=panel, name='baseline_fixed',
                                                         validate_type='float',
                                                         default=baseline_fixed)
form.inputs['baseline_fixed'].grid(row=0, column=0, sticky='news')

form.insert_button(text='Apply', command=subtract_baseline)
form.insert_button(text='Default', command=_default_baseline_params)

form.insert_separator()

form.insert_title(
    text='Average sweeps',
    separator=False,
)
form.insert_label_checkbox(
    name='average_show_result',
    text='Hide original sweeps',
    onvalue='1',
    offvalue='',
    separator=False,
    default=average_show_result
)
form.insert_button(
    text='Apply',
    command=average_sweeps
)
form.insert_button(
    text='Default',
    command=_default_averaging_params
)
form.insert_separator()
form.insert_title(
    text='Filtering',
    separator=False
)

form.insert_label_optionmenu(
    name='filter_algorithm',
    text="Select low or high pass:",
    options=filter_choices,
    separator=False,
    command=_select_filter_mode,
    default=filter_algorithm
)

form.insert_label_optionmenu(
    name='filter_Lowpass_algorithm',
    text='Algorithm:',
    options=lowpass_algorithms,
    separator=False,
    command=_select_lowpass_algorithm,
    default=filter_Lowpass_algorithm
)

# algorithm specific parameters
filter_params['width'] = form.insert_label_entry(
    name='width',
    text='Width',
    validate_type='int',
    default=width
)
form.inputs['width'].bind('<Return>', app.interface.focus)

highpass_algorithms = ['Not yet supported']
form.insert_label_optionmenu(
    name='filter_Highpass_algorithm',
    text='Algorithm:',
    options=highpass_algorithms,
    separator=False,
    command=_select_highpass_algorithm,
    default=filter_Highpass_algorithm
)

form.insert_button(text='Apply', command=filter_data)
form.insert_button(text='Default', command=_default_filter_params)
#

#### populate Batch processing ####

controller.create_batch_category()
controller.add_batch_command('Apply baseline subtraction', subtract_baseline)
controller.add_batch_command('Average sweeps', average_sweeps)
controller.add_batch_command('Filter recording', filter_data)


controller.load_values()
_select_baseline_mode()
_select_filter_mode()