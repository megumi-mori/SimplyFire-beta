import tkinter as Tk
from tkinter import ttk

from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
from PyMini.utils.widget import VarEntry
# import PyMini.app as app
from PyMini import app
from PyMini.Backend import interface
from PyMini.DataVisualizer import trace_display
from PyMini.Layout.base_module import BaseModule

global widgets
widgets = {}


class StyleTab(BaseModule):
    def __init__(self, parent, app, interface):
        super().__init__(parent, app, interface)


        # self.frame.insert_title(text='Main plot style')
        ttk.Label(self.frame, text='Main plot style', anchor=Tk.CENTER).grid(column=0, row=0, sticky='news')

def load(parent):
    global optionframe
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
        text='Main plot style'
    )

    global widgets
    main_style_panel = optionframe.make_panel(separator=False)
    main_style_panel.grid_columnconfigure(0, weight=1)
    main_style_panel.grid_columnconfigure(1, weight=1)
    main_style_panel.grid_columnconfigure(2, weight=1)

    color_width = 10
    size_width = 3

    label_column=1
    size_column=2
    color_column=3

    row = 0
    ttk.Label(main_style_panel, text='size', justify=Tk.CENTER).grid(column=size_column, row=row, sticky='news')
    ttk.Label(main_style_panel, text='color', justify=Tk.CENTER).grid(column=color_column, row=row, sticky='news')

    row+= 1
    ttk.Label(main_style_panel, text='Trace plot').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_trace_line_width', column=size_column, row=row, frame=main_style_panel, width=size_width)
    place_VarEntry(name='style_trace_line_color', column=color_column, row=row, frame=main_style_panel, width=color_width, validate_type='color')

    row+= 1
    ttk.Label(main_style_panel, text='Peak marker').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_event_peak_size', column=size_column, row=row, frame=main_style_panel, width=size_width)
    place_VarEntry(frame=main_style_panel, name='style_event_peak_color', width=color_width, column=color_column, row=row, validate_type='color')

    row+= 1
    ttk.Label(main_style_panel, text='Start marker').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_event_start_size', column=size_column, row=row, frame=main_style_panel, width=size_width)
    place_VarEntry(frame=main_style_panel, name='style_event_start_color', width=color_width, column=color_column,
                   row=row, validate_type='color')

    row+= 1
    ttk.Label(main_style_panel, text='Decay marker').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_event_decay_size', column=size_column, row=row, frame=main_style_panel,
                   width=size_width)
    place_VarEntry(frame=main_style_panel, name='style_event_decay_color', width=color_width, column=color_column,
                   row=row, validate_type='color')

    row += 1
    ttk.Label(main_style_panel, text='Event highlight marker').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_event_highlight_size', column=size_column, row=row, frame=main_style_panel,
                   width=size_width)
    place_VarEntry(frame=main_style_panel, name='style_event_highlight_color', width=color_width, column=color_column,
                   row=row, validate_type='color')

    row += 1
    ttk.Label(main_style_panel, text='Trace highlight').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_trace_highlight_width', column=size_column, row=row, frame=main_style_panel,
                   width=size_width)
    place_VarEntry(frame=main_style_panel, name='style_trace_highlight_color', width=color_width, column=color_column,
                   row=row, validate_type='color')

    row +=1
    ttk.Label(main_style_panel, text='Event pick offset').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_event_pick_offset', column=size_column, row=row, frame=main_style_panel, width=size_width)

    row += 1
    ttk.Label(main_style_panel, text='Sweep pick offset (% axis)').grid(column=label_column, row=row, sticky='news')
    place_VarEntry(name='style_trace_pick_offset_percent', column=size_column, row=row, frame=main_style_panel,
                   width=size_width)

    global entries
    entries = ['style_trace_line_width', 'style_trace_line_color',
                                'style_event_peak_size', 'style_event_peak_color',
                                'style_event_start_size', 'style_event_start_color',
                                'style_event_decay_size', 'style_event_decay_color',
                                'style_event_highlight_size', 'style_event_highlight_color',
                                'style_trace_highlight_width', 'style_trace_highlight_color',
               'style_event_pick_offset', 'style_trace_pick_offset_percent'
               ]

    for i in entries:
        widgets[i].bind(
            '<Return>',
            apply_styles,
            add='+'
        )
    #     app.widgets[i[0]].bind(
    #         '<Return>',
    #         lambda e, k=[i[0]]: trace_display.apply_styles(k),
    #         add='+'
    #     )
    #     app.widgets[i[0]].bind('<Return>', lambda e: trace_display.canvas.get_tk_widget().focus_set(), add='+')

    optionframe.insert_button(
        text='Apply',
        command= apply_styles
    )
    optionframe.insert_button(
        text='Default',
        command= default
    )
    ##################################################
    #                 Marker display                 #
    ##################################################

    optionframe.insert_title(
        name='event_markers',
        text='Event Markers'
    )
    global boxes
    boxes = [
        ('show_peak', 'Peak'),
        ('show_decay', 'Decay constant'),
        ('show_start', 'Event start'),
        # ('show_end', 'Event end')
    ]
    for i in boxes:
        widgets[i[0]] = optionframe.insert_label_checkbox(
            name = i[0],
            label=i[1],
            onvalue='1',
            offvalue='',
            command=lambda e=i[0]:interface.toggle_marker_display(e) #need to link this
        )
    b = optionframe.insert_button(
        text='Show all',
        command= show_all
    )
    b.bind('<ButtonPress-1>', show_all, add="+")
    b = optionframe.insert_button(
        text='Hide all',
        command=hide_all
    )
    b.bind('<ButtonPress-1>', hide_all, add='+')
    ####################################
    # Export options
    ####################################
    widgets['style_export_transparency'] = optionframe.insert_label_checkbox(
        name='style_export_transparency',
        label='Export with transparent background',
        onvalue='1',
        offvalue='',
    )
    return frame
def apply_styles(e=None):
    global entries
    interface.focus()
    trace_display.apply_styles(entries)

def default(e=None):
    global optionframe
    optionframe.default(filter='style', widgets=widgets)
    interface.focus()

def place_VarEntry(name, column, row, frame, width=None, validate_type=""):
    global widgets
    widgets[name] = VarEntry(frame, name=name, width=width,validate_type=validate_type)
    widgets[name].grid(column=column, row=row, sticky='news')
    return widgets[name]

def show_all(e=None):
    interface.focus()
    for i in boxes:
        widgets[i[0]].var.set('1')
        interface.toggle_marker_display(i[0])
def hide_all(e=None):
    interface.focus()
    for i in boxes:
        widgets[i[0]].var.set("")
        interface.toggle_marker_display(i[0])