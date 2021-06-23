from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini


def load(parent):
    def _change_display_mode(e):
        print(e)
    optionframe = ScrollableOptionFrame(parent)
    ##################################################
    #           Populate style option tab            #
    ##################################################

    ##################################################
    #               Parameter options                #
    ##################################################

    optionframe.insert_title(
        name='plot_style',
        text='Graph Style'
    )
    entries = [
        ('style_trace_line_width', 'Trace line width:','float'), # (config param name, Label text, validation type)
        ('style_trace_line_color', 'Trace line color:', 'color'),
        ('style_event_color_peak', 'Event peak marker color:', 'color'),
        ('style_event_color_start', 'Event start marker color:', 'color'),
        ('style_event_color_end', 'Event end marker color:', 'color'),
        ('style_event_color_decay', 'Event decay constant marker color:', 'color'),
        ('style_event_color_highlight', 'Event selection highlight color', 'color'),
        ('style_trace_highlight_color', 'Trace selection highlight color:', 'color')
    ]
    for i in entries:
        pymini.widgets[i[0]] = optionframe.insert_label_entry(
            name=i[0],
            label=i[1],
            validate_type=i[2]
        )
        pymini.widgets[i[0]].bind(
            '<Return>',
            lambda e, k=i[0]: pymini.plot_area.apply_style(k)
        )

    optionframe.insert_button(
        text='Apply',
        command=pymini.plot_area.apply_all_style
    )
    optionframe.insert_button(
        text='Default parameters',
        command=lambda k='style': optionframe.default(filter=k)
    )
    ##################################################
    #                 Marker display                 #
    ##################################################

    optionframe.insert_title(
        name='event_markers',
        text='Event Markers'
    )
    boxes = [
        ('show_peak', 'Peak'),
        ('show_decay_constant', 'Decay constant'),
        ('show_start', 'Event start'),
        ('show_end', 'Event end')
    ]
    for i in boxes:
        pymini.widgets[i[0]] = optionframe.insert_label_checkbox(
            name = i[0],
            label=i[1],
            onvalue='1',
            offvalue='',
            command=None #need to link this
        )
    b = optionframe.insert_button(
        text='Show all',
        command=lambda v='1', f='show_':optionframe.set_all(v, filter=f)
    )
    # b.bind(<Button>, ) need one more to link
    b = optionframe.insert_button(
        text='Hide all',
        command=lambda v='', f='show_':optionframe.set_all(v, filter=f)
    )

    return optionframe