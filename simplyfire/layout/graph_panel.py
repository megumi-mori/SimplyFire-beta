"""
simplyfire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import simplyfire
import tkinter as Tk
from tkinter import ttk
from PIL import Image, ImageTk
from simplyfire.utils import custom_widgets
from simplyfire.utils import scrollable_option_frame
from simplyfire import app

import os

#### default values ####
navigation_fps = 12
navigation_mirror_x_scroll = 1
navigation_mirror_y_scroll = 1
navigation_scroll_x_percent = 10
navigation_zoom_x_percent = 10
navigation_scroll_y_percent = 10
navigation_zoom_y_percent = 10

force_channel = ''
force_channel_id = 0

#### variables ####
inputs = {}

def load(parent):
    global inputs
    ##################################################
    #                    Methods                     #
    ##################################################
    def toggle_force_channel(event=None, undo=True):
        if inputs['force_channel'].get() == '1':
            inputs['force_channel_id'].config(state='normal')
            if undo and app.interface.is_accepting_undo():
                app.interface.add_undo([
                    reset_force_channel
                ])
        else:
            inputs['force_channel_id'].config(state='disabled')
            if undo and app.interface.is_accepting_undo():
                app.interface.add_undo([
                    reset_force_channel
                ])
    def reset_force_channel(event=None):
        inputs['force_channel'].set({'1':'', '':'1'}[inputs['force_channel'].get()])
        toggle_force_channel(undo=False)

    def set_force_channel_id(event=None, undo=True):
        global force_channel_id
        if undo and app.interface.is_accepting_undo():
            if force_channel_id != inputs['force_channel_id'].get():
                app.interface.add_undo(
                    [
                        lambda:inputs['force_channel_id'].set(force_channel_id),
                    ]
                )
                force_channel_id = inputs['force_channel_id'].get()
        app.interface.focus()


    def scroll_x(dir):
        # trace_display.start_animation()
        scroll_x_repeat(
            dir * int(navigation_mirror_x_scroll),
            int(navigation_fps),
            float(navigation_scroll_x_percent)
        )
    def scroll_y(dir):
        # trace_display.start_animation()
        scroll_y_repeat(
            dir * int(navigation_mirror_y_scroll),
            int(navigation_fps),
            float(navigation_scroll_y_percent)
        )

    def scroll_x_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), scroll_x_repeat, dir, fps, percent)
        app.trace_display.scroll_x_by(dir, percent)
        pass

    def scroll_y_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), scroll_y_repeat, dir, fps, percent)
        app.trace_display.scroll_y_by(dir, percent)
        pass

    def zoom_x(dir):
        zoom_x_repeat(dir, int(navigation_fps),
                      navigation_zoom_x_percent)
    def zoom_y(dir):
        zoom_y_repeat(dir, int(navigation_fps),
                      float(navigation_zoom_y_percent))

    def zoom_x_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), zoom_x_repeat, dir, fps, percent)
        app.trace_display.zoom_x_by(dir, percent)
        return None

    def zoom_y_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), zoom_y_repeat, dir, fps, percent)
        app.trace_display.zoom_y_by(dir, percent)
        return None


    # frame = ScrollableOptionFrame(parent)#, False)
    frame = Tk.Frame(parent)
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

    IMG_DIR = app.config.IMG_DIR

    y_zoom_in = ttk.Button(y_zoom_frame)
    y_zoom_in.image = Tk.PhotoImage(file=os.path.join(IMG_DIR,'y_zoom_in.png'))
    y_zoom_in.config(image=y_zoom_in.image)
    y_zoom_in.grid(column=0, row=0, sticky='news')
    y_zoom_in.bind('<ButtonPress-1>', lambda e, d=1: zoom_y(d))
    y_zoom_in.bind('<ButtonRelease-1>', stop)

    y_zoom_out = ttk.Button(y_zoom_frame)
    y_zoom_out.image = Tk.PhotoImage(file=os.path.join(IMG_DIR, 'y_zoom_out.png'))
    y_zoom_out.config(image=y_zoom_out.image)
    y_zoom_out.grid(column=0, row=1, sticky='news')
    y_zoom_out.bind('<ButtonPress-1>', lambda e, d=-1: zoom_y(d))
    y_zoom_out.bind('<ButtonRelease-1>', stop)

    yscrollbar_frame = Tk.Frame(big_frame, bg='lime')
    yscrollbar_frame.grid(column=0, row=1, sticky='news')
    yscrollbar_frame.grid_columnconfigure(0, weight=1)
    yscrollbar_frame.grid_rowconfigure(1, weight=1)

    arrow = Image.open(os.path.join(IMG_DIR, 'arrow.png'))
    pan_up = ttk.Button(yscrollbar_frame)
    pan_up.image = ImageTk.PhotoImage(arrow)
    pan_up.config(image=pan_up.image)
    pan_up.grid(column=0, row=0, sticky='news')
    pan_up.bind('<ButtonPress-1>', lambda e, d=1: scroll_y(d))
    pan_up.bind('<ButtonRelease-1>', stop)
    pan_down = ttk.Button(yscrollbar_frame)
    pan_down.image = ImageTk.PhotoImage(arrow.rotate(180))
    pan_down.config(image=pan_down.image)
    pan_down.grid(column=0, row=2, sticky='news')
    pan_down.bind('<ButtonPress-1>', lambda e, d=-1: scroll_y(d))
    pan_down.bind('<ButtonRelease-1>', stop)

    global y_scrollbar
    y_scrollbar = custom_widgets.VarScale(parent=yscrollbar_frame,
                                   name='y_scrollbar',
                                   from_=0,
                                   to=100,
                                   orient=Tk.VERTICAL,
                                   command= scroll_y_to)
    y_scrollbar.grid(column=0, row=1, sticky='news')
    y_scrollbar.config(state='disabled')  # disabled until a trace is loaded
    y_scrollbar.set(50)

    graph_frame = app.trace_display.load(big_frame) # can be replaced with any other plotting module  - must return a frame that can be gridded
    graph_frame.grid(column=1, row=1, sticky='news')

    upper_frame = Tk.Frame(big_frame)
    upper_frame.grid_columnconfigure(0, weight=1)
    upper_frame.grid_rowconfigure(0, weight=1)
    upper_frame.grid(column=1,row=0, sticky='news')


    toolbar_frame = Tk.Frame(upper_frame)
    toolbar_frame.grid_columnconfigure(0, weight=1)
    toolbar_frame.grid(column=0, row=0, sticky='news')
    navigation_toolbar = custom_widgets.NavigationToolbar(app.trace_display.canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')

    inputs['trace_info'] = custom_widgets.VarLabel(toolbar_frame, text='no file open')
    inputs['trace_info'].grid(column=0, row=1, sticky='news')

    channel_frame = scrollable_option_frame.OptionFrame(upper_frame)#, scrollbar = False)
    channel_frame.grid(column=1, row=0, sticky='ews')
    channel_frame.grid_rowconfigure(0, weight=1)
    channel_frame.grid_rowconfigure(1, weight=1)
    channel_frame.grid_columnconfigure(0, weight=1)

    inputs['channel_option'] = channel_frame.insert_label_optionmenu(
        name='channel_option',
        text='channel',
        value='',
        default='',
        options=[''],
        command=app.interface.focus
    )

    inputs['force_channel'] = channel_frame.insert_label_checkbox(
        name='force_channel',
        text='Always open the same channel:',
        onvalue=1,
        offvalue=-1,
        command=toggle_force_channel,
        default=force_channel,
        value=app.config.get_value('force_channel')
    )

    inputs['force_channel_id'] = custom_widgets.VarEntry(
        parent=inputs['force_channel'].master,
        name='force_channel_id',
        validate_type='int',
        value=app.config.get_value('force_channel_id'),
        default=force_channel_id
    )
    toggle_force_channel(undo=False)
    inputs['force_channel_id'].grid(column=2, row=0, sticky='ews')
    inputs['force_channel_id'].bind('<Return>', set_force_channel_id, add='+')
    inputs['force_channel_id'].bind('<FocusOut>', set_force_channel_id, add='+')

    x_zoom_frame = Tk.Frame(frame, bg='orange')
    x_zoom_frame.grid_rowconfigure(0, weight=1)
    x_zoom_frame.grid_columnconfigure(3, weight=1)
    x_zoom_frame.grid(column=0, row=2, sticky='news')

    x_zoom_in = ttk.Button(x_zoom_frame)
    x_zoom_in.image = Tk.PhotoImage(file=os.path.join(IMG_DIR, 'x_zoom_in.png'))
    x_zoom_in.config(image=x_zoom_in.image)
    x_zoom_in.grid(column=0, row=0, sticky='news')
    x_zoom_in.bind('<ButtonPress-1>', lambda e, d=-1: zoom_x(d))
    x_zoom_in.bind('<ButtonRelease-1>', stop)
    x_zoom_out = ttk.Button(x_zoom_frame)
    x_zoom_out.image = Tk.PhotoImage(file=os.path.join(IMG_DIR, 'x_zoom_out.png'))
    x_zoom_out.config(image=x_zoom_out.image)
    x_zoom_out.grid(column=1, row=0, sticky='news')
    x_zoom_out.bind('<ButtonPress-1>', lambda e, d=1: zoom_x(d))
    x_zoom_out.bind('<ButtonRelease-1>', stop)

    pan_left = ttk.Button(x_zoom_frame)
    pan_left.image = ImageTk.PhotoImage(arrow.rotate(90))
    pan_left.config(image=pan_left.image)
    pan_left.grid(column=2, row=0, sticky='news')
    pan_left.bind('<ButtonPress-1>', lambda e, d=-1: scroll_x(d))
    pan_left.bind('<ButtonRelease-1>', stop)

    pan_right = ttk.Button(x_zoom_frame)
    pan_right.image = ImageTk.PhotoImage(arrow.rotate(270))
    pan_right.config(image=pan_right.image)
    pan_right.grid(column=4, row=0, sticky='news')
    pan_right.bind('<ButtonPress-1>', lambda e, d=1: scroll_x(d))
    pan_right.bind('<ButtonRelease-1>', stop)

    global x_scrollbar
    x_scrollbar = custom_widgets.VarScale(parent=x_zoom_frame,
                                   name='y_scrollbar',
                                   from_=0,
                                   to=100,
                                   orient=Tk.HORIZONTAL,
                                   command= scroll_x_to
                                   )
    x_scrollbar.grid(column=3, row=0, sticky='news')
    x_scrollbar.config(state='disabled')  # disabled until a trace is loaded
    x_scrollbar.set(50)
    # x_scrollbar.bind('<ButtonRelease-1>', lambda e:trace_display.update_y_scrollbar)

    for w in inputs:
        value = app.config.get_value(w)
        if value and 'channel_option' not in w:
            inputs[w].set(value)
    return frame

def scroll_x_to(e):
    app.interface.focus()
    app.trace_display.scroll_x_to(e)

def scroll_y_to(e):
    app.interface.focus()
    app.trace_display.scroll_y_to(e)
def stop(e=None):
    app.root.after_cancel(jobid)
    app.trace_display.update_x_scrollbar()
    app.trace_display.update_y_scrollbar()
    app.interface.focus()
