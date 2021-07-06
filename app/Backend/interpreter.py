from DataVisualizer import trace_display, data_display
import pymini
from Backend import interface
from config import config
def initialize():

    global scroll_speed
    scroll_speed = 1
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



    # plot manipulation
    for key in config.key_deselect:
        bind_key_dp(key, press_function=unselect_key)

    for key in config.key_delete:
        bind_key_dp(key, press_function=delete_key)

    for key in config.key_select_all:
        bind_key_dp(key, press_function=select_all_key)

    for key in config.key_multi_select:
        bind_key_dp(key,
                 press_function=lambda e:exec('global multi_select; multi_select=True'),
                 release_function=lambda e: exec('global multi_select; multi_select=False'))

    # navigation keys
    for key in config.key_pan_left:
        bind_key_dp(key, press_function=lambda e, d=-1: pan_x_key(e, d),
                 release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=-1: pan_x_key(e, d),
                 release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
            except:
                pass
    for key in config.key_pan_right:
        bind_key_dp(key, press_function=lambda e, d=1: pan_x_key(e, d),
                 release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=1: pan_x_key(e, d),
                         release_function=lambda e: exec('global scrolling_x; scrolling_x=False'))
            except:
                pass

    for key in config.key_pan_up:
        bind_key_dp(key, press_function=lambda e, d=1: pan_y_key(e, d),
                 release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=1: pan_y_key(e, d),
                         release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
            except:
                pass

    for key in config.key_pan_down:
        bind_key_dp(key, press_function=lambda e, d=-1: pan_y_key(e, d),
                 release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=-1: pan_y_key(e, d),
                         release_function=lambda e: exec('global scrolling_y; scrolling_y=False'))
            except:
                pass

    for key in config.key_scroll_rapid:
        bind_key_dp(key, press_function=lambda e:exec('global scroll_speed; scroll_speed=2'),
                 release_function=lambda e: exec('global scroll_speed; scroll_speed=1'))

    for key in config.key_zoom_in_x:
        bind_key_dp(key, press_function=lambda e, d=1:zoom_x_key(e, d),
                 release_function=lambda e: exec('global zooming_x; zooming_x=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=1: zoom_x_key(e, d),
                         release_function=lambda e: exec('global zooming_x; zooming_x=False'))
            except:
                pass
    for key in config.key_zoom_out_x:
        bind_key_dp(key, press_function=lambda e, d=-1:zoom_x_key(e, d),
                 release_function=lambda e: exec('global zooming_x; zooming_x=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key.upper(), press_function=lambda e, d=-1: zoom_x_key(e, d),
                         release_function=lambda e: exec('global zooming_x; zooming_x=False'))
            except:
                pass
    for key in config.key_zoom_in_y:
        bind_key_dp(key, press_function=lambda e, d=1:zoom_y_key(e, d),
                 release_function=lambda e: exec('global zooming_y; zooming_y=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key, press_function=lambda e, d=1: zoom_y_key(e, d),
                        release_function=lambda e: exec('global zooming_y; zooming_y=False'))
            except:
                pass
    for key in config.key_zoom_out_y:
        bind_key_dp(key, press_function=lambda e, d=-1:zoom_y_key(e, d),
                 release_function=lambda e: exec('global zooming_y; zooming_y=False'))
        if '<Shift_L>' in config.key_scroll_rapid or '<Shift_R>' in config.key_scroll_rapid:
            try:
                bind_key_dp(key, press_function=lambda e, d=-1: zoom_y_key(e, d),
                        release_function=lambda e: exec('global zooming_y; zooming_y=False'))
            except:
                pass


    ######################################
    # Toolbar Toggle
    ######################################
    for key in config.key_toolbar_pan:
        bind_key_dp(key, press_function=lambda e:trace_display.canvas.toolbar.pan())
    for key in config.key_toolbar_zoom:
        bind_key_dp(key, press_function=lambda e:trace_display.canvas.toolbar.zoom())

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
    trace_display.canvas.mpl_connect('pick_event', plot_event_pick)
    trace_display.canvas.mpl_connect('button_press_event', plot_mouse_press)
    trace_display.canvas.mpl_connect('motion_notify_event', plot_mouse_move)
    trace_display.canvas.mpl_connect('button_release_event', plot_mouse_release)


def initialize_param_guide():
    for key in config.key_toolbar_pan:
        bind_key_pg(key, press_function=lambda e: param_guide.canvas.toolbar.pan())
    for key in config.key_toolbar_zoom:
        bind_key_dp(key, press_function=lambda e: param_guide.canvas.toolbar.zoom())
    pass

def bind_key_dp(key, press_function=None, release_function=None):
    bind_key(key, press_function, release_function, data_display.table)
    bind_key(key, press_function, release_function, trace_display.canvas.get_tk_widget())

def bind_key_pg(key, press_function=None, release_function=None):
    bind_key(key, press_function, release_function, param_guide.canvas.get_tk_widget())

def bind_key(key, press_function=None, release_function=None, target=None):
    # use for regular key press and release event binding
    if press_function is not None:
        target.bind(key, press_function, add="+")
    if release_function is not None:
        if key[0] == '<':
            rkey = key.strip('<')
            rkey = rkey.strip('>')
        else:
            rkey=key
        target.bind('<KeyRelease-{}>'.format(rkey),
                                release_function, add="+")


# trace_display mouse events
def plot_mouse_press(event):
    if trace_display.canvas.toolbar.mode == "" and event.button == 3:
        global drag_coord_start
        if event.xdata and event.ydata:
            drag_coord_start = (event.xdata, event.ydata)

def plot_mouse_move(event):
    global drag_coord_start
    global drag_coord_end
    if trace_display.canvas.toolbar.mode == "" and event.button == 3 and event.xdata and event.ydata:
        if drag_coord_start:
            xlim = trace_display.ax.get_xlim()
            ylim = trace_display.ax.get_ylim()
            width = xlim[1] - xlim[0]
            height = ylim[1] - ylim[0]
            pad = 0
            if xlim[0] + width * pad / 100 < event.xdata < xlim[1] - width * pad / 100 and ylim[
                0] + height * pad / 100 < event.ydata < \
                    ylim[1] + height * pad / 100:
                drag_coord_end = (event.xdata, event.ydata)
                trace_display.draw_rect(drag_coord_start, drag_coord_end)
                return
        drag_coord_end = (event.xdata, event.ydata)

def plot_event_pick(event):
    global event_pick
    event_pick = True
    if pymini.widgets['analysis_mode'].get() == 'mini' and pymini.widgets['trace_mode'].get() == 'continuous':
        xdata, ydata = event.artist.get_offsets()[event.ind][0]
        if multi_select:
            data_display.table.selection_toggle(str(xdata))
            data_display.table.see(str(xdata))
            return
        print('select event at {}'.format(xdata))
        data_display.table.selection_set(str(xdata))
        # data_display.toggle_one(str(xdata))

def plot_mouse_release(event):
    global event_pick
    if event_pick:
        event_pick = False
        return

    if trace_display.canvas.toolbar.mode == 'pan/zoom':
        # make sure the plot does not go out of xlim bounds
        trace_display.scroll_x_by(percent=0)
        trace_display.zoom_x_by(percent=0)
        return None

    if trace_display.canvas.toolbar.mode != "":
        # take care of other cases here
        return None

    # plot is clicked, not zoom/pan or zoom rect
    global drag_coord_end
    global drag_coord_start
    if drag_coord_start and event.button == 3:
        # take care of rect multiselection here
        if event.xdata and event.ydata:
            drag_coord_end = (event.xdata, event.ydata)
        if pymini.widgets['analysis_mode'].get() == 'mini' and pymini.widgets['trace_mode'].get() == 'continuous':
            interface.highlight_events_in_range((drag_coord_start[0], drag_coord_end[0]),
                                             (drag_coord_start[1], drag_coord_end[1]))
        elif pymini.widgets['trace_mode'].get() == 'overlay':
            interface.highlight_sweep_in_range((drag_coord_start[0], drag_coord_end[0]),
                                             (drag_coord_start[1], drag_coord_end[1]),
                                               draw=True)
        drag_coord_end = None
        drag_coord_start = None
        trace_display.draw_rect(drag_coord_start, drag_coord_end)
        return None

    if event.button == 3:
        return None

    if pymini.widgets['trace_mode'].get() == 'overlay' and event.xdata is not None:
        # overlay, a trace may have been selected
        interface.select_trace_from_plot(event.xdata, event.ydata)
    if pymini.widgets['trace_mode'].get() == 'continuous' and event.xdata is not None and pymini.widgets[
        'analysis_mode'].get() == 'mini' and event.button==1:
        interface.pick_event_manual(event.xdata)

# trace_display navigation by key-press
def pan_x_key(event, direction):
    #voids right click drag
    global drag_coord_start
    drag_coord_start = None
    global drag_coord_end
    drag_coord_end = None

    global scrolling_x
    if not scrolling_x:
        trace_display.scroll_x_by(direction * int(pymini.widgets['navigation_mirror_x_scroll'].get())*scroll_speed,
                              float(pymini.widgets['navigation_scroll_percent'].get()))
    scrolling_x = True
def pan_y_key(event, direction):
    # voids right click drag
    global drag_coord_start
    drag_coord_start = None
    global drag_coord_end
    drag_coord_end = None

    global scrolling_y
    if not scrolling_y:
        trace_display.scroll_y_by(direction * int(pymini.widgets['navigation_mirror_x_scroll'].get())*scroll_speed,
                              float(pymini.widgets['navigation_scroll_percent'].get()))
    scrolling_y = True

def zoom_x_key(event, direction):
    # voids right click drag
    global drag_coord_start
    drag_coord_start = None
    global drag_coord_end
    drag_coord_end = None

    global zooming_x
    if not zooming_x:
        trace_display.zoom_x_by(direction * scroll_speed,
                                float(pymini.widgets['navigation_zoom_percent'].get()))
    zooming_x = True

def zoom_y_key(event, direction):
    # voids right click drag
    global drag_coord_start
    drag_coord_start = None
    global drag_coord_end
    drag_coord_end = None

    global zooming_y
    if not zooming_y:
        trace_display.zoom_y_by(direction * scroll_speed,
                                float(pymini.widgets['navigation_zoom_percent'].get()))
    zooming_y = True

# trace_display navigation_toolbar control
def toolbar_toggle_pan(event, toolbar):
    toolbar.pan()
    pass

def toolbar_toggle_zoom(event, toolbar):
    toolbar.zoom()
    pass
# data_display and trace_display data item interaction
def unselect_key(event):
    data_display.unselect()
    if pymini.widgets['trace_mode'].get() == 'overlay':
        interface.unhighlight_all_sweeps()
    pass

def delete_key(event):
    if pymini.widgets['analysis_mode'].get() == 'mini':
        sel = data_display.table.selection()
        data_display.table.selection_remove(*sel)
        interface.delete_event([i for i in sel])
        data_display.table.update()
        try:
            data_display.table.selection_set(table.next(sel[-1]))
        except Exception as e:
            pass
        data_display.table.delete(*sel)
    if pymini.widgets['trace_mode'].get() == 'overlay':
        interface.hide_highlighted_sweep()
    pass

def select_all_key(event):
    if pymini.widgets['trace_mode'].get() == 'overlay':
        interface.highlight_all_sweeps()
    if pymini.widgets['analysis_mode'].get() == 'mini':
        if len(data_display.selected) == len(data_display.table.get_children()):
            return
        table.selection_set(table.get_children())
    pass



