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

    def default_axis_parameters():
        optionframe.set_value('min_x', 'auto')
        optionframe.set_value('max_x', 'auto')
        optionframe.set_value('min_y', 'auto')
        optionframe.set_value('max_y', 'auto')
        pass

    def apply_axis_limit(name, axis, idx):
        print((name, axis, idx))
        pymini.plot_area.set_single_axis_limit(axis, idx, optionframe.get_value(name))


    def get_current_axes():
        xlim = pymini.plot_area.get_axis_limits('x')
        optionframe.set_value('min_x', xlim[0])
        optionframe.set_value('max_x', xlim[1])
        ylim = pymini.plot_area.get_axis_limits('y')
        optionframe.set_value('min_y', ylim[0])
        optionframe.set_value('max_y', ylim[1])

    def apply_all_style():
        pymini.plot_area.apply_all_style()
        pass

    def apply_style(style):
        pymini.plot_area.apply_style(style)
        pass

    def default_style_parameters():
        optionframe.default([
            'line_color',
            'line_width',
            'event_color',
            'highlight_color',
            'baseline_color',
            'decay_color'
        ])

    optionframe = ScrollableOptionFrame(parent)
    ##################################################
    #           Populate style option tab            #
    ##################################################

    ##################################################
    #               Parameter options                #
    ##################################################
    optionframe.insert_title(
        name='axis',
        text='Axes'
    )
    optionframe.insert_label_entry(
        name='min_x',
        label='Min x-axis:',
        value=config.min_x,
        default=config.default_min_x,
        validate_type='auto/float'
    )
    optionframe.get_widget('min_x').bind(
        '<Return>',
        lambda e, n='min_x', a='x', i=0: apply_axis_limit(n,a,i)
    )
    optionframe.insert_label_entry(
        name='max_x',
        label='Max x-axis:',
        value=config.max_x,
        default=config.default_max_x,
        validate_type='auto/float'
    )
    optionframe.get_widget('max_x').bind(
        '<Return>',
        lambda e, n='max_x', a='x', i=1: apply_axis_limit(n, a, i)
    )
    optionframe.insert_label_entry(
        name='min_y',
        label='Min y-axis:',
        value=config.min_y,
        default=config.default_min_y,
        validate_type='auto/float'
    )
    optionframe.get_widget('min_y').bind(
        '<Return>',
        lambda e, n='min_y', a='y', i=0: apply_axis_limit(n, a, i)
    )
    optionframe.insert_label_entry(
        name='max_y',
        label='Max y-axis:',
        value=config.max_y,
        default=config.default_max_y,
        validate_type='auto/float'
    )
    optionframe.get_widget('max_y').bind(
        '<Return>',
        lambda e, n='max_y', a='y', i=1: apply_axis_limit(n, a, i)
    )
    optionframe.insert_checkbox(
        name='apply_axis_limit',
        label='Apply axis limits on a new trace',
        value=config.apply_axis_limit,
        default=config.default_apply_axis_limit
    )

    optionframe.insert_button(
        text='Default axis limits',
        command=default_axis_parameters
    )
    optionframe.insert_button(
        text='Get current axes limits',
        command=get_current_axes
    )
    optionframe.insert_button(
        text='Show all trace',
        command=pymini.plot_area.show_all_plot
    )
    optionframe.insert_button(
        text='Apply axes limits',
        command=apply_axes_limits
    )

    optionframe.insert_label_entry(
        name='line_width',
        label='Trace line width:',
        value=config.line_width,
        default=config.default_line_width,
        validate_type='color'
    )
    optionframe.get_widget('line_width').bind(
        '<Return>',
        lambda e, k='line_width': apply_style(k)
    )
    optionframe.insert_label_entry(
        name='line_color',
        label='Trace line color:',
        value=config.line_color,
        default=config.default_line_color,
        validate_type='color'
    )
    optionframe.get_widget('line_color').bind(
        '<Return>',
        lambda e, k='line_color': apply_style(k)
    )
    optionframe.insert_label_entry(
        name='event_color',
        label='Event peak color:',
        value=config.event_color,
        default=config.default_event_color,
        validate_type='color'
    )
    optionframe.get_widget('event_color').bind(
        '<Return>',
        lambda e, k='event_color': apply_style
    )
    optionframe.insert_label_entry(
        name='baseline_color',
        label='Event baseline color:',
        value=config.baseline_color,
        default=config.default_baseline_color,
        validate_type='color'
    )
    optionframe.get_widget('baseline_color').bind(
        '<Return>',
        lambda e, k='baseline_color': apply_style
    )
    optionframe.insert_label_entry(
        name='decay_color',
        label='Event decay (tau) color:',
        value=config.decay_color,
        default=config.default_decay_color,
        validate_type='color'
    )
    optionframe.get_widget('decay_color').bind(
        '<Return>',
        lambda e, k='decay_color': apply_style
    )
    optionframe.insert_label_entry(
        name='highlight_color',
        label='Event highlight color:',
        value=config.highlight_color,
        default=config.default_highlight_color,
        validate_type='color'
    )
    optionframe.get_widget('highlight_color').bind(
        '<Return>',
        lambda e, k='highlight_color': apply_style
    )
    optionframe.insert_button(
        text='Apply',
        command=apply_all_style
    )
    optionframe.insert_button(
        text='Default parameters',
        command=default_style_parameters
    )
    optionframe.insert_label_entry(
        name='nav_fps',
        label='Smooth navigation speed (fps):',
        value=config.nav_fps,
        default=config.default_nav_fps,
        validate_type='int'
    )
    optionframe.insert_label_entry(
        name='scroll_percent',
        label='Scroll speed (percent axis):',
        value=config.scroll_percent,
        default=config.default_scroll_percent,
        validate_type='float'
    )
    optionframe.insert_label_entry(
        name='zoom_percent',
        label='Zoom speed (percent axis):',
        value=config.zoom_percent,
        default=config.default_zoom_percent,
        validate_type='float'
    )
    optionframe.insert_button(
        text='Apply',
        # command=apply_all_style
    )
    optionframe.insert_button(
        text='Default parameters',
        # command=default_style_parameters
    )

    return optionframe