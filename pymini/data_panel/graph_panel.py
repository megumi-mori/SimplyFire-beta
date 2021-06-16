import tkinter as Tk
from tkinter import ttk
from utils import widget
from utils.scrollable_option_frame import ScrollableOptionFrame
from config import config


from data_panel.plot_area import InteractivePlot
import pymini

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


    pan_up = ttk.Button(yscrollbar_frame, text='^')
    pan_up.grid(column=0, row=0, sticky='news')
    pan_up.bind('<ButtonPress-1>', lambda e, c='y', d=1: scroll_plot(c, d))
    pan_up.bind('<ButtonRelease-1>', stop)
    pan_down = ttk.Button(yscrollbar_frame, text='v')
    pan_down.grid(column=0, row=2, sticky='news')
    pan_down.bind('<ButtonPress-1>', lambda e, c='y', d=-1: scroll_plot(c, d))
    pan_down.bind('<ButtonRelease-1>', stop)


    frame.widgets['y_scrollbar'] = widget.LinkedScale(parent=yscrollbar_frame,
                                                name='y_scrollbar',
                                                from_=0,
                                                to=100,
                                                orient=Tk.VERTICAL,
                                                command=None)
    frame.widgets['y_scrollbar'].widget.grid(column=0, row=1, sticky='news')
    frame.widgets['y_scrollbar'].widget.config(state='disabled')
    frame.widgets['y_scrollbar'].set(50)

    graph_frame = Tk.Frame(big_frame)
    graph_frame.grid(column=1, row=1, sticky='news')
    graph_frame.grid_columnconfigure(0, weight=1)
    graph_frame.grid_rowconfigure(0, weight=1)

    plot = InteractivePlot(graph_frame)
    frame.plot = plot
    plot.frame.grid(column=0, row=0, sticky='news')

    toolbar_frame = Tk.Frame(big_frame)
    toolbar_frame.grid_columnconfigure(0, weight=1)
    toolbar_frame.grid_rowconfigure(0, weight=1)
    toolbar_frame.grid(column=1, row=0, sticky='news')
    navigation_toolbar = widget.NavigationToolbar(plot.canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')
    navigation_toolbar.update()

    frame.widgets['channel_option'] = widget.LabeledOptionMenu(toolbar_frame,
                                              label='channel',
                                              value='0',
                                              default='0',
                                              options=[0])
    frame.widgets['channel_option'].frame.grid(column=2, row=0, sticky='news')

    x_zoom_frame = Tk.Frame(frame, bg='orange')
    x_zoom_frame.grid_rowconfigure(0, weight=1)
    x_zoom_frame.grid_columnconfigure(3, weight=1)
    x_zoom_frame.grid(column=0, row=2, sticky='news')

    ttk.Button(x_zoom_frame, text='+').grid(column=0, row=0, sticky='news')
    ttk.Button(x_zoom_frame, text='-').grid(column=1, row=0, sticky='news')

    pan_left = ttk.Button(x_zoom_frame, text='<')
    pan_left.grid(column=2, row=0, sticky='news')
    pan_left.bind('<ButtonPress-1>', lambda e, c='x', d=-1: scroll_plot(c, d))
    pan_left.bind('<ButtonRelease-1>', stop)

    pan_right = ttk.Button(x_zoom_frame, text='>')
    pan_right.grid(column=4, row=0, sticky='news')
    pan_right.bind('<ButtonPress-1>', lambda e, c='x', d=1: scroll_plot(c, d))
    pan_right.bind('<ButtonRelease-1>', stop)


    frame.widgets['x_scrollbar'] = widget.LinkedScale(parent=x_zoom_frame,
                                                name='y_scrollbar',
                                                from_=0,
                                                to=100,
                                                orient=Tk.HORIZONTAL,
                                                command=None)
    frame.widgets['x_scrollbar'].widget.grid(column=3, row=0, sticky='news')
    frame.widgets['x_scrollbar'].widget.config(state='disabled')
    frame.widgets['x_scrollbar'].set(50)

    return frame

def scroll_plot(axis, dir):
    scroll_plot_repeat(axis, dir)
    return None

def scroll_plot_repeat(axis, dir):
    global jobid
    jobid = pymini.root.after(config.scroll_wait, scroll_plot_repeat, axis, dir)
    pymini.gp.plot.scroll(axis, dir)
    return None

def stop(e=None):
    pymini.root.after_cancel(jobid)
