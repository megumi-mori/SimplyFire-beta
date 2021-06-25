import tkinter as Tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils import widget
from utils.scrollable_option_frame import ScrollableOptionFrame
from config import config
from DataVisualizer import trace_display
# from DataVisualizer.plot import InteractivePlot
import pymini
import os
import time

def load(parent):
    ##################################################
    #                    Methods                     #
    ##################################################
    def force_channel(event=None):
        if pymini.get_value('force_channel') == '1':
            pymini.get_widget('force_channel_id').config(state='normal')
        else:
            pymini.get_widget('force_channel_id').config(state='disabled')
    # def scroll_plot(axis, dir):
    #     scroll_plot_repeat(
    #         axis,
    #         dir * int(pymini.get_value('mirror_{}_scroll'.format(axis), 'plot_area')),
    #         int(pymini.get_value('nav_fps')),
    #         float(pymini.get_value('scroll_percent'))
    #     )
    #     return None

    scroll_plot = lambda axis, dir: scroll_plot_repeat(
        axis,
        dir * int(pymini.get_value('mirror_{}_scroll'.format(axis), 'plot_area')),
        int(pymini.get_value('nav_fps')),
        float(pymini.get_value('scroll_percent'))
    )
    def scroll_plot_repeat(axis, dir, fps, percent):
        global jobid
        jobid = pymini.root.after(int(1000 / fps), scroll_plot_repeat, axis, dir, fps, percent)
        trace_display.scroll(axis, dir, percent)
        return None

    def zoom_plot(axis, dir):
        zoom_plot_repeat(axis, dir, int(pymini.get_value('nav_fps')), float(pymini.get_value('zoom_percent')))
        return None

    def zoom_plot_repeat(axis, dir, fps, percent):
        global jobid
        jobid = pymini.root.after(int(1000 / fps), zoom_plot_repeat, axis, dir, fps, percent)
        trace_display.zoom(axis, dir, percent)
        return None

    def _choose_channel(event):
        pass



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

    big_frame = Tk.Frame(frame)
    big_frame.grid_columnconfigure(1, weight=1)
    big_frame.grid_rowconfigure(1, weight=1)
    big_frame.grid(column=0, row=0, sticky='news')

    y_zoom_frame = Tk.Frame(big_frame)
    y_zoom_frame.grid(column=0, row=0, sticky='ews')
    y_zoom_frame.grid_columnconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(0, weight=1)
    y_zoom_frame.grid_rowconfigure(1, weight=1)


    y_zoom_in = Tk.Button(y_zoom_frame)
    y_zoom_in.image = Tk.PhotoImage(file=os.path.join(config.DIR, 'img','y_zoom_in.png'))
    y_zoom_in.config(image=y_zoom_in.image)
    y_zoom_in.grid(column=0, row=0, sticky='news')
    y_zoom_in.bind('<ButtonPress-1>', lambda e, c='y', d=1 : zoom_plot(c, d))
    y_zoom_in.bind('<ButtonRelease-1>', stop)

    y_zoom_out = Tk.Button(y_zoom_frame)
    y_zoom_out.image = Tk.PhotoImage(file=os.path.join(config.DIR, 'img', 'y_zoom_out.png'))
    y_zoom_out.config(image=y_zoom_out.image)
    y_zoom_out.grid(column=0, row=1, sticky='news')
    y_zoom_out.bind('<ButtonPress-1>', lambda e, c='y', d=-1: zoom_plot(c, d))
    y_zoom_out.bind('<ButtonRelease-1>', stop)

    yscrollbar_frame = Tk.Frame(big_frame, bg='lime')
    yscrollbar_frame.grid(column=0, row=1, sticky='news')
    yscrollbar_frame.grid_columnconfigure(0, weight=1)
    yscrollbar_frame.grid_rowconfigure(1, weight=1)

    arrow = Image.open(os.path.join(config.DIR, 'img', 'arrow.png'))
    pan_up = Tk.Button(yscrollbar_frame)
    pan_up.image = ImageTk.PhotoImage(arrow)
    pan_up.config(image=pan_up.image)
    pan_up.grid(column=0, row=0, sticky='news')
    pan_up.bind('<ButtonPress-1>', lambda e, c='y', d=1: scroll_plot(c, d))
    pan_up.bind('<ButtonRelease-1>', stop)
    pan_down = Tk.Button(yscrollbar_frame)
    pan_down.image = ImageTk.PhotoImage(arrow.rotate(180))
    pan_down.config(image=pan_down.image)
    pan_down.grid(column=0, row=2, sticky='news')
    pan_down.bind('<ButtonPress-1>', lambda e, c='y', d=-1: scroll_plot(c, d))
    pan_down.bind('<ButtonRelease-1>', stop)

    frame.widgets['y_scrollbar'] = widget.VarScale(parent=yscrollbar_frame,
                                                      name='y_scrollbar',
                                                      from_=0,
                                                      to=100,
                                                      orient=Tk.VERTICAL,
                                                      command=None)
    frame.widgets['y_scrollbar'].grid(column=0, row=1, sticky='news')
    frame.widgets['y_scrollbar'].config(state='disabled')  # disabled until a trace is loaded
    frame.widgets['y_scrollbar'].set(50)

    graph_frame = trace_display.load(big_frame) # can be replaced with any other plotting module  - must return a frame that can be gridded
    graph_frame.grid(column=1, row=1, sticky='news')

    upper_frame = Tk.Frame(big_frame)
    upper_frame.grid_columnconfigure(0, weight=1)
    upper_frame.grid_rowconfigure(0, weight=1)
    upper_frame.grid(column=1,row=0, sticky='news')


    toolbar_frame = Tk.Frame(upper_frame)
    toolbar_frame.grid_columnconfigure(0, weight=1)
    toolbar_frame.grid(column=0, row=0, sticky='news')
    navigation_toolbar = widget.NavigationToolbar(trace_display.canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')


    pymini.widgets['trace_info'] = widget.VarLabel(toolbar_frame, text='no file open')
    pymini.widgets['trace_info'].grid(column=0, row=1, sticky='news')

    channel_frame = ScrollableOptionFrame(upper_frame, scrollbar = False)
    channel_frame.grid(column=1, row=0, sticky='ews')
    channel_frame.grid_rowconfigure(0, weight=1)
    channel_frame.grid_rowconfigure(1, weight=1)
    channel_frame.grid_columnconfigure(0, weight=1)

    pymini.widgets['channel_option'] = channel_frame.insert_label_optionmenu(
        name='channel_option',
        label='channel',
        value='',
        default='',
        options=['']
    )

    pymini.widgets['force_channel'] = channel_frame.insert_label_checkbox(
        name='force_channel',
        label='Always open the same channel:',
        onvalue=1,
        offvalue=-1,
        command=force_channel
    )

    pymini.widgets['force_channel_id'] = widget.VarEntry(
        parent=channel_frame.widgets['force_channel']._nametowidget(channel_frame.widgets['force_channel'].winfo_parent()),
        name='force_channel_id',
        validate_type='int'
    )
    force_channel()
    pymini.widgets['force_channel_id'].grid(column=2,row=0,sticky='ews')

    x_zoom_frame = Tk.Frame(frame, bg='orange')
    x_zoom_frame.grid_rowconfigure(0, weight=1)
    x_zoom_frame.grid_columnconfigure(3, weight=1)
    x_zoom_frame.grid(column=0, row=2, sticky='news')

    x_zoom_in = Tk.Button(x_zoom_frame)
    x_zoom_in.image = Tk.PhotoImage(file=os.path.join(config.DIR, 'img', 'x_zoom_in.png'))
    x_zoom_in.config(image=x_zoom_in.image)
    x_zoom_in.grid(column=0, row=0, sticky='news')
    x_zoom_in.bind('<ButtonPress-1>', lambda e, c='x', d=1 : zoom_plot(c, d))
    x_zoom_in.bind('<ButtonRelease-1>', stop)
    x_zoom_out = Tk.Button(x_zoom_frame)
    x_zoom_out.image = Tk.PhotoImage(file=os.path.join(config.DIR, 'img', 'x_zoom_out.png'))
    x_zoom_out.config(image=x_zoom_out.image)
    x_zoom_out.grid(column=1, row=0, sticky='news')
    x_zoom_out.bind('<ButtonPress-1>', lambda e, c='x', d=-1: zoom_plot(c, d))
    x_zoom_out.bind('<ButtonRelease-1>', stop)

    pan_left = Tk.Button(x_zoom_frame)
    pan_left.image = ImageTk.PhotoImage(arrow.rotate(90))
    pan_left.config(image=pan_left.image)
    pan_left.grid(column=2, row=0, sticky='news')
    pan_left.bind('<ButtonPress-1>', lambda e, c='x', d=-1: scroll_plot(c, d))
    pan_left.bind('<ButtonRelease-1>', stop)

    pan_right = Tk.Button(x_zoom_frame)
    pan_right.image = ImageTk.PhotoImage(arrow.rotate(270))
    pan_right.config(image=pan_right.image)
    pan_right.grid(column=4, row=0, sticky='news')
    pan_right.bind('<ButtonPress-1>', lambda e, c='x', d=1: scroll_plot(c, d))
    pan_right.bind('<ButtonRelease-1>', stop)

    frame.widgets['x_scrollbar'] = widget.VarScale(parent=x_zoom_frame,
                                                      name='y_scrollbar',
                                                      from_=0,
                                                      to=100,
                                                      orient=Tk.HORIZONTAL,
                                                      command=None)
    frame.widgets['x_scrollbar'].grid(column=3, row=0, sticky='news')
    frame.widgets['x_scrollbar'].config(state='disabled')  # disabled until a trace is loaded
    frame.widgets['x_scrollbar'].set(50)

    return frame









def stop(e=None):
    pymini.root.after_cancel(jobid)