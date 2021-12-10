from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import app
from DataVisualizer import data_display, trace_display, log_display
from Backend import interface
changed = True
changes = {}
parameters = {}

global widgets
widgets = {}
def find_all():
    interface.find_mini_in_range(trace_display.default_xlim, trace_display.default_ylim)

def find_in_window():
    interface.find_mini_in_range(trace_display.ax.get_xlim(), trace_display.ax.get_ylim())

def filter_all():
    interface.filter_mini()
def filter_in_window():
    interface.filter_mini(trace_display.ax.get_xlim())
def load(parent):
    global widgets
    ##################################################
    #                    Methods                     #
    ##################################################
    def _show_all():
        for key in optionframe.get_keys(filter='data_display_'):
            optionframe.widgets[key].set(1)
        data_display.show_columns(extract_columns2display())

    def _hide_all():
        for key in optionframe.get_keys(filter='data_display_'):
            optionframe.widgets[key].set('')
        data_display.show_columns(extract_columns2display())
    def apply_parameters(e=None):
        global changed
        for i in parameters:
            if parameters[i] != app.widgets[i].get():
                changes[i] = app.widgets[i].get()
                changed = True

    # frame = ScrollableOptionFrame(parent)

    ##################################################
    #          Populate detector option tab          #
    ##################################################
    """
    Populates the detector tab in the control panel.
    :param frame:
    :return:
    """
    frame = ScrollableOptionFrame(parent)
    optionframe = frame.frame

    ##################################################
    #              Detector parameters               #
    ##################################################
    optionframe.insert_title(
        name='detector',
        text='Mini analysis mode'
    )

    # mini analysis core parameters
    optionframe.insert_title(
        text='core parameters'
    )
    widgets['detector_core_direction'] = optionframe.insert_label_optionmenu(
        name='detector_core_direction',
        label='Direction',
        options=['positive', 'negative']
    )
    # the keys will be used to export parameters to interface during mini search (see extract_mini_parameters())
    global core_params
    core_params = {
        'manual_radius': {'id': 'detector_core_search_radius',
                          'label': 'Search radius in % of visible x-axis (Manual)', 'validation': 'float', 'conversion':float},
        'auto_radius': {'id':'detector_core_auto_radius',
                        'label':'Search window in ms (Auto)', 'validation':'float', 'conversion': float},
        # 'delta_x': {'id': 'detector_core_deltax',
        #             'label':'Points before peak to estimate baseline (input 0 to ignore this factor)',
        #             'validation':'positive_int/zero',
        #             'conversion': int},
        'lag_ms': {'id': 'detector_core_lag',
                            'label': 'Window of data points averaged to find start of mini (ms):',
                            'validation': 'float', 'conversion':float},
        'lag_end_ms': {'id': 'detector_core_lag_end',
                    'label': 'Window of data points averaged to find end of mini (ms):',
                    'validation': 'float',
                    'conversion': float}, # convert to ms later
        # 'max_points_decay': {'id': 'detector_core_max_points_decay',
        #                      'label': 'Maximum data points after peak to consider for decay', 'validation': 'int'},
        'min_peak2peak': {'id': 'detector_core_min_peak2peak',
                          'label':'Minimum interval between peaks (ms)', 'validation':'float'}
    }

    for k, d in core_params.items():
        widgets[d['id']] = optionframe.insert_label_entry(
            name=d['id'],
            label=d['label'],
            validate_type=d['validation']
        )
        widgets[d['id']].bind('<Return>', apply_parameters, add='+')
        widgets[d['id']].bind('<FocusOut>', apply_parameters, add='+')
        parameters[d['id']] = widgets[d['id']].get()
        changes[d['id']] = widgets[d['id']].get()

    widgets['detector_compound'] = optionframe.insert_label_checkbox(
        name='detector_core_compound',
        label='Analyze compound minis',
        onvalue=1,
        offvalue=0,
        command=toggle_compound_params # toggles activation state of compound-analysis param widgets
    )
    global compound_params
    compound_params = {
        # 'extrapolation_length': {'id': 'detector_core_extrapolation_length',
        #                   'label': 'Number of points after previous peak to extrapolate decay', 'validation': 'int',
        #                   'conversion': int},
        'p_valley': {'id': 'detector_core_p_valley',
                        'label': 'Minimum valley size in % of peak amplitude', 'validation': 'float',
                        'conversion': float},
        'max_compound_interval': {'id': 'detector_core_max_compound_interval',
                                'label': 'Maximum interval between two peaks to use compound mini analysis (ms)',
                                'validation':'float', 'conversion': float},

    }
    for k, d in compound_params.items():
        widgets[d['id']] = optionframe.insert_label_entry(
            name=d['id'],
            label=d['label'],
            validate_type=d['validation']
        )
        widgets[d['id']].bind('<Return>', apply_parameters, add='+')
        widgets[d['id']].bind('<FocusOut>', apply_parameters, add='+')
        parameters[d['id']] = widgets[d['id']].get()
        changes[d['id']] = widgets[d['id']].get()

    toggle_compound_params() # set state of compound param widgets

    widgets['detector_core_update_events'] = optionframe.insert_label_checkbox(
        name='detector_core_update_events',
        label='Update graph after each event detection during automated search (will slow down search)',
    )

    optionframe.insert_button(
        text='Apply',
        command=trace_display.canvas.get_tk_widget().focus_set
    )
    optionframe.insert_button(
        text='Default',
        command=lambda k='detector_core_': optionframe.default(filter=k)
    )
    optionframe.insert_button(
        text='Find all',
        command=find_all  # link this later
    )
    optionframe.insert_button(
        text='Delete all',
        command=None  # link this later
    )
    optionframe.insert_button(
        text='Find in \nwindow',
        command=find_in_window  # link this later
    )
    optionframe.insert_button(
        text='Delete in \nwindow',
        command=None  # link this later
    )
    # mini filtering (min and max values) options
    optionframe.insert_title(
        text='Filtering options'
    )
    # the keys will be used to export parameters to interface during mini search (see extract_mini_parameters())
    global filter_params
    filter_params={
        'min_amp': {'id': 'detector_filter_min_amp',
                    'label':'Minimum amplitude (absolute value) (y-axis unit):',
                    'validation': 'float/None', 'conversion':float},
        'max_amp': {'id': 'detector_filter_max_amp',
                    'label':'Maximum amplitude (absolute value) (y-axis unit):',
                    'validation': 'float/None', 'conversion':float},
        'min_decay': {'id': 'detector_filter_min_decay',
                      'label': 'Minimum decay constant (tau) (ms)', 'validation': 'float/None', 'conversion':float},
        'max_decay': {'id': 'detector_filter_max_decay', 'label': 'Maximum decay constant (tau) (ms)', 'validation':'float/None', 'conversion':float},
        'min_hw': {'id':'detector_filter_min_hw', 'label':'Minimum halfwidth (ms)', 'validation':'float/None', 'conversion':float},
        'max_hw':{'id':'detector_filter_max_hw', 'label':'Maximum halfwidth (ms)', 'validation':'float/None', 'conversion':float},
        'min_rise':{'id':'detector_filter_min_rise', 'label':'Minimum rise constant (ms)', 'validation':'float/None', 'conversion':float},
        'max_rise':{'id':'detector_filter_max_rise', 'label':'Maximum rise constant (ms)', 'validation':'float/None', 'conversion':float},
        'min_drr':{'id':'detector_filter_min_dr', 'label':'Minimum decay:rise ratio', 'validation':'float/None', 'conversion':float},
        'max_drr':{'id':'detector_filter_max_dr', 'label':'Maximum decay:rise ratio', 'validation':'float/None', 'conversion':float}
    }
    for k, d in filter_params.items():
        widgets[d['id']] = optionframe.insert_label_entry(
            name=d['id'],
            label=d['label'],
            validate_type=d['validation']
        )
        widgets[d['id']].bind('<Return>', apply_parameters, add='+')
        widgets[d['id']].bind('<FocusOut>', apply_parameters, add='+')
        parameters[d['id']] = widgets[d['id']].get()
        changes[d['id']] = widgets[d['id']].get()
    optionframe.insert_button(
        text='Confim',
        command=trace_display.canvas.get_tk_widget().focus_set
    )
    optionframe.insert_button(
        text='Default',
        command=lambda k='detector_filter_': optionframe.default(filter=k)
    )
    optionframe.insert_button(
        text='Apply filter\n(all)',
        command=filter_all,  # link this later,
    )
    optionframe.insert_button(
        text='Apply filter\n(window)',
        command=filter_in_window  # link this later
    )
    # panel = frame.make_panel()
    # Tk.Label(panel, text='Fit decay functions using:').grid(column=0, row=0, sticky='news')
    # app.widgets['detector_decay_func_type'] = widget.VarWidget(name='detector_decay_func_type')
    #
    # op_frame = Tk.Frame(panel)
    # op_frame.grid(column=0, row=1, sticky='news')
    # op_frame.grid_rowconfigure(0, weight=1)
    # for i in range(3):
    #     op_frame.grid_columnconfigure(i, weight=1)
    # buttons = [
    #     ('Single', '1'),
    #     ('Double', '2'),
    #     ('Triple', '3'),
    #     # ('Rise-decay', '4') NOT SUPPORTED
    # ]
    # for i, b in enumerate(buttons):
    #     ttk.Radiobutton(op_frame, text=b[0], variable=app.widgets['detector_decay_func_type'].var,
    #                    value=b[1], command=apply_parameters).grid(column=i, row=0, sticky='news')
    #
    # app.widgets['detector_decay_func_constant'] = frame.insert_label_checkbox(name='detector_decay_func_constant',
    #                                                                              label='Add a constant',
    #                                                                              onvalue='1',
    #                                                                              offvalue="",
    #                                                                              command=apply_parameters)



    ##################################################
    #                  Data Export                   #
    ##################################################
    # frame.insert_title(
    #     name='data_export',
    #     text='Data Export'
    # )
    # app.widgets['data_export_all'] = frame.insert_label_checkbox(
    #     name='data_export_all',
    #     label='Export all visible and hidden data?',
    #     onvalue=1,
    #     offvalue=-1
    #     # command=None #Link this to exporting data sets
    # )

    ##################################################
    #                  Data Display                  #
    ##################################################
    # all column display options for the data table must start with "data_display_"

    optionframe.insert_title(
        name='dataframe',
        text='Data Table Display'
    )

    global boxes
    boxes = [
        ('data_display_time', 'Peak time'),
        ('data_display_amplitude', 'Amplitude'),
        ('data_display_decay', 'Decay constant'),
        # ('data_display_decay_func', 'Decay function'),
        ('data_display_rise', 'Rise duration'),
        ('data_display_halfwidth', 'Halfwidth'),
        ('data_display_baseline', 'Baseline'),
        # ('data_display_start', 'Start time'),
        # ('data_display_end', 'End time'),
        ('data_display_channel', 'Channel'),
        ('data_display_direction', 'Direction'),
        ('data_display_compound', 'Compound')
    ]
    def apply_columns():
        data_display.show_columns(extract_columns2display())

    for i in boxes:
        widgets[i[0]] = optionframe.insert_label_checkbox(
            name=i[0],
            label=i[1],
            command=apply_columns,
            onvalue='1',
            offvalue=''
        )

    apply_columns()
    optionframe.insert_button(
        text='Show All',
        command=_show_all
    )
    optionframe.insert_button(
        text='Hide All',
        command=_hide_all
    )
    optionframe.insert_button(
        text='Fit columns',
        command=data_display.fit_columns
    )

    return frame

def populate_data_display():
    try:
        xs = interface.mini_df.index.where(interface.mini_df['channel'] == analyzer2.trace_file.channel)
        xs = xs.dropna()
        data_display.set(interface.mini_df.loc[xs])
    except: # file not loaded yet
        pass

def extract_mini_parameters():
    params = {}
    params['direction'] = {'negative':-1, 'positive':1}[widgets['detector_core_direction'].get()] # convert direction to int value
    params['update'] = widgets['detector_core_update_events'].get()
    params['compound'] = int(widgets['detector_compound'].get())
    global core_params
    global filter_params
    for k, d in core_params.items():
        try:
            params[k] = d['conversion'](widgets[d['id']].get())
        except:
            if widgets[d['id']].get() == 'None':
                params[k] = None
            else:
                params[k] = widgets[d['id']].get()
    for k, d in filter_params.items():
        try:
            params[k] = d['conversion'](widgets[d['id']].get())
        except:
            if widgets[d['id']].get() == 'None':
                params[k] = None
            else:
                params[k] = widgets[d['id']].get()
    if params['compound']:
        for k, d in compound_params.items():
            params[k] = widgets[d['id']].get()
    return params

def extract_filter_parameters():
    params={}
    global filter_params
    for k, d in filter_params.items():
        try:
            params[k] = d['conversion'](widgets[d['id']].get())
        except:
            if widgets[d['id']].get() == 'None':
                params[k] = None
            else:
                params[k] = widgets[d['id']].get()
    return params

def extract_columns2display():
    columns = []
    for b in boxes:
        if widgets[b[0]].get():
            columns.append(b[0])
    print(columns)
    return columns

def toggle_compound_params(e=None):
    state = {'1':'normal', '0':'disabled'}[widgets['detector_compound'].get()]
    for k, d in compound_params.items():
        widgets[d['id']].config(state=state)

def log(msg, header=True):
    if header:
        log_display.log('@ {}: {}'.format('mini', msg), header)
    else:
        log_display.log("   {}".format(msg), header)