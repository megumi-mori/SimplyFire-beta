from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
from PyMini import app
from PyMini.DataVisualizer import trace_display
from PyMini.Backend import interface


def load(parent):
    global widgets
    widgets = {}
    ##################################################
    #                    Methods                     #
    ##################################################
    def apply_axes_limits():
        interface.focus()
        # trace_display.focus()
        trace_display.set_axis_limit(
            axis='x',
            lim=(
                app.widgets['min_x'].get(),
                app.widgets['max_x'].get()
            )
        )
        trace_display.set_axis_limit(
            axis='y',
            lim=(
                app.widgets['min_y'].get(),
                app.widgets['max_y'].get()
            )
        )
        trace_display.canvas.draw()
        pass

    def default_axis_parameters():
        interface.focus()
        app.widgets['min_x'].set('auto')
        app.widgets['max_x'].set('auto')
        app.widgets['min_y'].set('auto')
        app.widgets['max_y'].set('auto')
        pass

    def default_nav_parameters():
        interface.focus()
        optionframe.default(filter='navigation', widgets=widgets)


    def get_current_axes():
        interface.focus()
        xlim = trace_display.get_axis_limits('x')
        app.widgets['min_x'].set(xlim[0])
        app.widgets['max_x'].set(xlim[1])
        ylim = trace_display.get_axis_limits('y')
        app.widgets['min_y'].set(ylim[0])
        app.widgets['max_y'].set(ylim[1])
        pass

    def show_all(e=None):
        interface.focus()
        trace_display.show_all_plot()

    ##################################################
    #                    Populate                    #
    ##################################################

    frame = ScrollableOptionFrame(parent)
    optionframe = frame.frame

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
        widgets[e[0]] = optionframe.insert_label_entry(
            name=e[0],
            label=e[1],
            validate_type=e[2]
        )
        widgets[e[0]].bind('<Return>', lambda e:apply_axes_limits(), add='+')
        widgets[e[0]].bind('<Return>', lambda e: interface.focus(), add='+')


    widgets['force_axis_limit'] = optionframe.insert_label_checkbox(
        name='force_axis_limit',
        label="Force axes limits on a new trace (reverts to 'show all' if out of bounds)"
    )
    optionframe.insert_button(
        text='Apply',
        command=apply_axes_limits
    )
    optionframe.insert_button(
        text='Default',
        command=default_axis_parameters
    )
    optionframe.insert_button(
        text='Show all',
        command=show_all
    )
    optionframe.insert_button(
        text='Current values',
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
        widgets[e[0]] = optionframe.insert_label_entry(
            name=e[0],
            label=e[1],
            validate_type=e[2]
        )
        widgets[e[0]].bind('<Return>', lambda e: interface.focus(), add ='+')

    boxes = [
       ('navigation_mirror_y_scroll', 'Mirror y-axis scroll button directions'), #name, label
       ('navigation_mirror_x_scroll', 'Mirror x-axis scroll button directions')
    ]

    for b in boxes:
       widgets[b[0]] = optionframe.insert_label_checkbox(
           name=b[0],
           label=b[1],
           onvalue=-1,
           offvalue=1
       )
    optionframe.insert_button(
        text='Apply',
        # command=app.plot.focus
    )
    optionframe.insert_button(
        text='Default',
        command=default_nav_parameters
    )


    return frame

