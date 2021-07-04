from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini
from Backend import interface
from DataVisualizer import trace_display

def load(parent):

    frame = ScrollableOptionFrame(parent)
    optionframe = frame.frame
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
        ('style_trace_highlight_color', 'Trace selection highlight color:', 'color'),
        ('style_event_pick_offset', 'Pixel offset for selecting event markers', 'int'),
    ]
    for i in entries:
        pymini.widgets[i[0]] = optionframe.insert_label_entry(
            name=i[0],
            label=i[1],
            validate_type=i[2]
        )
        pymini.widgets[i[0]].bind(
            '<Return>',
            lambda e, k=[i[0]]: trace_display.apply_styles(k),
            add='+'
        )
        pymini.widgets[i[0]].bind('<Return>', lambda e: trace_display.canvas.get_tk_widget().focus_set(), add='+')

    optionframe.insert_button(
        text='Apply',
        command= lambda e=[i[0] for i in entries]: trace_display.apply_styles(e)
    )
    optionframe.insert_button(
        text='Default',
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
        ('show_decay', 'Decay constant'),
        ('show_start', 'Event start'),
        # ('show_end', 'Event end')
    ]
    for i in boxes:
        pymini.widgets[i[0]] = optionframe.insert_label_checkbox(
            name = i[0],
            label=i[1],
            onvalue='1',
            offvalue='',
            command=lambda e=i[0]:interface.toggle_marker_display(e) #need to link this
        )
    def show_all(e=None):
        optionframe.set_all('1', filter='show_')
        for i in boxes:
            interface.toggle_marker_display(i[0])
    def hide_all(e=None):
        optionframe.set_all('', filter='show_')
        for i in boxes:
            interface.toggle_marker_display(i[0])
    b = optionframe.insert_button(
        text='Show all',
        command= show_all
    )
    b.bind('<ButtonPress-1>', show_all, add="+")
    b = optionframe.insert_button(
        text='Hide all',
        command=hide_all
    )

    return frame