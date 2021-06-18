import tkinter as Tk
from config import config

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import trace
import matplotlib.colors
import pymini
import time


class InteractivePlot():
    def __init__(self, parent):
        self.frame = Tk.Frame(parent)

        self.fig = Figure()
        self.fig.set_tight_layout(True)

        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(right=1, top=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.ax.plot()
        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()

    def scroll(self, axis, dir=1):
        if axis == "x":
            win_lim = self.ax.get_xlim()
        elif axis == "y":
            win_lim = self.ax.get_ylim()

        else:
            return None
        width = win_lim[1] - win_lim[0]
        delta = width * config.scroll_percent / 100
        new_lim = (win_lim[0] + delta * dir, win_lim[1] + delta * dir)

        if axis == "x":
            self.ax.set_xlim(new_lim)
        else:
            self.ax.set_ylim(new_lim)
        self.draw()

        """
        need to link this to the scrollbar once the trace is opened
        """

    def zoom(self, axis, dir=1, event=None):
        """
        zooms in/out of the axes by percentage specified in config
        :param axis: 'x' for x-axis, 'y' for y-axis. currently does not support both
        :param dir: 1 to zoom in , -1 to zoom out
        :param event:
        :return:
        """
        if axis == 'x':
            win_lim = self.ax.get_xlim()
        elif axis == 'y':
            win_lim = self.ax.get_ylim()
        else:
            return None

        delta = (win_lim[1] - win_lim[0]) * config.zoom_percent * dir / 100
        try:
            if axis == 'x':
                center_pos = (event.xdata - win_lim[0]) / (win_lim[1] - win_lim[0])
            elif axis == 'y':
                center_pos = (event.ydata - win_lim[0]) / (win_lim[1] - win_lim[0])
        except:
            center_pos = 0.5

        new_lim = (win_lim[0] + (1 - center_pos) * delta, win_lim[1] - (center_pos) * delta)

        if axis == 'x':
            self.ax.set_xlim(new_lim)
            """
            need to compare against plot area (xlim of trace) once trace is loaded
            """
        else:
            self.ax.set_ylim(new_lim)
        self.canvas.draw()

        """
        need to link this to the scrollbar once a trace is opened
        """

    def open_trace(self, filename):
        self.trace = trace.Trace(filename)
        self._clear()

        xlim = None
        ylim = None

        self.ax.autoscale(enable=True, axis='x', tight=True)
        self.ax.autoscale(enable=True, axis='y')

        self.plot(self.trace, xlim, ylim)

        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()

        if pymini.cp.style_tab.get_value('apply_axis_limit') == "1":
            self.set_axis_limits(
                {
                    'x': (
                        pymini.cp.style_tab.get_value('min_x'),
                        pymini.cp.style_tab.get_value('max_x')
                    ),
                    'y': (
                        pymini.cp.style_tab.get_value('min_y'),
                        pymini.cp.style_tab.get_value('max_y')
                    )

                }
            )

        self.draw()


    def plot(self, trace, xlim=None, ylim=None):
        xs = trace.get_xs()
        ys = trace.get_ys()
        line, = self.ax.plot(
            xs,
            ys,
            linewidth=pymini.cp.style_tab.get_value('line_width'),
            c=pymini.cp.style_tab.get_value('line_color')
        )
        try:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        except:
            pass
        self.draw()

    def _clear(self):
        # for l in self.ax.lines:
        #     l.remove()
        # print(self.ax.lines)
        for l in self.ax.lines:
            self.ax.lines.remove(l)
        for c in self.ax.collections:
            self.ax.collections.remove(i)
        self.ax.clear()
        self.draw()

    def draw(self):
        self.canvas.draw()

        pass

    # def set_axis(self, axis='x', lim=None):
    #     if axis == 'x':
    #         self.ax.set_xlim(lim)
    #     elif axis == 'y':
    #         self.ax.set_ylim(lim)

    def get_axis_limits(self, axis='x'):

        if axis == 'x':
            return self.ax.get_xlim()
        elif axis == 'y':
            return self.ax.get_ylim()
        return None

    def set_axis_limits(self, axis=None):
        """

        :param axis: dict of axis parameters, shoud be given as:
        {'x': (min_x, max_x),
        'y': (min_y, max_y)}
        min and max values can be float, 'auto', or None
        :return:
        """

        for a in axis:
            self._set_ax_lim(a, axis[a])

    def _set_ax_lim(self, axis=None, lim=None):
        """
        :param axis: 'x' or 'y'
        :param lim: tuple (min, max). can be float, 'auto' or None
        :return:
        """
        if axis == 'x':
            set_lim_func = self.ax.set_xlim
        elif axis == 'y':
            set_lim_func = self.ax.set_ylim
        else:
            return None

        try:
            set_lim_func([float(l) for l in lim])
        except:
            try:
                new_lim = [0] * len(lim)
                for i, l in enumerate(lim):
                    if l == 'auto':
                        new_lim[i] = getattr(self, 'default_{}lim'.format(axis))[i]
                    elif l is None:
                        new_lim[i] = self.get_axis_limits(axis)[i]
                    else:
                        new_lim[i] = float(lim[i])
                set_lim_func(new_lim)
            except:
                return None

        self.draw()

    def show_all_plot(self):
        self.ax.set_xlim(self.default_xlim)
        self.ax.set_ylim(self.default_ylim)
        self.draw()



