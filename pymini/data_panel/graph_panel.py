import tkinter as Tk
from tkinter import ttk
from utils import widget
from utils.scrollable_option_frame import ScrollableOptionFrame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_panel.plot_area import InteractivePlot

def load(parent):
    frame = ScrollableOptionFrame(parent, False)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    """
    ___________________________
    |+/-  |toolbox   | channel|
    |_____|__________|________|
    |  ^  | graph             |
    |  |  |                   |
    |  v  |                   |
    |_____|___________________|
    |+/-  |< ---- >           |
    |_____|___________________|
    
    """
    ##################################################
    #                    Top Row                     #
    ##################################################

    big_frame = Tk.Frame(frame, bg='pink')
    big_frame.grid_columnconfigure(1, weight=1)
    big_frame.grid_rowconfigure(1, weight=1)
    big_frame.grid(column=0, row=0, sticky='news')

    y_zoom_frame = Tk.Frame(big_frame, bg='')
    y_zoom_frame.grid(column=0, row=0, sticky='news')
    y_zoom_frame.grid_columnconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(1, weight=1)
    ttk.Button(y_zoom_frame, text='+').grid(column=0, row=0, sticky='news')
    ttk.Button(y_zoom_frame, text='-').grid(column=0, row=1, sticky='news')

    yscrollbar_frame = Tk.Frame(big_frame, bg='lime')
    yscrollbar_frame.grid(column=0, row=1, sticky='news')
    yscrollbar_frame.grid_columnconfigure(0, weight=1)
    yscrollbar_frame.grid_rowconfigure(1, weight=1)


    ttk.Button(yscrollbar_frame, text='^').grid(column=0, row=0, sticky='news')
    ttk.Button(yscrollbar_frame, text='v').grid(column=0, row=2, sticky='news')

    frame.widgets['y_scrollbar'] = widget.LinkedScale(parent=yscrollbar_frame,
                                                name='y_scrollbar',
                                                from_=0,
                                                to=100,
                                                orient=Tk.VERTICAL,
                                                command=None)
    frame.widgets['y_scrollbar'].widget.grid(column=0, row=1, sticky='news')

    graph_frame = Tk.Frame(big_frame)
    graph_frame.grid(column=1, row=1, sticky='news')
    graph_frame.grid_columnconfigure(0, weight=1)
    graph_frame.grid_rowconfigure(0, weight=1)

    plot = InteractivePlot(graph_frame)
    plot.frame.grid(column=0, row=0, sticky='news')

    toolbar_frame = Tk.Frame(big_frame)
    toolbar_frame.grid_columnconfigure(0, weight=1)
    toolbar_frame.grid_rowconfigure(0, weight=1)
    toolbar_frame.grid(column=1, row=0, sticky='news')
    navigation_toolbar = widget.NavigationToolbar(plot.canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')
    navigation_toolbar.update()

    channel_option = widget.LabeledOptionMenu(toolbar_frame,
                                              label='channel',
                                              value='0',
                                              default='0',
                                              options=[0])
    channel_option.frame.grid(column=2, row=0, sticky='news')
    #
    x_zoom_frame = Tk.Frame(frame, bg='orange')
    x_zoom_frame.grid_rowconfigure(0, weight=1)
    x_zoom_frame.grid_columnconfigure(3, weight=1)
    x_zoom_frame.grid(column=0, row=2, sticky='news')
    #
    ttk.Button(x_zoom_frame, text='+').grid(column=0, row=0, sticky='news')
    ttk.Button(x_zoom_frame, text='-').grid(column=1, row=0, sticky='news')

    ttk.Button(x_zoom_frame, text='<').grid(column=2, row=0, sticky='news')
    ttk.Button(x_zoom_frame, text='>').grid(column=4, row=0, sticky='news')


    frame.widgets['x_scrollbar'] = widget.LinkedScale(parent=x_zoom_frame,
                                                name='y_scrollbar',
                                                from_=0,
                                                to=100,
                                                orient=Tk.HORIZONTAL,
                                                command=None)
    frame.widgets['x_scrollbar'].widget.grid(column=3, row=0, sticky='news')

    return frame