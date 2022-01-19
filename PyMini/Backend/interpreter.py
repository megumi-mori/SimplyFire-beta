from PyMini import app
from PyMini.Backend import interface
from PyMini.config import config

# debugging
# from time import time
def initialize():

    global navigation_speed
    navigation_speed = 1
    global multi_select
    multi_select = False
    global scrolling_x
    scrolling_x = False
    global scrolling_y
    scrolling_y = False
    global zooming_x
    zooming_x = False
    global zooming_y
    zooming_y = False


    ################################
    # trace marker manipulation
    ################################
    for key in config.key_deselect:
        bind_key(key, press_function=unselect_key, target=app.trace_display.canvas.get_tk_widget())
        bind_key(key, press_function=unselect_key, target=app.data_display.table, add="")

    for key in config.key_delete:
        bind_key(key, release_function=delete_key, target=app.trace_display.canvas.get_tk_widget())

    for key in config.key_select_all:
        bind_key(key, press_function=select_all_key, target=app.trace_display.canvas.get_tk_widget())

    for key in config.key_select_window:
        bind_key_dp(key, press_function=select_window_key)


    for key in config.key_multi_select:
        bind_key_dp(key,
                 press_function=lambda e:exec('global multi_select; multi_select=True'),
                 release_function=lambda e: exec('global multi_select; multi_select=False'))

    #######################
    # navigation keys
    #######################
    for key in config.key_pan_left:
        bind_key_dp(key, press_function=lambda e, d=-1: scroll_x_key(e, d),
                    release_function=lambda e: stop_x_scroll())
                 # release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_x_scroll())
            bind_key_dp(key.lowerw(), release_function=lambda e: stop_x_scroll())
             # release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        except:
            pass
    for key in config.key_pan_right:
        bind_key_dp(key, press_function=lambda e, d=1: scroll_x_key(e, d),
                    release_function=lambda e: stop_x_scroll())
                 # release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_x_scroll())
            bind_key_dp(key.upper(), release_function=lambda e: stop_x_scroll())
                     # release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        except:
            pass

    for key in config.key_pan_up:
        bind_key_dp(key, press_function=lambda e, d=1: scroll_y_key(e, d),
                    release_function=lambda e: stop_y_scroll())
                 # release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_y_scroll())
            bind_key_dp(key.lower(), release_function=lambda e: stop_y_scroll())
                     # release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        except:
            pass

    for key in config.key_pan_down:
        bind_key_dp(key, press_function=lambda e, d=-1: scroll_y_key(e, d),
                    release_function=lambda e: stop_y_scroll())
                 # release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_y_scroll())
            bind_key_dp(key.lower(), release_function=lambda e: stop_y_scroll())
                     # release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        except:
            pass

    for key in config.key_scroll_rapid:
        bind_key_dp(key, press_function=lambda e:exec('global navigation_speed; navigation_speed=2'),
                 release_function=lambda e: exec('global navigation_speed; navigation_speed=1'))

    for key in config.key_zoom_in_x:
        bind_key_dp(key, press_function=lambda e, d=1:zoom_x_key(e, d),
                 release_function=lambda e: stop_x_zoom())
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_x_zoom())
            bind_key_dp(key.lower(), release_function=lambda e: stop_x_zoom())
        except:
            pass
    for key in config.key_zoom_out_x:
        bind_key_dp(key, press_function=lambda e, d=-1:zoom_x_key(e, d),
                 release_function=lambda e: stop_x_zoom())
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(),release_function=lambda e: stop_x_zoom())
            bind_key_dp(key.lower(), release_function=lambda e: stop_x_zoom())
        except:
            pass

    bind_key_dp('<FocusOut>', press_function=lambda e: stop_all())
    for key in config.key_zoom_in_y:
        bind_key_dp(key, press_function=lambda e, d=1:zoom_y_key(e, d),
                 release_function=lambda e: stop_y_zoom())
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.upper(), release_function=lambda e: stop_y_zoom())
            bind_key_dp(key.lower(), release_function=lambda e: stop_y_zoom())
        except:
            pass
    for key in config.key_zoom_out_y:
        bind_key_dp(key, press_function=lambda e, d=-1:zoom_y_key(e, d),
                 release_function=lambda e: stop_y_zoom())
        # if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
        try:
            bind_key_dp(key.lower(), release_function=lambda e: stop_y_zoom())
            bind_key_dp(key.upper(), release_function=lambda e: stop_y_zoom())
        except:
            pass
    for key in config.key_select:
        bind_key_dp(key, release_function=interface.select_left)



    ######################################
    # Toolbar Toggle
    ######################################
    for key in config.key_toolbar_pan:
        bind_key_dp(key, press_function=lambda e:toolbar_toggle_pan())
    for key in config.key_toolbar_zoom:
        bind_key_dp(key, press_function=lambda e:toolbar_toggle_zoom())

    #######################################
    # Mini analysis
    #######################################
    for key in config.key_find_all:
        bind_key(key, press_function=lambda e:app.detector_tab.find_all_button.invoke(), target=app.trace_display.canvas.get_tk_widget())
        bind_key(key, press_function=lambda e:app.detector_tab.find_all_button.invoke(), target=app.data_display.table)
    for key in config.key_find_in_window:
        bind_key(key, press_function=lambda e:app.detector_tab.find_in_window_button.invoke(), target=app.trace_display.canvas.get_tk_widget())
        bind_key(key, press_function=lambda e:app.detector_tab.find_in_window_button.invoke(), target=app.data_display.table)
    #######################################
    # Canvas Mouse Events
    #######################################

    global event_pick
    event_pick = False
    global mouse_move
    mouse_move = False
    global drag_coord_start
    drag_coord_start = None
    global drag_coord_end
    drag_coord_end = None
    app.trace_display.canvas.mpl_connect('pick_event', plot_event_pick)
    app.trace_display.canvas.mpl_connect('button_press_event', plot_mouse_press)
    app.trace_display.canvas.mpl_connect('motion_notify_event', plot_mouse_move)
    app.trace_display.canvas.mpl_connect('button_release_event', plot_mouse_release)

    #######################################
    # Global Keys
    #######################################
    for key in config.key_undo:
        app.root.bind(key, interface.undo)

def bind_key_dp(key, press_function=None, release_function=None, add='+'):
    if key is None:
        return None
    bind_key(key, press_function, release_function, app.data_display.table, add=add)
    bind_key(key, press_function, release_function, app.trace_display.canvas.get_tk_widget(), add=add)
    bind_key(key, press_function, release_function, app.results_display.table, add=add)
    bind_key(key, press_function, release_function, app.evoked_data_display.table, add=add)

def bind_key_pg(key, press_function=None, release_function=None, add='+'):
    if key is None:
        return None
    bind_key(key, press_function, release_function, app.param_guide.canvas.get_tk_widget(), add=add)

def bind_key(key, press_function=None, release_function=None, target=None, add='+'):
    if key is None:
        return None
    # use for regular key press and release event binding
    # key binding must have '<' and '>'
    key_format = key.strip('<')
    key_format = key_format.strip('>')
    pkey_upper = key_format.split('-')
    pkey_lower = key_format.split('-')
    for i, k in enumerate(pkey_upper):
        if len(k) == 1:
            pkey_upper[i] = k.upper()
            pkey_lower[i] = k.lower()
    pkey = ['-'.join(pkey_upper), '-'.join(pkey_lower)]
    if press_function is not None:
        for k in pkey:
            if '<' in key:
                k = f'<{k}>'
            try:
                target.bind(k, press_function, add=add)
            except: # remove key specifiers
                target.bind(k.replace('_L', "").replace('_R', ""), press_function, add=add)
    if release_function is not None:
        for k in pkey:
            for r in k.split('-'):
                if r!='Key':
                    target.bind('<KeyRelease-{}>'.format(r),
                                release_function, add="+")

# app.trace_display mouse events
def plot_mouse_press(event):
    if app.trace_display.canvas.toolbar.mode == "" and event.button == 3:
        global drag_coord_start
        if event.xdata and event.ydata:
            drag_coord_start = (event.xdata, event.ydata)

def plot_mouse_move(event):
    global drag_coord_start
    global drag_coord_end
    if app.trace_display.canvas.toolbar.mode == "" and event.button == 3 and event.xdata and event.ydata:
        if drag_coord_start:
            xlim = app.trace_display.ax.get_xlim()
            ylim = app.trace_display.ax.get_ylim()
            width = xlim[1] - xlim[0]
            height = ylim[1] - ylim[0]
            pad = 0
            if xlim[0] + width * pad / 100 < event.xdata < xlim[1] - width * pad / 100 and ylim[
                0] + height * pad / 100 < event.ydata < \
                    ylim[1] + height * pad / 100:
                drag_coord_end = (event.xdata, event.ydata)
                app.trace_display.draw_rect(drag_coord_start, drag_coord_end)
                return
        drag_coord_end = (event.xdata, event.ydata)

def plot_event_pick(event):
    global event_pick
    event_pick = True
    if app.widgets['analysis_mode'].get() == 'mini' and app.widgets['trace_mode'].get() == 'continuous':
        xdata, ydata = event.artist.get_offsets()[event.ind][0]
        if multi_select:
            try:
                app.data_display.table.selection_toggle(str(xdata))
                # app.data_display.table.see(str(xdata))
            except:
                app.data_display.table.selection_toggle(str(round(xdata,interface.recordings[0].x_sigdig)))
                # app.data_display.table.see(str(round(xdata, interface.recordings[0].x_sigdig)))
            return
        try:
            app.data_display.table.selection_set(str(xdata))
            # app.data_display.table.see(str(xdata))
        except:
            app.data_display.table.selection_set(str(round(xdata, interface.recordings[0].x_sigdig)))
            # app.data_display.table.see(str(round(xdata, interface.recordings[0].x_sigdig)))
        # data_display.toggle_one(str(xdata))

def plot_mouse_release(event):
    global event_pick
    if event_pick:
        event_pick = False
        return
    if app.trace_display.canvas.toolbar.mode == 'pan/zoom' or app.trace_display.canvas.toolbar.mode == 'zoom rect':
        # make sure the plot does not go out of xlim bounds
        app.trace_display.scroll_x_by(percent=0)
        app.trace_display.zoom_x_by(percent=0)
        return None

    if app.trace_display.canvas.toolbar.mode != "":
        # take care of other cases here
        return None

    # plot is clicked, not zoom/pan or zoom rect
    global drag_coord_end
    global drag_coord_start
    if drag_coord_start and event.button == 3:
        # take care of rect multiselection here
        if event.xdata and event.ydata:
            drag_coord_end = (event.xdata, event.ydata)
        if app.widgets['analysis_mode'].get() == 'mini' and app.widgets['trace_mode'].get() == 'continuous':
            interface.highlight_events_in_range((drag_coord_start[0], drag_coord_end[0]),
                                             (drag_coord_start[1], drag_coord_end[1]))
        elif app.widgets['trace_mode'].get() == 'overlay':
            interface.highlight_sweep_in_range((drag_coord_start[0], drag_coord_end[0]),
                                             (drag_coord_start[1], drag_coord_end[1]),
                                               draw=True)
        drag_coord_end = None
        drag_coord_start = None
        app.trace_display.draw_rect(drag_coord_start, drag_coord_end)
        return None

    if event.button == 3:
        return None

    if app.widgets['trace_mode'].get() == 'overlay' and event.xdata is not None:
        # overlay, a trace may have been selected
        interface.select_trace_from_plot(event.xdata, event.ydata)
        return None
    if app.widgets['trace_mode'].get() == 'continuous' and event.xdata is not None and app.widgets[
        'analysis_mode'].get() == 'mini' and event.button==1:
        interface.pick_event_manual(event.xdata)

# app.trace_display navigation by key-press
def scroll_x_key(event, direction):
    global scrolling_x
    # if not scrolling_x:
    #     app.trace_display.scroll_x_by(direction * int(app.widgets['navigation_mirror_x_scroll'].get())*navigation_speed,
    #                           float(app.widgets['navigation_scroll_percent'].get()))
    if not scrolling_x:
        scroll_x_repeat(direction * int(app.widgets['navigation_mirror_x_scroll'].get()),
                     int(app.widgets['navigation_fps'].get()),
                     float(app.widgets['navigation_scroll_percent'].get()) * navigation_speed)
    scrolling_x = True

def scroll_y_key(event, direction):
    global scrolling_y
    if not scrolling_y:
        # app.trace_display.scroll_y_by(direction * int(app.widgets['navigation_mirror_x_scroll'].get())*navigation_speed,
        #                       float(app.widgets['navigation_scroll_percent'].get()))
        scroll_y_repeat(direction * int(app.widgets['navigation_mirror_y_scroll'].get()),
                     int(app.widgets['navigation_fps'].get()),
                     float(app.widgets['navigation_scroll_percent'].get()))
    scrolling_y = True

def scroll_x_repeat(direction, fps, percent):
    global jobid_x_scroll
    jobid_x_scroll = app.root.after(int(1000 / fps), scroll_x_repeat, direction, fps, percent)
    app.trace_display.scroll_x_by(direction, percent)
    pass

def scroll_y_repeat(direction, fps, percent):
    global jobid_y_scroll
    jobid_y_scroll = app.root.after(int(1000 / fps), scroll_y_repeat, direction, fps, percent)
    app.trace_display.scroll_y_by(direction, percent * navigation_speed)
    pass

def stop_x_scroll(e=None):
    global jobid_x_scroll
    global scrolling_x
    scrolling_x = False
    try:
        app.root.after_cancel(jobid_x_scroll)
    except:
        pass

def stop_y_scroll(e=None):
    global jobid_y_scroll
    global scrolling_y
    scrolling_y = False
    try:
        app.root.after_cancel(jobid_y_scroll)
    except:
        pass

def stop_all(e=None):
    global jobid_x_scroll
    global jobid_y_scroll
    global jobid_x_zoom
    global jobid_y_zoom

    global scrolling_y
    global scrolling_x
    global zooming_x
    global zooming_y

    scrolling_x = False
    scrolling_y = False
    zooming_x = False
    zooming_y = False
    try:
        app.root.after_cancel(jobid_x_scroll)
    except:
        pass
    try:
        app.root.after_cancel(jobid_y_scroll)
    except:
        pass
    try:
        app.root.after_cancel(jobid_x_zoom)
    except:
        pass
    try:
        app.root.after_cancel(jobid_y_zoom)
    except:
        pass

def zoom_x_key(event, direction):
    global zooming_x
    if not zooming_x:
        zoom_x_repeat(direction,
                      int(app.widgets['navigation_fps'].get()),
                      float(app.widgets['navigation_zoom_percent'].get()))
    zooming_x = True

def zoom_x_repeat(direction, fps, percent):
    global jobid_x_zoom
    jobid_x_zoom = app.root.after(int(1000/fps), zoom_x_repeat, direction, fps, percent)
    app.trace_display.zoom_x_by(direction, percent)
    pass

def stop_x_zoom(e=None):
    global jobid_x_zoom
    global zooming_x
    try:
        app.root.after_cancel(jobid_x_zoom)
    except:
        pass
    zooming_x = False

def zoom_y_key(event, direction):
    global zooming_y
    if not zooming_y:
        zoom_y_repeat(
            direction,
            int(app.widgets['navigation_fps'].get()),
            float(app.widgets['navigation_zoom_percent'].get())
        )
    zooming_y = True

def zoom_y_repeat(direction, fps, percent):
    global jobid_y_zoom
    jobid_y_zoom = app.root.after(int(1000 / fps), zoom_y_repeat, direction, fps, percent)
    app.trace_display.zoom_y_by(direction, percent)

def stop_y_zoom(e=None):
    global jobid_y_zoom
    global zooming_y
    try:
        app.root.after_cancel(jobid_y_zoom)
    except:
        pass
    zooming_y = False

# app.trace_display navigation_toolbar control
def toolbar_toggle_pan():
    app.trace_display.canvas.toolbar.pan()

def toolbar_toggle_zoom():
    app.trace_display.canvas.toolbar.zoom()

# data_display and app.trace_display data item interaction
def unselect_key(event):
    if app.widgets['analysis_mode'].get() == 'mini' and app.widgets['trace_mode'].get() == 'continuous':
        app.data_display.unselect()
        return None
    if app.widgets['trace_mode'].get() == 'overlay':
        interface.unhighlight_all_sweeps()
    pass

def delete_key(event):
    if app.widgets['analysis_mode'].get() == 'mini' and app.widgets['trace_mode'].get() == 'continuous':
        app.data_display.delete_selected()
        return
    if app.widgets['trace_mode'].get() == 'overlay':
        interface.hide_highlighted_sweep()

    # if app.widgets['trace_mode'].get() == 'overlay':
    #     interface.hide_highlighted_sweep()
    pass

def select_all_key(event):
    # if app.widgets['trace_mode'].get() == 'overlay':
    #     interface.highlight_all_sweeps()
    if app.widgets['analysis_mode'].get() == 'mini' and app.root.focus_get() == app.trace_display.canvas.get_tk_widget():
        app.data_display.dataframe.select_all()
    pass

def select_window_key(event=None):
    xlim = app.trace_display.ax.get_xlim()
    ylim = app.trace_display.ax.get_ylim()
    if app.widgets['analysis_mode'].get() == 'mini' and app.widgets['trace_mode'].get() == 'continuous':
        interface.highlight_events_in_range(xlim, ylim)
    elif app.widgets['trace_mode'].get() == 'overlay':
        interface.highlight_sweep_in_range(xlim, ylim,
                                           draw=True)
