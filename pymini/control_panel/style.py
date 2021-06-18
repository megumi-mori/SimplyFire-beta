from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini


def load(parent):

    def apply_axes_limits():
        pymini.plot_area.set_axis_limits(
            {
                'x': (
                    optionframe.get_value('min_x'),
                    optionframe.get_value('max_x')
                ),
                'y': (
                    optionframe.get_value('min_y'),
                    optionframe.get_value('max_y')
                )
            }
        )

    def apply_axis_limit(type, idx, lim):

        pass
    def get_current_axes():
        xlim = pymini.plot_area.get_axis_limits('x')
        pymini.cp.style_tab.set_value('min_x', xlim[0])
        pymini.cp.style_tab.set_value('max_x', xlim[1])
        ylim = pymini.plot_area.get_axis_limits('y')
        pymini.cp.style_tab.set_value('min_y', ylim[0])
        pymini.cp.style_tab.set_value('max_y', ylim[1])

    optionframe = ScrollableOptionFrame(parent)
    ##################################################
    #           Populate style option tab            #
    ##################################################

    ##################################################
    #               Parameter options                #
    ##################################################

    optionframe.insert_label_entry(
        name='min_x',
        label='Min x-axis:',
        value=config.min_x,
        default=config.default_min_x,
        validate_type='auto/float'
    )
    optionframe.insert_label_entry(
        name='max_x',
        label='Max x-axis:',
        value=config.max_x,
        default=config.default_max_x,
        validate_type='auto/float'
    )
    optionframe.insert_label_entry(
        name='min_y',
        label='Min y-axis:',
        value=config.min_y,
        default=config.default_min_y,
        validate_type='auto/float'
    )
    optionframe.insert_label_entry(
        name='max_y',
        label='Max y-axis:',
        value=config.max_y,
        default=config.default_max_y,
        validate_type='auto/float'
    )
    optionframe.insert_checkbox(
        name='apply_axis_limit',
        label='Apply axis limits on a new trace',
        value=config.apply_axis_limit,
        default=config.default_apply_axis_limit
    )
    optionframe.insert_button(
        text='Apply axes limits',
        command=apply_axes_limits
    )
    optionframe.insert_button(
        text='Fetch current axes limits',
        command=get_current_axes
    )
    optionframe.insert_button(
        text='Show all trace',
        command=pymini.plot_area.show_all_plot
    )
    optionframe.insert_label_entry(
        name='line_width',
        label='Trace line width:',
        value=config.line_width,
        default=config.default_line_width,
        validate_type='color'
    )
    optionframe.insert_label_entry(
        name='line_color',
        label='Trace line color:',
        value=config.line_color,
        default=config.default_line_color,
        validate_type='color'
    )
    optionframe.insert_label_entry(
        name='event_color',
        label='Event peak color:',
        value=config.event_color,
        default=config.default_event_color,
        validate_type='color'
    )
    optionframe.insert_label_entry(
        name='baseline_color',
        label='Event baseline color:',
        value=config.baseline_color,
        default=config.default_baseline_color,
        validate_type='color'
    )
    optionframe.insert_label_entry(
        name='decay_color',
        label='Event decay (tau) color:',
        value=config.decay_color,
        default=config.default_decay_color,
        validate_type='color'
    )
    optionframe.insert_label_entry(
        name='highlight_color',
        label='Event highlight color:',
        value=config.highlight_color,
        default=config.default_highlight_color,
        validate_type='color'
    )

    return optionframe