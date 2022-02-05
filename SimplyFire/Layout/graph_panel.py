import tkinter as Tk
from tkinter import ttk
from PIL import Image, ImageTk
from SimplyFire.utils import custom_widgets
from SimplyFire.utils import scrollable_option_frame
from SimplyFire.DataVisualizer import trace_display
from SimplyFire.Backend import interface
from SimplyFire import app
import os
import pkg_resources




def load(parent):
    global widgets
    widgets = {}

    widgets['navigation_fps'] = Tk.IntVar(value=int(app.config.default_vars.get('default_navigation_fps')))
    widgets['navigation_mirror_x_scroll'] = Tk.IntVar(
        value=int(app.config.default_vars.get('default_navigation_mirror_x_scroll')))
    widgets['navigation_scroll_x_percent'] = Tk.DoubleVar(
        value=float(app.config.default_vars.get('default_navigation_scroll_x_percent')))
    widgets['navigation_zoom_x_percent'] = Tk.DoubleVar(
        value=float(app.config.default_vars.get('default_navigation_zoom_x_percent')))

    widgets['navigation_scroll_y_percent'] = Tk.DoubleVar(
        value=float(app.config.default_vars.get('default_navigation_scroll_y_percent')))
    widgets['navigation_mirror_y_scroll'] = Tk.IntVar(
        value=int(app.config.default_vars.get('default_navigation_mirror_y_scroll')))
    widgets['navigation_zoom_y_percent'] = Tk.DoubleVar(
        value=float(app.config.default_vars.get('default_navigation_zoom_y_percent')))

    ##################################################
    #                    Methods                     #
    ##################################################
    def force_channel(event=None):
        if widgets['force_channel'].get() == '1':
           widgets['force_channel_id'].config(state='normal')
        else:
            widgets['force_channel_id'].config(state='disabled')

    def scroll_x(dir):
        # trace_display.start_animation()
        scroll_x_repeat(
            dir * int(widgets['navigation_mirror_x_scroll'].get()),
            int(widgets['navigation_fps'].get()),
            float(widgets['navigation_scroll_x_percent'].get())
        )
    def scroll_y(dir):
        # trace_display.start_animation()
        scroll_y_repeat(
            dir * int(widgets['navigation_mirror_y_scroll'].get()),
            int(widgets['navigation_fps'].get()),
            float(widgets['navigation_scroll_y_percent'].get())
        )

    def scroll_x_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), scroll_x_repeat, dir, fps, percent)
        trace_display.scroll_x_by(dir, percent)
        pass

    def scroll_y_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), scroll_y_repeat, dir, fps, percent)
        trace_display.scroll_y_by(dir, percent)
        pass

    def zoom_x(dir):
        zoom_x_repeat(dir, int(widgets['navigation_fps'].get()),
                      float(widgets['navigation_zoom_x_percent'].get()))
    def zoom_y(dir):
        zoom_y_repeat(dir, int(widgets['navigation_fps'].get()),
                      float(widgets['navigation_zoom_y_percent'].get()))

    def zoom_x_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), zoom_x_repeat, dir, fps, percent)
        trace_display.zoom_x_by(dir, percent)
        return None

    def zoom_y_repeat(dir, fps, percent):
        global jobid
        jobid = app.root.after(int(1000 / fps), zoom_y_repeat, dir, fps, percent)
        trace_display.zoom_y_by(dir, percent)
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

    IMG_DIR = pkg_resources.resource_filename('PyMini', 'img/')

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

    graph_frame = trace_display.load(big_frame) # can be replaced with any other plotting module  - must return a frame that can be gridded
    graph_frame.grid(column=1, row=1, sticky='news')

    upper_frame = Tk.Frame(big_frame)
    upper_frame.grid_columnconfigure(0, weight=1)
    upper_frame.grid_rowconfigure(0, weight=1)
    upper_frame.grid(column=1,row=0, sticky='news')


    toolbar_frame = Tk.Frame(upper_frame)
    toolbar_frame.grid_columnconfigure(0, weight=1)
    toolbar_frame.grid(column=0, row=0, sticky='news')
    navigation_toolbar = custom_widgets.NavigationToolbar(trace_display.canvas, toolbar_frame)
    navigation_toolbar.grid(column=0, row=0, sticky='news')

    widgets['trace_info'] = custom_widgets.VarLabel(toolbar_frame, text='no file open')
    widgets['trace_info'].grid(column=0, row=1, sticky='news')

    channel_frame = scrollable_option_frame.OptionFrame(upper_frame)#, scrollbar = False)
    channel_frame.grid(column=1, row=0, sticky='ews')
    channel_frame.grid_rowconfigure(0, weight=1)
    channel_frame.grid_rowconfigure(1, weight=1)
    channel_frame.grid_columnconfigure(0, weight=1)

    widgets['channel_option'] = channel_frame.insert_label_optionmenu(
        name='channel_option',
        text='channel',
        value='',
        default='',
        options=[''],
    )

    widgets['force_channel'] = channel_frame.insert_label_checkbox(
        name='force_channel',
        text='Always open the same channel:',
        onvalue=1,
        offvalue=-1,
        command=force_channel
    )

    widgets['force_channel_id'] = custom_widgets.VarEntry(
        parent=widgets['force_channel'].master,
        name='force_channel_id',
        validate_type='int',
        value=app.config.user_vars['force_channel_id'],
        default=app.config.default_vars['default_force_channel_id']
    )
    force_channel()
    widgets['force_channel_id'].grid(column=2, row=0, sticky='ews')

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

    return frame

def scroll_x_to(e):
    interface.focus()
    trace_display.scroll_x_to(e)

def scroll_y_to(e):
    interface.focus()
    trace_display.scroll_y_to(e)
def stop(e=None):
    app.root.after_cancel(jobid)
    trace_display.update_x_scrollbar()
    trace_display.update_y_scrollbar()
    interface.focus()
