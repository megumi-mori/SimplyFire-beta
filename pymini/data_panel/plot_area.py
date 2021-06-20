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
        # self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure(0 ,weight=1) #I guess this doesn't matter?

        self.fig = Figure()
        self.fig.set_tight_layout(True)

        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(right=1, top=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.ax.plot()

        self.labels = {'x': 'Time (n/a)',
                      'y': 'y (n/a)'}
        self.ax.set_xlabel(self.labels['x'])
        self.ax.set_ylabel(self.labels['y'])
        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()



    def scroll(self, axis, dir=1, percent=0):
        if axis == "x":
            win_lim = self.ax.get_xlim()
        elif axis == "y":
            win_lim = self.ax.get_ylim()

        else:
            return None
        width = win_lim[1] - win_lim[0]
        delta = width * percent / 100
        new_lim = (win_lim[0] + delta * dir, win_lim[1] + delta * dir)

        if axis == "x":
            self.ax.set_xlim(new_lim)
        else:
            self.ax.set_ylim(new_lim)
        self.draw()

        """
        need to link this to the scrollbar once the trace is opened
        """

    def zoom(self, axis, dir=1, percent=0):
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
        if pymini.get_value('force_channel') == '1':
            try:
                self.trace.set_channel(
                    int(pymini.get_value('force_channel_id')) - 1 #1indexing
                )
            except:
                pass
        self._clear()

        pymini.change_label(
            'trace_info',
            '{} : {}Hz : {} channel{}'.format(
                self.trace.fname,
                self.trace.sampling_rate,
                self.trace.channel_count,
                's' if self.trace.channel_count > 1 else ""
            ),
            tab='graph_panel'
        )

        xlim = None
        ylim = None

        self.plot(self.trace, xlim, ylim)

        if pymini.get_value('apply_axis_limit') == "1":
            self.set_axis_limits(
                {
                    'x': (
                        pymini.get_value('min_x'),
                        pymini.get_value('max_x')
                    ),
                    'y': (
                        pymini.get_value('min_y'),
                        pymini.get_value('max_y')
                    )

                }
            )
        pymini.get_widget('channel_option').clear_options()
        for i in range(self.trace.channel_count):
            pymini.get_widget('channel_option').add_option(
                label = "{}: {}".format(i+1, self.trace.channel_labels[i]),
                command=lambda c=i:self._choose_channel(c)
            )
        pymini.set_value('channel_option', "{}: {}".format(self.trace.channel + 1, self.trace.y_label))
        self.draw()

    def close(self):
        self._clear()
        pymini.get_widget('channel_option').clear_options()
        pymini.set_value('channel_option', '', 'graph_panel')
        pymini.change_label('trace_info', "", 'graph_panel')
        try:
            self.trace.forget()
            self.trace = None
        except:
            pass

        self.draw()

    def _choose_channel(self, num):
        self.trace.set_channel(num)
        pymini.set_value('channel_option', "{}: {}".format(self.trace.channel, self.trace.y_label))

        xlim = self.ax.get_xlim()
        self._clear()


        self.plot(self.trace, xlim)

        pass

    def plot(self, trace, xlim=None, ylim=None):
        """
        plots data from the trace
        will first plot everything with autoscale, and save the limits as defaults.
        To avoid this behavior, make a separate function
        :param trace: Trace object
        :param xlim: desired xlim
        :param ylim: desired ylim
        :return:
        """
        # print('trace channel = {}'.format(trace.channel))
        xs = trace.get_xs()
        ys = trace.get_ys()
        self.ax.set_xlabel(
            trace.x_label
        )
        self.ax.set_ylabel(
            trace.y_label
        )
        self.ax.autoscale(enable=True, axis='x', tight=True)
        self.ax.autoscale(enable=True, axis='y', tight=True)

        self.ax.plot(
            xs,
            ys,
            linewidth=pymini.get_value('line_width'),
            c=pymini.get_value('line_color')
        )
        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()

        try:
            self.ax.set_xlim(xlim)
        except:
            pass
        try:
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

    def set_single_axis_limit(self, axis, idx, value):
        if idx == 0:
            self._set_ax_lim(axis, (value, self.get_axis_limits(axis)[1]))
        elif idx == 1:
            self._set_ax_lim(axis, (self.get_axis_limits(axis)[0], value))

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

    def get_unit(self, axis):
        try:
            return getattr(self.trace, '{}_unit'.format(axis), 'n/a')
        except:
            return 'n/a'

    def show_all_plot(self):
        self.ax.set_xlim(self.default_xlim)
        self.ax.set_ylim(self.default_ylim)
        self.draw()

    def apply_all_style(self):
        # markers should be in collections, not lines, so this shouldn't affect peaks, baselines, etc
        for l in self.ax.lines:
            l.set_color(pymini.get_value('line_color'))
            l.set_linewidth(float(pymini.get_value('line_width')))

        self.draw()

    def apply_style(self, key):
        try:
            if key == 'line_width':
                for l in self.ax.lines:
                    l.set_linewidth(float(pymini.get_value('line_width')))
            elif key == 'line_color':
                for l in self.ax.lines:
                    l.set_color(pymini.get_value('line_color'))
            self.draw()
            return True
        except:
            return False

    def focus(self):
        self.canvas.get_tk_widget().focus_set()







