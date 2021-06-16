import tkinter as Tk
from tkinter import ttk
from utils import widget
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def load(parent):
    frame = Tk.Frame(parent, bg='green')
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_rowconfigure(1, weight=1)

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

    y_zoom_frame = Tk.Frame(frame, bg='')
    y_zoom_frame.grid(column=0, row=0, sticky='news')
    y_zoom_frame.grid_columnconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(1, weight=1)
    ttk.Button(y_zoom_frame, text='+').grid(column=0, row=0, sticky='news')
    ttk.Button(y_zoom_frame, text='-').grid(column=0, row=1, sticky='news')

    top_frame = Tk.Frame(frame, bg='')
    top_frame.grid(column=1, row=0, sticky='news')
    top_frame.grid_columnconfigure(0, weight=1)
    top_frame.grid_rowconfigure(0, weight=1)

    channel_option = widget.LabeledOptionMenu(top_frame,
                                              label='channel',
                                              value='0',
                                              default='0',
                                              options=[0])
    channel_option.frame.grid(column=1, row=0, sticky='news')

    yscrollbar_frame = Tk.Frame(frame, bg='lime')
    yscrollbar_frame.grid(column=0, row=1, sticky='news')
    yscrollbar_frame.grid_columnconfigure(1, weight=1)
    y_zoom_frame.grid_rowconfigure(1, weight=1)

    graph_frame = Tk.Frame(frame, bg='pink')
    graph_frame.grid(column=1, row=1, sticky='news')
    graph_frame.grid_columnconfigure(1, weight=1)
    graph_frame.grid_rowconfigure(1, weight=1)

    fig = Figure()
    fig.set_tight_layout(True)

    ax = fig.add_subplot(111)
    fig.subplots_adjust(right=1, top=1)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    ax.plot()

    toolbar_frame = Tk.Frame(top_frame, bg='pink')
    toolbar_frame.grid(column=0, row=0, sticky='news')
    navigation_toolbar = widget.NavigationToolbar(canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')
    navigation_toolbar.update()

    x_zoom_frame = Tk.Frame(frame, bg='yellow')
    x_zoom_frame.grid(column=0, row=2, sticky='news')
    x_zoom_frame.grid_columnconfigure(1, weight=1)
    x_zoom_frame.grid_rowconfigure(1, weight=1)

    xscrollbar_frame = Tk.Frame(frame, bg='magenta')
    xscrollbar_frame.grid(column=1, row=2, sticky='news')
    xscrollbar_frame.grid_columnconfigure(1, weight=1)
    xscrollbar_frame.grid_rowconfigure(1, weight=1)

    return frame