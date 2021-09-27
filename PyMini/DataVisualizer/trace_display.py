import tkinter as Tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import pymini
import gc

from Backend import interface, analyzer
from Layout import graph_panel

from DataVisualizer import data_display

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
    # canvas.mpl_connect('pick_event', _on_event_pick)
    canvas.mpl_connect('button_press_event', _on_mouse_press)
    canvas.mpl_connect('motion_notify_event', _on_mouse_move)
    # canvas.mpl_connect('button_release_event', _on_mouse_release)

    canvas.draw()
    # refresh()
    return frame


def _on_mouse_press(event):
    canvas.get_tk_widget().focus_set()
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


def pause_animation():
    for l in ax.lines:
        ax.draw_artist(l)
        l.set_animated(False)


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
    update_x_scrollbar(new_lim)

    global fig
    global ani
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()


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
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()


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
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()


def scroll_y_to(num):
    ylim = ax.get_ylim()
    height = ylim[1] - ylim[0]
    xlim = ax.get_xlim()
    ys = ax.lines[0].get_ydata()
    y = ys[analyzer.search_index(xlim[0], ax.lines[0].get_xdata())]
    y1 = float(num) / 100 * (height) + y
    ax.set_ylim((y1 - height, y1))
    global fig
    global ani
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()


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
    canvas.draw()


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

    canvas.draw()


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

    center_pos = 0.5
    try:
        center_pos = (event.xdata - win_lim[0])/width
    except:
        pass
    center_pos = center_pos * width + xlim[0]
    new_lim = (center_pos - new_width/2, center_pos + new_width/2)

    if new_lim[0] < default_xlim[0]:
        width = new_lim[1] - new_lim[0]
        new_lim = (default_xlim[0], min(new_lim[0] + width, default_xlim[1]))
    elif new_lim[1] > default_xlim[1]:
        width = new_lim[1] - new_lim[0]
        new_lim = (max(new_lim[1] - width, default_xlim[0]), default_xlim[1])

    ax.set_xlim(new_lim)
    global fig
    global ani
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval = int(1),
        repeat=False
    )
    ani._start()
    update_x_scrollbar(new_lim)

def anim_func(idx):
    return None

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
    global fig
    global ani
    ani = FuncAnimation(
        fig,
        anim_func,
        frames=1,
        interval=int(1),
        repeat=False
    )
    ani._start()


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
        idx = analyzer.search_index(xlim[0], ax.lines[0].get_xdata())
        y = ax.lines[0].get_ydata()[idx]

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
        try:
            for m in markers.keys():
                markers[m].remove()
            markers.clear()
        except:
            pass
        for c in ax.collections:
            c.remove()
    canvas.draw()


def plot_trace(xs, ys, draw=True, relim=True, idx=0):
    if 'sweep_{}'.format(idx) in sweeps:
        try:
            sweeps['sweep_{}'.format(idx)].remove()
        except:
            pass

    sweeps['sweep_{}'.format(idx)], = ax.plot(xs, ys,
                                              linewidth=pymini.widgets['style_trace_line_width'].get(),
                                              c=pymini.widgets['style_trace_line_color'].get(),
                                              animated=False)  # pickradius=int(pymini.widgets['style_event_pick_offset'].get())
    if relim:
        ax.autoscale(enable=True, axis='both', tight=True)
        ax.relim()
        canvas.draw()
        global default_xlim
        default_xlim = ax.get_xlim()

        global default_ylim
        default_ylim = ax.get_ylim()

        print(default_xlim)

    if draw:
        canvas.draw()
        # refresh()

def hide_sweep(idx, draw=False):
    try:
        sweeps['sweep_{}'.format(idx)].set_linestyle('None')
        # del sweeps['sweep_{}'.format(idx)]
    except Exception as e:
        print(e)
        pass
    if draw:
        canvas.draw()

def show_sweep(idx, draw=False):
    sweeps['sweep_{}'.format(idx)].set_linestyle('-')
    try:
        pass
    except:
        pass
    if draw:
        canvas.draw()

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
    c = pymini.widgets['style_trace_line_color'].get()
    print(highlighted_sweep)
    if exclusive:
        for l in sweeps:
            sweeps[l].set_color(c)
        if idx in highlighted_sweep and len(highlighted_sweep) == 1:
            highlighted_sweep = []
            canvas.draw()
            return None
        highlighted_sweep = []
    if idx in highlighted_sweep:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(c)
            highlighted_sweep.remove(idx)
        except:
            pass
    else:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(pymini.widgets['style_trace_highlight_color'].get())
            highlighted_sweep.append(idx)
        except:
            pass
    if draw:
        canvas.draw()


def set_highlight_sweep(idx, highlight=True, draw=True):
    if idx not in highlighted_sweep and highlight:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(pymini.widgets['style_trace_highlight_color'].get())
            highlighted_sweep.append(idx)
        except:
            pass
    elif not highlight and idx in highlighted_sweep:
        try:
            sweeps['sweep_{}'.format(idx)].set_color(pymini.widgets['style_trace_line_color'].get())
            highlighted_sweep.remove(idx)
        except Exception as e:
            print('remove highlight : {}'.format(e))
            pass
    if draw:
        canvas.draw()


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
    except Exception as e:
        pass
    try:
        markers['peak'] = ax.scatter(xs, ys, marker='o', c=pymini.widgets['style_event_color_peak'].get(), picker=True,
                                     pickradius=int(pymini.widgets['style_event_pick_offset'].get()), animated=False)
        # canvas.draw()
    except Exception as e:
        print('plot peak, plotting error:{}'.format(e))
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
              'style_event_color_end', 'style_event_color_decay', 'style_event_color_highlight',
              'style_trace_highlight_color']
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


def show_all_plot(update_default=False):
    ax.autoscale(enable=True, axis='both', tight=True)
    ax.relim()
    canvas.draw()
    if update_default:
        global default_xlim
        default_xlim = ax.get_xlim()
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
        print('set y lim: {}'.format(l))
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
        global bg
        bg = canvas.copy_from_bbox(fig.bbox)
        ax.draw_artist(rect)
        canvas.blit(fig.bbox)
        return
    if rect:
        ax.patches.remove(rect)
        rect = None
        canvas.draw()