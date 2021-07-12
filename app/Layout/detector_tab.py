from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini
from DataVisualizer import data_display, trace_display
from Backend import interface, analyzer
changed = True
changes = {}
parameters = {}

def find_all():
    interface.find_mini_in_range(trace_display.default_xlim, trace_display.default_ylim)

def find_in_window():
    interface.find_mini_in_range(trace_display.ax.get_xlim(), trace_display.ax.get_ylim())
def load(parent):
    ##################################################
    #                    Methods                     #
    ##################################################
    def _show_all():
        for key in optionframe.get_keys(filter='data_display_'):
            optionframe.widgets[key].set(1)
        data_display.show_columns()

    def _hide_all():
        for key in optionframe.get_keys(filter='data_display_'):
            optionframe.widgets[key].set('')
        data_display.show_columns()
    def apply_parameters(e=None):
        global changed
        for i in parameters:
            if parameters[i] != pymini.widgets[i].get():
                changes[i] = pymini.widgets[i].get()
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

    pymini.widgets['detector_direction'] = optionframe.insert_label_optionmenu(
        name='detector_direction',
        label='Direction',
        options=['positive', 'negative']
    )
    entries = [
        ('detector_search_radius', 'Search radius in % of visible x-axis (Manual)', 'float'),
        ('detector_auto_radius', 'Search radius in number of points (Auto)', 'int'),
        ('detector_min_amp', 'Minimum amplitude (absolute value) (y-axis unit):', 'float'),# (config param name, Label text, validation type)
        ('detector_min_decay', 'Minimum decay constant (tau) (ms)', 'float'),
        ('detector_max_decay','Maximum decay constant (tau) (ms)', 'float/None'),
        # ('detector_min_auc', 'Minimum area under the curve', 'float'),
        ('detector_min_hw', 'Minimum halfwidth (ms)', 'float'),
        ('detector_max_hw', 'Maximum halfwidth (ms)', 'float/None'),
        ('detector_min_rise', 'Minimum rise constant (ms)', 'float'),
        ('detector_max_rise', 'Maximum rise constant (ms)', 'float/None'),
        ('detector_points_baseline', 'Number of data points averaged to find the start of an event:', 'int'),
        # ('detector_max_points_baseline', 'Maximum data points to consider before peak to find the baseline', 'int'),
        ('detector_max_points_decay', 'Maximum data points after peak to consider for decay', 'int'),
        # ('detector_decay_fit_ftol', 'Tolerance for termination by the change of the cost function in Scipy Curvefit', 'float')
    ]
    for i in entries:
        pymini.widgets[i[0]] = optionframe.insert_label_entry(
            name=i[0],
            label=i[1],
            validate_type=i[2]
        )
        pymini.widgets[i[0]].bind('<Return>', apply_parameters, add='+')
        pymini.widgets[i[0]].bind('<FocusOut>', apply_parameters, add='+')
        parameters[i[0]] = pymini.widgets[i[0]].get()
        changes[i[0]] = pymini.widgets[i[0]].get()

    # panel = frame.make_panel()
    # Tk.Label(panel, text='Fit decay functions using:').grid(column=0, row=0, sticky='news')
    # pymini.widgets['detector_decay_func_type'] = widget.VarWidget(name='detector_decay_func_type')
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
    #     ttk.Radiobutton(op_frame, text=b[0], variable=pymini.widgets['detector_decay_func_type'].var,
    #                    value=b[1], command=apply_parameters).grid(column=i, row=0, sticky='news')
    #
    # pymini.widgets['detector_decay_func_constant'] = frame.insert_label_checkbox(name='detector_decay_func_constant',
    #                                                                              label='Add a constant',
    #                                                                              onvalue='1',
    #                                                                              offvalue="",
    #                                                                              command=apply_parameters)
    pymini.widgets['detector_update_events'] = optionframe.insert_label_checkbox(
        name='detector_update_events',
        label='Update graph after each event detection during automated search (will slow down search)',
    )
    optionframe.insert_button(
        text='Apply',
        command=trace_display.canvas.get_tk_widget().focus_set
    )
    optionframe.insert_button(
        text='Default',
        command= lambda k='detector_':optionframe.default(filter=k)
    )
    optionframe.insert_button(
        text='Find all',
        command= find_all# link this later
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

    ##################################################
    #                  Data Export                   #
    ##################################################
    # frame.insert_title(
    #     name='data_export',
    #     text='Data Export'
    # )
    # pymini.widgets['data_export_all'] = frame.insert_label_checkbox(
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

    boxes = [
        ('data_display_time', 'Peak time'),
        ('data_display_amplitude', 'Amplitude'),
        ('data_display_decay', 'Decay constant'),
        ('data_display_decay_func', 'Decay function'),
        ('data_display_rise', 'Rise duration'),
        ('data_display_halfwidth', 'Halfwidth'),
        ('data_display_baseline', 'Baseline'),
        # ('data_display_start', 'Start time'),
        # ('data_display_end', 'End time'),
        ('data_display_channel', 'Channel'),
        ('data_display_direction', 'Direction'),
    ]
    for i in boxes:
        pymini.widgets[i[0]] = optionframe.insert_label_checkbox(
            name=i[0],
            label=i[1],
            command=data_display.show_columns,
            onvalue='1',
            offvalue=''
        )

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
        xs = interface.mini_df.index.where(interface.mini_df['channel'] == analyzer.trace_file.channel)
        xs = xs.dropna()
        data_display.set(interface.mini_df.loc[xs])
    except: # file not loaded yet
        pass