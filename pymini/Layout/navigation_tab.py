from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini
from DataVisualizer import trace_display


def load(parent, root):
    ##################################################
    #                    Methods                     #
    ##################################################
    def apply_axes_limits():
        # trace_display.focus()
        trace_display.set_axis_limit(
            axis='x',
            lim=(
                optionframe.get_value('min_x'),
                optionframe.get_value('max_x')
            )
        )
        trace_display.set_axis_limit(
            axis='y',
            lim=(
                optionframe.get_value('min_y'),
                optionframe.get_value('max_y')
            )
        )
        trace_display.canvas.draw()
        pass

    def default_axis_parameters():
        optionframe.set_value('min_x', 'auto')
        optionframe.set_value('max_x', 'auto')
        optionframe.set_value('min_y', 'auto')
        optionframe.set_value('max_y', 'auto')
        pass

    def default_nav_parameters():
        optionframe.default(filter='navigation')


    def get_current_axes():
        xlim = trace_display.get_axis_limits('x')
        optionframe.set_value('min_x', xlim[0])
        optionframe.set_value('max_x', xlim[1])
        ylim = trace_display.get_axis_limits('y')
        optionframe.set_value('min_y', ylim[0])
        optionframe.set_value('max_y', ylim[1])
        pass

    ##################################################
    #                    Populate                    #
    ##################################################

    optionframe = ScrollableOptionFrame(parent)

    ##################################################
    #                      Axes                      #
    ##################################################
    optionframe.insert_title(
        name='axis',
        text='Axes'
    )
    entries = [
        ('min_x', 'Left x-axis', '[auto]/float'),  # config name, label text, validate_type
        ('max_x', 'Right x-axis', '[auto]/float'),
        ('max_y', 'Top y-axis', '[auto]/float'),
        ('min_y', 'Bottom y-axis', '[auto]/float')
    ]
    for e in entries:
        pymini.widgets[e[0]] = optionframe.insert_label_entry(
            name=e[0],
            label=e[1],
            validate_type=e[2]
        )
        pymini.widgets[e[0]].bind('<Return>', lambda e:apply_axes_limits())
    # pymini.widgets['min_x'] = optionframe.insert_label_entry(
    #     name='min_x',
    #     label='Min x-axis:',
    #     validate_type='auto/float'
    # )
    # pymini.widgets['min_x'].bind(
    #     '<Return>',
    #     lambda e, n='min_x', a='x', i=0: apply_axis_limit(n, a, i),
    #     add="+"
    # )
    # pymini.widgets['max_x'] = optionframe.insert_label_entry(
    #     name='max_x',
    #     label='Max x-axis:',
    #     validate_type='auto/float'
    # )
    # pymini.widgets['max_x'].bind(
    #     '<Return>',
    #     lambda e, n='max_x', a='x', i=1: apply_axis_limit(n, a, i),
    #     add="+"
    # )
    # pymini.widgets['min_y'] = optionframe.insert_label_entry(
    #     name='min_y',
    #     label='Min y-axis:',
    #     validate_type='auto/float'
    # )
    # pymini.widgets['min_y'].bind(
    #     '<Return>',
    #     lambda e, n='min_y', a='y', i=0: apply_axis_limit(n, a, i),
    #     add="+"
    # )
    # pymini.widgets['max_y'] = optionframe.insert_label_entry(
    #     name='max_y',
    #     label='Max y-axis:',
    #     validate_type='auto/float'
    # )
    # optionframe.get_widget('max_y').bind(
    #     '<Return>',
    #     lambda e, n='max_y', a='y', i=1: apply_axis_limit(n, a, i),
    #     add="+"
    # )

    pymini.widgets['force_axis_limit'] = optionframe.insert_label_checkbox(
        name='force_axis_limit',
        label='Force axes limits on a new trace'
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
        text='Show all trace',
        command=trace_display.show_all_plot
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
    entries = [
        ('navigation_fps', 'Smooth navigation speed (fps):', 'int'), #name, label, validatetype
        ('navigation_scroll_percent','Scroll speed (percent axis):', 'float'),
        ('navigation_zoom_percent', 'Zoom speed (percent axis):', 'float')
    ]
    for e in entries:
        pymini.widgets[e[0]] = optionframe.insert_label_entry(
            name=e[0],
            label=e[1],
            validate_type=e[2]
        )

    boxes = [
       ('navigation_mirror_y_scroll', 'Mirror y-axis scroll button directions'), #name, label
       ('navigation_mirror_x_scroll', 'Mirror x-axis scroll button directions')
    ]

    for b in boxes:
       pymini.widgets[b[0]] = optionframe.insert_label_checkbox(
           name=b[0],
           label=b[1],
           onvalue=-1,
           offvalue=1
       )
    optionframe.insert_button(
        text='Apply',
        # command=pymini.plot.focus
    )
    optionframe.insert_button(
        text='Default parameters',
        command=default_nav_parameters
    )


    return optionframe

