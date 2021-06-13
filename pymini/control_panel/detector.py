from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame

def load(parent):
    frame = ScrollableOptionFrame(parent)

    ##################################################
    #          Populate detector option tab          #
    ##################################################

    ##################################################
    #               Parameter options                #
    ##################################################

    frame.insert_optionmenu(
        name='direction',
        label='Direction',
        value=config.direction,
        default=config.default_direction,
        options=['positive', 'negative']
    )
    frame.insert_entry(
        name='min_amp',
        label='Minimum amplitude (nA):',
        value=config.min_amp,
        default=config.default_min_amp,
        validate_type='float'
    )
    frame.insert_entry(
        name='points_baseline',
        label='Number of data points to average for baseline:',
        value=config.points_baseline,
        default=config.default_points_baseline,
        validate_type='int'
    )
    frame.insert_entry(
        name='points_search',
        label='Number of data points to search for a peak',
        value=config.points_search,
        default=config.default_points_search,
        validate_type='int'
    )
    frame.insert_entry(
        name='min_decay',
        label='Minimum decay constant (tau) (ms)',
        value=config.min_decay,
        default=config.default_min_decay,
        validate_type='float'
    )
    frame.insert_entry(
        name='max_points_baseline',
        label='Maximum data points to consider before peak to find the baseline',
        value=config.max_points_baseline,
        default=config.default_max_points_baseline,
        validate_type='int'
    )
    frame.insert_entry(
        name='max_points_decay',
        label='Maximum data points after peak to consider for decay',
        value=config.max_points_decay,
        default=config.default_max_points_decay,
        validate_type='int'
    )
    frame.insert_entry(
        name='manual_pixel_offset',
        label='Pixel offset for manually picking events',
        value=config.manual_pixel_offset,
        default=config.default_manual_pixel_offset,
        validate_type='int'
    )
    frame.insert_checkbox(
        name='update_events',
        label='Update graph after each event detection (will slow down search)',
        value=config.update_events,
        default=config.default_update_events,
    )
    frame.insert_checkbox(
        name='save_detector_preferencs',
        label='Save preferences',
        value=config.update_events,
        default=config.default_update_events
    )
    frame.insert_button(
        text='Default Paramters',
        command=frame.default
    )

    ##################################################
    #                    Buttons                     #
    ##################################################

    frame.insert_button(text='hello, world!')
    frame.insert_button(text='hello, world!')
    frame.isolate_button()
    frame.insert_button(text='hello, world!')

    return frame

class Detector(ScrollableOptionFrame):
    def __init__(self, parent):
        self.param={}

        super().__init__(parent)

        self.load_parameters()

    def load_parameters(self):

        self.param['direction'] = self.insert_optionmenu(
            name='direction',
            label='Direction',
            value=config.direction,
            default=config.default_direction,
            options=['positive', 'negative']
        )
        self.param['min_amp'] = self.insert_entry(
            name='min_amp',
            label='Minimum amplitude (nA):',
            value=config.min_amp,
            default=config.default_min_amp,
            validate_type='float'
        )
        self.param['points_baseline'] = self.insert_entry(
            name='points_baseline',
            label='Number of data points to average for baseline:',
            value=config.points_baseline,
            default=config.default_points_baseline,
            validate_type='int'
        )
        self.param['points_search'] = self.insert_entry(
            name='points_search',
            label='Number of data points to search for a peak',
            value=config.points_search,
            default=config.default_points_search,
            validate_type='int'
        )
        self.param['min_decay'] = self.insert_entry(
            name='min_decay',
            label='Minimum decay constant (tau) (ms)',
            value=config.min_decay,
            default=config.default_min_decay,
            validate_type='float'
        )
        self.param['max_points_baseline'] = self.insert_entry(
            name='max_points_baseline',
            label='Maximum data points to consider before peak to find the baseline',
            value=config.max_points_baseline,
            default=config.default_max_points_baseline,
            validate_type='int'
        )
        self.param['max_points_decay'] = self.insert_entry(
            name='max_points_decay',
            label='Maximum data points after peak to consider for decay',
            value=config.max_points_decay,
            default=config.default_max_points_decay,
            validate_type='int'
        )
        self.param['manual_pixel_offset'] = self.insert_entry(
            name='manual_pixel_offset',
            label='Pixel offset for manually picking events',
            value=config.manual_pixel_offset,
            default=config.default_manual_pixel_offset,
            validate_type='int'
        )
        self.param['update_events'] = self.insert_checkbox(
            name='update_events',
            label='Update graph after each event detection (will slow down search)',
            value=config.update_events,
            default=config.default_update_events,
        )
        self.param['save_detector_preferencs'] = self.insert_checkbox(
            name='save_detector_preferencs',
            label='Save preferences',
            value=config.update_events,
            default=config.default_update_events
        )
        self.insert_button(
            text='Default Paramters',
            command=self.default
        )

        self.insert_button(text='hello, world!')
        self.insert_button(text='hello, world!')
        self.isolate_button()
        self.insert_button(text='hello, world!')





