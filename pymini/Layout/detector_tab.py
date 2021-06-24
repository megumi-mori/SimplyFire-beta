from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini
from DataVisualizer import data_display
from utils import widget


def load(parent):
    ##################################################
    #                    Methods                     #
    ##################################################
    def _show_all():
        for key in frame.get_keys(filter='data_display_'):
            frame.widgets[key].set(1)
        data_display.show_columns()

    def _hide_all():
        for key in frame.get_keys(filter='data_display_'):
            frame.widgets[key].set('')
        data_display.show_columns()

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

    ##################################################
    #              Detector parameters               #
    ##################################################
    frame.insert_title(
        name='detector',
        text='Detector Parameters'
    )

    pymini.widgets['detector_direction'] = frame.insert_label_optionmenu(
        name='detector_direction',
        label='Direction',
        options=['positive', 'negative']
    )
    entries = [
        ('detector_min_amp', 'Minimum amplitude (y-axis unit):', 'float'),# (config param name, Label text, validation type)
        ('detector_points_baseline', 'Number of data points averaged to find the start/end of an event:', 'int'),
        ('detector_points_search', 'Number of data points to search for a peak', 'int'),
        ('detector_min_decay', 'Minimum decay constant (tau) (ms)', 'float'),
        ('detector_min_auc', 'Minimum area under the curve', 'float'),
        ('detector_max_points_baseline', 'Maximum data points to consider before peak to find the baseline', 'int'),
        ('detector_max_points_decay', 'Maximum data points after peak to consider for decay', 'int'),
        ('detector_manual_pixel_offset', 'Pixel offset for manuall picking events', 'int')
    ]
    for i in entries:
        pymini.widgets[i[0]] = frame.insert_label_entry(
            name=i[0],
            label=i[1],
            validate_type=i[2]
        )

    pymini.widgets['detector_update_events'] = frame.insert_label_checkbox(
        name='detector_update_events',
        label='Update graph after each event detection (will slow down search)',
    )
    frame.insert_button(
        text='Apply',
        # command=pymini.plot.focus
    )
    frame.insert_button(
        text='Default paramters',
        command= lambda k='detector_':frame.default(filter=k)
    )
    frame.insert_button(
        text='Find all',
        command=None  # link this later
    )
    frame.insert_button(
        text='Delete all',
        command=None  # link this later
    )
    frame.insert_button(
        text='Find in window',
        command=None  # link this later
    )

    frame.insert_button(
        text='Delete in window',
        command=None  # link this later
    )

    ##################################################
    #                  Data Export                   #
    ##################################################
    frame.insert_title(
        name='data_export',
        text='Data Export'
    )
    pymini.widgets['data_export_all'] = frame.insert_label_checkbox(
        name='data_export_all',
        label='Export all visible and hidden data?',
        onvalue=1,
        offvalue=-1
        # command=None #Link this to exporting data sets
    )

    ##################################################
    #                  Data Display                  #
    ##################################################
    # all column display options for the data table must start with "data_display_"

    frame.insert_title(
        name='dataframe',
        text='Data Table Display'
    )

    boxes = [
        ('data_display_time', 'Peak time'),
        ('data_display_amplitude', 'Amplitude'),
        ('data_display_decay', 'Decay constant'),
        ('data_display_decay_time', 'Decay time point'),
        ('data_display_rise', 'Rise duration'),
        ('data_display_halfwidth', 'Halfwidth'),
        ('data_display_baseline', 'Baseline'),
        ('data_display_start', 'Start time'),
        ('data_display_end', 'End time'),
        ('data_display_channel', 'Channel')
    ]
    for i in boxes:
        pymini.widgets[i[0]] = frame.insert_label_checkbox(
            name=i[0],
            label=i[1],
            command=data_display.show_columns,
            onvalue='1',
            offvalue=''
        )

    frame.insert_button(
        text='Show All',
        command=_show_all
    )
    frame.insert_button(
        text='Hide All',
        command=_hide_all
    )
    frame.insert_button(
        text='Fit columns',
        command=data_display.table.fit_columns
    )

    return frame
