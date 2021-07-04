import tkinter as Tk
from config import config
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import recording, analysis
import matplotlib.colors
import pymini
import os
import gc
import time
import datetime
import numpy as np

from Backend import interface, analyzer
from Layout import graph_panel

from DataVisualizer import data_display

temp = []
markers = {}
sweeps = {}

event_pick = False

def load(parent):
    frame = Tk.Frame(parent)
    global fig
    fig = Figure()
    fig.set_tight_layout(True)

    global ax
    ax = fig.add_subplot(111)
    fig.subplots_adjust(right=1, top=1)

    global canvas
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    ax.plot()


    ax.set_xlabel('Time (n/a)')
    ax.set_ylabel('y (n/a)')

    global default_xlim
    default_xlim = ax.get_xlim()

    global default_ylim
    default_ylim = ax.get_ylim()

    global state
    state = State()
    state.press = False
    state.move = False

    # connect user events:
    canvas.mpl_connect('pick_event', _on_event_pick)
    canvas.mpl_connect('button_press_event', _on_mouse_press)
    canvas.mpl_connect('motion_notify_event', _on_mouse_move)
    canvas.mpl_connect('button_release_event', _on_mouse_release)

    canvas.draw()
    # refresh()
    return frame
def _on_event_pick(event):
    global event_pick
    event_pick = True
    xdata, ydata = event.artist.get_offsets()[event.ind][0]
    data_display.toggle_one(str(xdata))

def _on_mouse_press(event):
    canvas.get_tk_widget().focus_set()
    if canvas.toolbar.mode == "" and event.button == 3:
        state.press_coord = (event.x, event.y)
    # print('click! {}'.format(event))
    pass

def _on_mouse_release(event):
    global event_pick
    data_display.table.focus_set()
    if canvas.toolbar.mode == 'pan/zoom':
        scroll_x_by(percent=0)
        zoom_x_by(percent=0)

    if event_pick:
        event_pick = False
        return

    if state.move:
        state.move = False
        state.release_coord = (event.x, event.y)
        print('release! {}'.format(event))

        # do something
        state.release_coord = None
        state.press_coord = None
        return None

    if canvas.toolbar.mode =="" and event.xdata and event.button == 1 and pymini.widgets['trace_mode'].get() == 'continuous':
        print('click!')
        interface.pick_event_manual(event.xdata)
        state.move = False
        state.release_coord = (None, None)
        state.press_coord = (None, None)

    pass

def _on_mouse_move(event):
    if canvas.toolbar.mode == '' and event.button == 3:
        state.move = True
        pass

    pass


################# Navigation ####################

def start_animation():
    for l in ax.lines:
        ax.draw_artist(l)
        l.set_animated(True)

def pause_animation():
    for l in ax.lines:
        ax.draw_artist(l)
        l.set_animated(False)

def scroll_x_by(dir=1, percent=0):
    dir = dir
    xlim = ax.get_xlim()
    width = xlim[1] - xlim[0]
    delta = width*percent/100
    new_lim=(xlim[0] + delta*dir, xlim[1] + delta*dir)

    if new_lim[0] < default_xlim[0]:
        delta = default_xlim[0] - new_lim[0]
        new_lim = (new_lim[0] + delta, new_lim[1] + delta)
    elif new_lim[1] > default_xlim[1]:
        delta = new_lim[1] - default_xlim[1]
        new_lim = (new_lim[0] - delta, new_lim[1] - delta)
    ax.set_xlim(new_lim)
    update_x_scrollbar(new_lim)
    # refresh()
    canvas.draw()

def scroll_y_by(dir=1, percent=0):
    dir = dir
    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]
    delta = height * percent/100
    new_lim=(ylim[0] + delta * dir, ylim[1] + delta * dir)

    ax.set_ylim(new_lim)
    # refresh()
    # update_y_scrollbar(ylim=new_lim)
    canvas.draw()

def scroll_x_to(num):
    # start_animation()
    xlim = ax.get_xlim()
    if xlim[1] == default_xlim[1] and xlim[0] == default_xlim[0]:
        graph_panel.x_scrollbar.set(50)
        return None
    start = (default_xlim[1] - default_xlim[0] - (xlim[1] - xlim[0])) * float(num)/100 + default_xlim[0]
    end = start + xlim[1] - xlim[0]

    ax.set_xlim((start,end))
    canvas.draw()
    # refresh()


def scroll_y_to(num):
    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]
    xlim = ax.get_xlim()
    ys = ax.lines[0].get_ydata()
    y = ys[analyzer.search_index(xlim[0], ax.lines[0].get_xdata())]
    y1 = float(num) / 100 * (height) + y
    ax.set_ylim((y1-height, y1))
    canvas.draw()


def center_plot_on(x, y):
    xlim = ax.get_xlim()
    ylim=ax.get_ylim()

    new_xlim = xlim
    new_ylim =ylim

    if xlim[0] < x < xlim[1] and ylim[0] < y < ylim[1]:
        return None
    if xlim[0] > x or xlim[1] < x:
        xlim_width = xlim[1] - xlim[0]
        new_xlim_left = x - xlim_width / 2
        new_xlim_right = x + xlim_width / 2

        adjust = max(0, default_xlim[0] - new_xlim_left)
        new_xlim_right += adjust
        adjust = min(0, default_xlim[1] - new_xlim_right)
        new_xlim_left += adjust

        new_xlim_left = max(default_xlim[0], new_xlim_left)
        new_xlim_right = min(default_xlim[1], new_xlim_right)

        ax.set_xlim(new_xlim_left, new_xlim_right)
        update_x_scrollbar((new_xlim_left, new_xlim_right))
        new_xlim = (new_xlim_left, new_xlim_right)

    if ylim[0] > y or ylim[1] < y:
        ylim_width = ylim[1] - ylim[0]
        new_ylim_bottom = y - ylim_width / 2
        new_ylim_top = y + ylim_width / 2
        ax.set_ylim(new_ylim_bottom, new_ylim_top)
        new_ylim = (new_ylim_bottom, new_ylim_top)
    update_y_scrollbar(xlim=new_xlim, ylim=new_ylim)
    canvas.draw()

def center_plot_area(x1, x2, y1, y2):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    pad = 0.05
    if x2-x1 < xlim[1] - xlim[0]: # current x-axis zoom will fit the desired range
        delta = ((xlim[1]-xlim[0])/2 + xlim[0]) - ((x2 - x1)/2 + x1)
        new_xlim_left = xlim[0] - delta
        new_xlim_right = xlim[1] - delta
    else:

        padx = (x2-x1) * pad

        new_xlim_left = max(min(xlim[0], x1-padx), default_xlim[0])
        new_xlim_right = min(max(xlim[1], x2+padx), default_xlim[1])

    pady = (y2-y1)*pad

    new_ylim_bottom = min(ylim[0], y1-pady)
    new_ylim_top = max(ylim[1], y2+pady)

    ax.set_xlim(new_xlim_left, new_xlim_right)
    update_x_scrollbar((new_xlim_left, new_xlim_right))
    ax.set_ylim(new_ylim_bottom, new_ylim_top)
    update_y_scrollbar(xlim=(new_xlim_left, new_xlim_right),ylim=(new_ylim_bottom, new_ylim_top))

    canvas.draw()

def zoom_x_by(dir=1, percent=0, event=None):
    win_lim = ax.get_xlim()
    delta = (win_lim[1] - win_lim[0]) * percent * dir / 100
    center_pos = 0.5
    try:
        center_pos = (event.xdata - win_lim[0]) / (win_lim[1] - win_lim[0])
    except:
        pass
    new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)

    if new_lim[0] < default_xlim[0]:
        width = new_lim[1] - new_lim[0]
        new_lim = (default_xlim[0], min(new_lim[0] + width, default_xlim[1]))
    elif new_lim[1] > default_xlim[1]:
        width = new_lim[1] - new_lim[0]
        new_lim = (max(new_lim[1] - width, default_xlim[0]), default_xlim[1])

    ax.set_xlim(new_lim)
    update_x_scrollbar(new_lim)
    canvas.draw()
    # refresh()
def zoom_y_by(dir=1, percent=0, event=None):
    win_lim = ax.get_ylim()
    delta = (win_lim[1] - win_lim[0]) * percent * dir / 100
    center_pos = 0.5
    try:
        center_pos = (event.ydata - win_lim[0]) / (win_lim[1] - win_lim[0])
    except:
        pass
    new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)
    ax.set_ylim(new_lim)
    canvas.draw()
    # refresh()

def zoom_by(axis, dir=1, percent=0, event=None):
    """
    zooms in/out of the axes by percentage specified in config
    :param axis: 'x' for x-axis, 'y' for y-axis. currently does not support both
    :param dir: 1 to zoom in , -1 to zoom out
    :param event:
    :return:
    """
    if axis == 'x':
        win_lim = ax.get_xlim()
    elif axis == 'y':
        win_lim = ax.get_ylim()
    else:
        return None

    delta = (win_lim[1] - win_lim[0]) * percent * dir / 100
    center_pos = 0.5
    try:
        if axis == 'x':
            center_pos = (event.xdata - win_lim[0]) / (win_lim[1] - win_lim[0])
        elif axis == 'y':
            center_pos = (event.ydata - win_lim[0]) / (win_lim[1] - win_lim[0])
    except:
        center_pos = 0.5

    new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)

    if axis == 'x':
        if new_lim[0] < default_xlim[0]:
            width = new_lim[1] - new_lim[0]
            new_lim = (default_xlim[0], min(new_lim[0] + width, default_xlim[1]))
        elif new_lim[1] > default_xlim[1]:
            width = new_lim[1] - new_lim[0]
            new_lim = (max(new_lim[1] - width, default_xlim[0]), default_xlim[1])

        ax.set_xlim(new_lim)
        update_x_scrollbar(new_lim)
        # update_y_scrollbar(xlim=new_lim)
        """
        need to compare against plot area (xlim of trace) once trace is loaded
        """
    else:
        ax.set_ylim(new_lim)
        # update_y_scrollbar(ylim=new_lim)
    canvas.draw()

    """
    need to link this to the scrollbar once a trace is opened
    """

################## Navigation by Scrollbar ###################

def update_x_scrollbar(xlim=None):
    if xlim is None:
        xlim = ax.get_xlim()
    if abs(xlim[0] - default_xlim[0]) < 0.001 and abs(xlim[1] - default_xlim[1]) < 0.001:
        graph_panel.x_scrollbar.set(50)
        return
    pos = xlim[0] - default_xlim[0]
    percent = pos / (default_xlim[1] - default_xlim[0] - (xlim[1] - xlim[0])) * 100
    graph_panel.x_scrollbar.set(percent)
    return

def update_y_scrollbar(ylim=None, xlim=None):
    if ylim is None:
        ylim = ax.get_ylim()
    if xlim is None:
        xlim = ax.get_xlim()
    try:
        idx = analyzer.search_index(xlim[0], ax.lines[0].get_xdata())
        y = ax.lines[0].get_ydata()[idx]

        percent = (ylim[1] - y)/(ylim[1]-ylim[0])*100
        graph_panel.y_scrollbar.set(percent)
    except:
        pass
#
# def refresh():
#     pause_animation()
#     global bg
#     canvas.restore_region(bg)
#     for l in ax.lines:
#         ax.draw_artist(l)
#     canvas.blit(fig.bbox)
#     canvas.flush_events()
#     canvas.draw()
#     bg = fig.canvas.copy_from_bbox(fig.bbox)
#     # canvas.restore_region(bg)
#
# # canvas.draw()



def clear():
    for t in temp:
        temp[t].remove()
    temp.clear()
    for m in markers.keys():
        try:
            markers[m].remove()
        except:
            pass
    markers.clear()
    for s in sweeps.keys():
        sweeps[s].remove()
    sweeps.clear()
    for l in ax.lines:
        l.remove()
    for c in ax.collections:
        c.remove()
    ax.clear()
    gc.collect()
    canvas.draw()

def clear_markers(key=None):
    for t in temp:
        temp[t].remove()
    temp.clear()
    if key:
        try:
            markers[key].remove()
        except:
            pass
        markers[key] = None
    else:
        for m in markers.keys():
            markers[m].remove()
        markers.clear()
        for c in ax.collections:
            c.remove()
    canvas.draw()

def plot_trace(xs, ys, draw=True, relim=True):
    sweeps['sweep{}'.format(len(sweeps))], = ax.plot(xs, ys,
                                                    linewidth=pymini.widgets['style_trace_line_width'].get(),
                                                    c=pymini.widgets['style_trace_line_color'].get(),
                                                     animated=False)
    if relim:
        ax.autoscale(enable=True, axis='both', tight=True)
        ax.relim()
        canvas.draw()
        global default_xlim
        default_xlim = ax.get_xlim()

        global default_ylim
        default_ylim = ax.get_ylim()
    if draw:
        canvas.draw()
        # refresh()

def plot_highlight(xs, ys):
    try:
        markers['highlight'].remove()
    except:
        pass
    try:
        markers['highlight'] = ax.scatter(xs, ys, marker='o', c=pymini.widgets['style_event_color_highlight'].get(),
                                          alpha=0.5, animated=False)
        # canvas.draw()
    except:
        pass

def plot_peak(xs, ys):
    global markers
    try:
        markers['peak'].remove()
    except:
        pass
    try:
        markers['peak']=ax.scatter(xs, ys, marker='o', c=pymini.widgets['style_event_color_peak'].get(), picker=True,
                                   pickradius=int(pymini.widgets['style_event_pick_offset'].get()), animated=False)
        # canvas.draw()
    except Exception as e:
        print(e)
        pass

def plot_start(xs, ys):
    global markers
    try:
        markers['start'].remove()
    except:
        pass
    try:
        markers['start'] = ax.scatter(xs, ys, marker='x', c=pymini.widgets['style_event_color_start'].get(),
                                      animated=False)
        # canvas.draw()
    except:
        pass

def plot_decay(xs, ys):
    global markers
    try:
        markers['decay'].remove()
    except:
        pass
    try:
        markers['decay'] = ax.scatter(xs, ys, marker='x', c=pymini.widgets['style_event_color_decay'].get(),
                                      animated=False)
        # canvas.draw()
    except:
        pass

def plot_end(xs, ys):
    global markers
    try:
        markers['end'].remove()
    except:
        pass
    try:
        markers['end'] = ax.scatter(xs, ys, marker='x', c=pymini.widgets['style_event_color_end'].get(),
                                    animated=False)
        # canvas.draw()
    except:
        pass

def apply_styles(keys):
    styles = ['style_trace_line_width', 'style_trace_line_color', 'style_event_color_peak', 'style_event_color_start',
     'style_event_color_end', 'style_event_color_decay', 'style_event_color_highlight', 'style_trace_highlight_color']
    for k in keys:
        try:
            if k == 'style_trace_line_width':
                for l in ax.lines:
                    l.set_linewidth(float(pymini.widgets[k].get()))
            if k == 'style_trace_line_color':
                for l in ax.lines:
                    l.set_color(pymini.widgets[k].get())
            if k == 'style_event_color_peak':
                markers['peak'].set_color(pymini.widgets[k].get())
            if k == 'style_event_color_start':
                markers['start'].set_color(pymini.widgets[k].get())
            if k == 'style_event_color_decay':
                markers['decay'].set_color(pymini.widgets[k].get())
            if k == 'style_event_color_highlight':
                markers['highlight'].set_color(pymini.widgets[k].get())
            if k == 'style_event_pick_offset':
                markers['peak'].set_picker(True)
                markers['peak'].set_pickradius(int(pymini.widgets[k].get()))
        except:
            pass
    canvas.draw()

def show_all_plot():
    ax.autoscale(enable=True, axis='both', tight=True)
    ax.relim()
    canvas.draw()

get_axis_limits = lambda axis:getattr(ax, 'get_{}lim'.format(axis))()

def set_axis_limit(axis, lim):
    if axis=='x':
        l = [float(e) if e != 'auto' else default_xlim[i] for i,e in enumerate(lim)]
        if l[0] < default_xlim[0] or l[0] > default_xlim[1]:
            l[0] = default_xlim[0]
        if l[1] < default_xlim[0] or l[1] > default_xlim[1]:
            l[1] = default_xlim[1]
        ax.set_xlim(l)
    if axis=='y':

        l = [float(e) if e != 'auto' else default_ylim[i] for i,e in enumerate(lim)]
        ax.set_ylim(l)
    canvas.draw()


class State():
    def __init__(self):
        self.press = False
        self.release = False
        self.move = False
        self.press_coord = (None, None)
        self.release_coord = (None, None)
    ####


