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

import tkinter as Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
from simplyfire import app
import gc

import simplyfire.backend.analyzer2 as analyzer
from simplyfire.backend import interface
from simplyfire.layout import graph_panel


temp = []
markers = {}
sweeps = {}

event_pick = False

highlighted_sweep = []

rect = None

def load(parent):
    frame = Tk.Frame(parent)
    global fig
    fig = Figure()
    fig.set_tight_layout(True)

    global focus_in_edge_color
    focus_in_edge_color = '#90EE90'

    global focus_out_edge_color
    focus_out_edge_color = '#FFB6C1'

    fig.set_edgecolor(focus_in_edge_color)
    fig.set_linewidth(1)


    global ax
    ax = fig.add_subplot(111)
    fig.subplots_adjust(right=1, top=1)

    global canvas
    canvas = FigureCanvasTkAgg(fig, master=parent)
    # canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    canvas.get_tk_widget().grid(column=1, row=1,sticky='news')
    def focus_in(event=None):
        fig.set_edgecolor(focus_in_edge_color)
        draw_ani()
    def focus_out(event=None):
        fig.set_edgecolor(focus_out_edge_color)
        draw_ani()
    canvas.get_tk_widget().bind('<FocusIn>', focus_in)
    canvas.get_tk_widget().bind('<FocusOut>', focus_out)
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
    global trace_color
    trace_color = 'Black'
    global trace_width
    trace_width = 1
    global transparent_background
    transparent_background = True
    # connect user events:
    # canvas.mpl_connect('pick_event', _on_event_pick)
    canvas.mpl_connect('button_press_event', _on_mouse_press)
    canvas.mpl_connect('motion_notify_event', _on_mouse_move)
    # canvas.mpl_connect('button_release_event', _on_mouse_release)

    draw_ani()
    # canvas.draw()
    # refresh()
    return frame


def _on_mouse_press(event):
    # canvas.get_tk_widget().focus_set()
    interface.focus()
    if canvas.toolbar.mode == "" and event.button == 3:
        state.press_coord = (event.x, event.y)
    # print('click! {}'.format(event))
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
    for c in ax.collections:
        ax.draw_artist(c)
        c.set_animated(True)


def pause_animation():
    for l in ax.lines:
        ax.draw_artist(l)
        l.set_animated(False)
    for c in ax.collections:
        ax.draw_artist(c)
        c.set_animated(False)


def scroll_x_by(dir=1, percent=0):
    dir = dir
    xlim = ax.get_xlim()
    width = xlim[1] - xlim[0]
    delta = width * percent / 100
    new_lim = (xlim[0] + delta * dir, xlim[1] + delta * dir)

    if new_lim[0] < default_xlim[0]:
        delta = default_xlim[0] - new_lim[0]
        new_lim = (new_lim[0] + delta, new_lim[1] + delta)
    elif new_lim[1] > default_xlim[1]:
        delta = new_lim[1] - default_xlim[1]
        new_lim = (new_lim[0] - delta, new_lim[1] - delta)
    ax.set_xlim(new_lim)

    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval=int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()
    update_x_scrollbar(new_lim)
    scroll_y_by(0)


def scroll_y_by(dir=1, percent=0):
    dir = dir
    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]
    delta = height * percent / 100
    new_lim = (ylim[0] + delta * dir, ylim[1] + delta * dir)
    # update_x_scrollbar()
    # update_y_scrollbar(ylim=new_lim)
    ax.set_ylim(new_lim)
    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval=int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()
    update_y_scrollbar(new_lim)


def scroll_x_to(num):
    # start_animation()
    xlim = ax.get_xlim()
    if xlim[1] == default_xlim[1] and xlim[0] == default_xlim[0]:
        graph_panel.x_scrollbar.set(50)
        return None
    start = (default_xlim[1] - default_xlim[0] - (xlim[1] - xlim[0])) * float(num) / 100 + default_xlim[0]
    end = start + xlim[1] - xlim[0]

    ax.set_xlim((start, end))
    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval=int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()
    scroll_y_by(0)


def scroll_y_to(num):
    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]
    xlim = ax.get_xlim()
    ys = sweeps[list(sweeps.keys())[0]].get_ydata()
    y = ys[analyzer.search_index(xlim[0], sweeps[list(sweeps.keys())[0]].get_xdata())]
    y1 = float(num) / 100 * (height) + y
    ax.set_ylim((y1 - height, y1))
    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval=int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()


def center_plot_on(x, y):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    new_xlim = xlim
    new_ylim = ylim


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
    # canvas.draw()
    draw_ani()

def center_plot_area(x1, x2, y1, y2):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    pad = 0.05
    if xlim[1] == default_xlim[1] and xlim[0] == default_xlim[0]:  # currently showing max xlim
        new_xlim_left = xlim[0]
        new_xlim_right = xlim[1]
    elif x1 > xlim[0] + pad and x2 < xlim[1] - pad:  # x1 and x2 are within current xlim
        new_xlim_left = xlim[0]
        new_xlim_right = xlim[1]
    elif x2 - x1 < xlim[1] - xlim[0]:  # current x-axis zoom will x1 and x2 if shifted
        delta = ((xlim[1] + xlim[0]) / 2) - ((x2 + x1) / 2)
        new_xlim_left = max(xlim[0] - delta, default_xlim[0])
        new_xlim_right = min(xlim[1] - delta, default_xlim[1])
    else:
        padx = (x2 - x1) * pad
        new_xlim_left = max(min(xlim[0], x1 - padx), default_xlim[0])
        new_xlim_right = min(max(xlim[1], x2 + padx), default_xlim[1])

    pady = (y2 - y1) * pad

    new_ylim_bottom = min(ylim[0], y1 - pady)
    new_ylim_top = max(ylim[1], y2 + pady)

    ax.set_xlim(new_xlim_left, new_xlim_right)
    update_x_scrollbar((new_xlim_left, new_xlim_right))
    ax.set_ylim(new_ylim_bottom, new_ylim_top)
    update_y_scrollbar(xlim=(new_xlim_left, new_xlim_right), ylim=(new_ylim_bottom, new_ylim_top))

    # canvas.draw()
    draw_ani()

def zoom_x_by(direction=1, percent=0, event=None):
    # direction 1 = zoom in, -1=zoom out
    xlim = ax.get_xlim()
    # delta = (win_lim[1] - win_lim[0]) * percent * dir / 100
    # center_pos = 0.5
    # try:
    #     center_pos = (event.xdata - win_lim[0]) / (win_lim[1] - win_lim[0])
    # except:
    #     pass
    # new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)
    # print(center_pos)

    width = xlim[1] - xlim[0]
    new_width = width + width * direction * percent/100

    center_ratio = 0.5
    try:
        center_ratio = (event.xdata - xlim[0])/width
    except:
        pass
    center_x = center_ratio * width + xlim[0]
    new_lim = (center_x - new_width*center_ratio, center_x + new_width*(1-center_ratio))

    if new_lim[0] < default_xlim[0]:
        width = new_lim[1] - new_lim[0]
        new_lim = (default_xlim[0], min(new_lim[0] + width, default_xlim[1]))
    elif new_lim[1] > default_xlim[1]:
        width = new_lim[1] - new_lim[0]
        new_lim = (max(new_lim[1] - width, default_xlim[0]), default_xlim[1])

    ax.set_xlim(new_lim)
    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval = int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()
    update_x_scrollbar(new_lim)
    scroll_y_by(0)

def anim_func(idx):
    return None

def zoom_y_by(direction=1, percent=0, event=None):
    win_lim = ax.get_ylim()
    delta = (win_lim[1] - win_lim[0]) * percent * direction / 100
    center_pos = 0.5
    try:
        center_pos = (event.ydata - win_lim[0]) / (win_lim[1] - win_lim[0])
    except:
        pass
    new_lim = (win_lim[0] + center_pos * delta, win_lim[1] - (1- center_pos) * delta)
    ax.set_ylim(new_lim)
    global fig
    global ani
    # ani = FuncAnimation(
    #     fig,
    #     anim_func,
    #     frames=1,
    #     interval=int(1),
    #     repeat=False
    # )
    draw_ani()
    # ani._start()
    update_y_scrollbar(new_lim)


# def zoom_by(axis, dir=1, percent=0, event=None):
#     """
#     zooms in/out of the axes by percentage specified in config
#     :param axis: 'x' for x-axis, 'y' for y-axis. currently does not support both
#     :param dir: 1 to zoom in , -1 to zoom out
#     :param event:
#     :return:
#     """
#     if axis == 'x':
#         win_lim = ax.get_xlim()
#     elif axis == 'y':
#         win_lim = ax.get_ylim()
#     else:
#         return None
#
#     delta = (win_lim[1] - win_lim[0]) * percent * dir / 100
#     center_pos = 0.5
#     try:
#         if axis == 'x':
#             center_pos = (event.xdata - win_lim[0]) / (win_lim[1] - win_lim[0])
#         elif axis == 'y':
#             center_pos = (event.ydata - win_lim[0]) / (win_lim[1] - win_lim[0])
#     except:
#         center_pos = 0.5
#
#     new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)
#
#     if axis == 'x':
#         if new_lim[0] < default_xlim[0]:
#             width = new_lim[1] - new_lim[0]
#             new_lim = (default_xlim[0], min(new_lim[0] + width, default_xlim[1]))
#         elif new_lim[1] > default_xlim[1]:
#             width = new_lim[1] - new_lim[0]
#             new_lim = (max(new_lim[1] - width, default_xlim[0]), default_xlim[1])
#
#         ax.set_xlim(new_lim)
#         update_x_scrollbar(new_lim)
#         # update_y_scrollbar(xlim=new_lim)
#         """
#         need to compare against plot area (xlim of trace) once trace is loaded
#         """
#     else:
#         ax.set_ylim(new_lim)
#         # update_y_scrollbar(ylim=new_lim)
#     canvas.draw()
#
#     """
#     need to link this to the scrollbar once a trace is opened
#     """


################## Navigation by Scrollbar ###################

def update_x_scrollbar(xlim=None):
    if xlim is None:
        xlim = ax.get_xlim()
    if abs(xlim[0] - default_xlim[0]) < 0.001 and abs(xlim[1] - default_xlim[1]) < 0.001:
        graph_panel.x_scrollbar.set(50)
        return
    if (default_xlim[1] - default_xlim[0]) - (xlim[1] - xlim[0]) < 0.001:
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
        idx = analyzer.search_index(xlim[0],sweeps[list(sweeps.keys())[0]].get_xdata())
        y = sweeps[list(sweeps.keys())[0]].get_ydata()[idx]

        percent = (ylim[1] - y) / (ylim[1] - ylim[0]) * 100
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
        try:
            sweeps[s].remove()
        except:
            pass
    sweeps.clear()
    gc.collect()
    # canvas.draw()
    draw_ani()

def refresh():
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
        try:
            sweeps[s].remove()
        except:
            pass
    sweeps.clear()
    for l in ax.lines:
        l.remove()
    for c in ax.collections:
        c.remove()
    ax.clear()
    gc.collect()
    # canvas.draw()
    draw_ani()


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
            try:
                markers[m].remove()
            except:
                pass
        markers.clear()
        for c in ax.collections:
            c.remove()
    # canvas.draw()

    draw_ani()

def plot_trace(xs, ys, draw=True, relim=True, idx=0, color=None, width=None, name="", relim_axis='both'):
    global sweeps
    global trace_color
    global trace_width
    if not width:
        width=trace_width
    if name == "":
        name = f'Sweep_{len(sweeps)}'
    if sweeps.get(name, None):
        sweeps.get(name).set_xdata(xs)
        sweeps.get(name).set_ydata(ys)
    else:
        if not color:
            # color = app.widgets['style_trace_line_color'].get()
            color = trace_color
        sweeps[name], = ax.plot(xs, ys,
                                              linewidth=width,
                                              c=color,
                                              animated=False)  # pickradius=int(app.widgets['style_event_pick_offset'].get())
    if relim:
        ax.autoscale(enable=False, axis='both')
        ax.autoscale(enable=True, axis=relim_axis, tight=True)
        ax.relim(visible_only=True)
        # canvas.draw()
        draw_ani()
        if relim_axis == 'x' or relim_axis == 'both':
            global default_xlim
            default_xlim = ax.get_xlim()
        if relim_axis == 'y' or relim_axis =='both':
            global default_ylim
            default_ylim = ax.get_ylim()


    if draw:
        # canvas.draw()
        # refresh()
        draw_ani()

def hide_sweep(idx, draw=False):
    try:
        sweeps['sweep_{}'.format(idx)].set_linestyle('None')
        # del sweeps['sweep_{}'.format(idx)]
    except:
        pass
    if draw:
        # canvas.draw()
        draw_ani()

def show_sweep(idx, draw=False):
    sweeps['sweep_{}'.format(idx)].set_linestyle('-')
    try:
        pass
    except:
        pass
    if draw:
        # canvas.draw()
        draw_ani()
def delete_last_sweep(draw=False):
    sweeps['sweep_{}'.format(len(sweeps) - 1)].remove()
    # print('length of ax lines after removing sweep: {}'.format(len(ax.lines)))
    # ax lines are removed - memory leak not because of the axis retaining object
    del sweeps['sweep_{}'.format(len(sweeps) - 1)]



def get_sweep(idx):
    try:
        return sweeps['sweep_{}'.format(idx)]
    except:
        return None


def toggle_sweep_highlight(idx, exclusive=True, draw=False):
    global highlighted_sweep
    c = app.inputs['style_trace_line_color'].get()
    w = float(app.inputs['style_trace_line_width'].get())
    if exclusive:
        for l in sweeps:
            sweeps[l].set_color(c)
            sweeps[l].set_linewidth(w)
        if idx in highlighted_sweep and len(highlighted_sweep) == 1:
            highlighted_sweep = []
            if draw:
                # canvas.draw()
                draw_ani()
                return None
        highlighted_sweep = []
    if idx in highlighted_sweep:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(c)
            sweeps[f'sweep_{idx}'].set_linewidth(w)
            highlighted_sweep.remove(idx)
        except:
            pass
    else:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(app.inputs['style_trace_highlight_color'].get())
            sweeps[f'sweep_{idx}'].set_linewidth(float(app.inputs['style_trace_highlight_width'].get()))
            highlighted_sweep.append(idx)
        except:
            pass
    if draw:
        # canvas.draw()
        draw_ani()
def remove_highlight_sweep(draw=True):
    global highlighted_sweep
    for idx in highlighted_sweep:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(app.inputs['style_trace_line_color'].ge())
            sweeps[f'sweep_{idx}'].set_linewidth(float(app.inputs['style_trace_line_width'].get()))
            highlighted_sweep.remove(idx)
        except:
            pass
    highlighted_sweep = []
    if draw:
        # canvas.draw()
        draw_ani()
def set_highlight_sweep(idx, highlight=True, draw=True):
    if idx not in highlighted_sweep and highlight:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(app.inputs['style_trace_highlight_color'].get())
            sweeps[f'sweep_{idx}'].set_linewidth(float(app.inputs['style_trace_highlight_width'].get()))
            highlighted_sweep.append(idx)
        except:
            pass
    elif not highlight and idx in highlighted_sweep:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(app.inputs['style_trace_line_color'].get())
            sweeps[f'sweep_{idx}'].set_linewidth(float(app.inputs['style_trace_line_width'].get()))
            highlighted_sweep.remove(idx)
        except:
            pass
    if draw:
        # canvas.draw()
        draw_ani()

def plot_highlight(xs, ys):
    try:
        markers['highlight'].remove()
    except:
        pass
    try:
        markers['highlight'], = ax.plot(xs, ys, marker='o', c=app.inputs['style_event_highlight_color'].get(),
                                        markersize=app.inputs['style_event_highlight_size'].get(),
                                        linestyle='None',
                                        alpha=0.5, animated=False)
        # canvas.draw()
    except:
        pass


def plot_peak(xs, ys):
    global markers
    try:
        markers['peak'].remove()
    except Exception as e:
        pass
    try:
        markers['peak'] = ax.scatter(xs, ys, marker='o', c=app.inputs['style_event_peak_color'].get(), picker=True,
                                     s=float(app.inputs['style_event_peak_size'].get()) ** 2,
                                     pickradius=float(app.inputs['style_event_pick_offset'].get()), animated=False)
        # canvas.draw()
    except:
        pass


def plot_start(xs, ys):
    global markers
    try:
        markers['start'].remove()
    except:
        pass
    try:
        markers['start'], = ax.plot(xs, ys, marker='x', c=app.inputs['style_event_start_color'].get(),
                                    markersize=app.inputs['style_event_start_size'].get(),
                                    linestyle='None',
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
        markers['decay'], = ax.plot(xs, ys, marker='x', c=app.inputs['style_event_decay_color'].get(),
                                    markersize=app.inputs['style_event_decay_size'].get(),
                                    linestyle='None',
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
        markers['end'], = ax.plot(xs, ys, marker='x', c=app.inputs['style_event_color_end'].get(),
                                  animated=False)
        # canvas.draw()
    except:
        pass


def apply_styles(keys, draw=True):
    global highlighted_sweep
    for k in keys:
        try:
            if k == 'style_trace_line_width':
                for l in ax.lines:
                    l.set_linewidth(float(app.inputs[k].get()))
            if k == 'style_trace_line_color':
                if not app.inputs['trace_mode'].get() == 'compare':
                    for l in ax.lines:
                        l.set_color(app.inputs[k].get())
            if k == 'compare_color_list':
                idx_offset = 0
                for i,r in enumerate(interface.recordings):
                    for j in range(r.sweep_count):
                        sweeps[f'sweep_{j+idx_offset}'].set_color(app.compare_tab.get_color(i))
                    idx_offset += r.sweep_count
            if k == 'style_event_peak_color':
                markers['peak'].set_color(app.inputs[k].get())
            if k == 'style_event_peak_size':
                markers['peak'].set_sizes([float(app.inputs[k].get()) ** 2])
            if k == 'style_event_start_color':
                markers['start'].set_color(app.inputs[k].get())
            if k == 'style_event_start_size':
                markers['start'].set_markersize(app.inputs[k].get())
            if k == 'style_event_decay_color':
                markers['decay'].set_color(app.inputs[k].get())
            if k == 'style_event_decay_size':
                markers['decay'].set_markersize(app.inputs[k].get())
            if k == 'style_event_highlight_color':
                markers['highlight'].set_color(app.inputs[k].get())
            if k == 'style_event_highlight_size':
                markers['highlight'].set_markersize(app.inputs[k].get())
            if k == 'style_trace_highlight_width':
                for idx in highlighted_sweep:
                    sweeps[f'sweep_{idx}'].set_linewidth(float(app.inputs[k].get()))
            if k == 'style_trace_highlight_color':
                for idx in highlighted_sweep:
                    sweeps[f'sweep_{idx}'].set_color(app.inputs[k].get())
            if k == 'style_event_pick_offset':
                markers['peak'].set_picker(float(app.inputs[k].get()))
        except:
            pass
    if draw:
        # canvas.draw()
        draw_ani()


def show_all_plot(update_default=False):
    ax.autoscale(enable=True, axis='both', tight=True)
    ax.relim(visible_only=True)
    # canvas.draw()
    draw_ani()
    if update_default:
        global default_xlim
        default_xlim = ax.get_xlim()
        global default_ylim
        default_ylim = ax.get_ylim()

def update_default_lim(x=True, y=True):
    ax.autoscale(enable=True, axis='both', tight=True)
    ax.relim(visible_only=True)
    draw_ani()
    if x:
        global default_xlim
        default_xlim = ax.get_xlim()
    if y:
        global default_ylim
        default_ylim = ax.get_ylim()




get_axis_limits = lambda axis: getattr(ax, 'get_{}lim'.format(axis))()

def adjust_default_ylim(adjust):
    global default_ylim
    default_ylim = (default_ylim[0]+adjust,
                    default_ylim[1]+adjust)

def set_axis_limit(axis, lim):
    if axis == 'x':
        l = [float(e) if e != 'auto' else default_xlim[i] for i, e in enumerate(lim)]
        if l[0] < default_xlim[0] or l[0] > default_xlim[1]:
            l[0] = default_xlim[0]
        if l[1] < default_xlim[0] or l[1] > default_xlim[1]:
            l[1] = default_xlim[1]
        ax.set_xlim(l)
    if axis == 'y':
        l = [float(e) if e != 'auto' else default_ylim[i] for i, e in enumerate(lim)]
        ax.set_ylim(l)
    # canvas.draw()
    draw_ani()

class State():
    def __init__(self):
        self.press = False
        self.release = False
        self.move = False
        self.press_coord = (None, None)
        self.release_coord = (None, None)
    ####


##################
def draw_rect(coord_start, coord_end):
    global rect
    if coord_start and coord_end:
        height = coord_end[1] - coord_start[1]
        width = coord_end[0] - coord_start[0]
        if rect:
            rect.set_width(width)
            rect.set_height(height)
        else:
            rect = Rectangle(coord_start, width, height, angle=0.0,
                      edgecolor='blue',
                      facecolor='gray',
                      fill=True,
                      alpha=0.2,
                      animated=True)
            ax.add_patch(rect)
        canvas.draw()
        # draw_ani()
        global bg
        bg = canvas.copy_from_bbox(fig.bbox)
        ax.draw_artist(rect)
        canvas.blit(fig.bbox)
        return
    if rect:
        ax.patches.remove(rect)
        rect = None
        # canvas.draw()
        draw_ani()
def draw_ani():
    global ani
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()