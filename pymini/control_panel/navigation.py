from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini


def load(parent):
    def apply_axes_limits():
        pymini.plot_area.focus()
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

    def default_nav_parameters():
        optionframe.default([
            'nav_fps',
            'scroll_percent',
            'zoom_percent',
            'mirror_y_scroll',
            'mirror_x_scroll'
        ])

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

    optionframe = ScrollableOptionFrame(parent)

    ##################################################
    #                      Axes                      #
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
        lambda e, n='min_x', a='x', i=0: apply_axis_limit(n, a, i),
        add="+"
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
        lambda e, n='max_x', a='x', i=1: apply_axis_limit(n, a, i),
        add="+"
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
        lambda e, n='min_y', a='y', i=0: apply_axis_limit(n, a, i),
        add="+"
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
        lambda e, n='max_y', a='y', i=1: apply_axis_limit(n, a, i),
        add="+"
    )
    optionframe.insert_label_checkbox(
        name='apply_axis_limit',
        label='Force axes limits on a new trace',
        value=config.apply_axis_limit,
        default=config.default_apply_axis_limit
    )
    optionframe.insert_button(
        text='Show all trace',
        command=pymini.plot_area.show_all_plot
    )
    optionframe.insert_button(
        text='Apply axes limits',
        command=apply_axes_limits
    )
    optionframe.insert_button(
        text='Get default parameters',
        command=default_axis_parameters
    )
    optionframe.insert_button(
        text='Get current axes limits',
        command=get_current_axes
    )

    ##################################################
    #                  Scroll/Zoom                   #
    ##################################################

    optionframe.insert_title(
        name='scroll_zoom',
        text='Scroll/Zoom'
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
    optionframe.insert_label_checkbox(
        name='mirror_y_scroll',
        label='Mirror y-axis scroll button directions',
        value=config.mirror_y_scroll,
        default=config.default_mirror_y_scroll
    )
    optionframe.widgets['mirror_y_scroll'].config(onvalue=-1, offvalue=1)
    optionframe.insert_label_checkbox(
        name='mirror_x_scroll',
        label='Mirror x-axis scroll button directions',
        value=config.mirror_x_scroll,
        default=config.default_mirror_x_scroll
    )
    optionframe.widgets['mirror_x_scroll'].config(onvalue=-1, offvalue=1)
    optionframe.insert_button(
        text='Apply',
        command=pymini.plot_area.focus
    )
    optionframe.insert_button(
        text='Default parameters',
        command=default_nav_parameters
    )


    return optionframe

