import tkinter as Tk
from config import config

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import trace
import matplotlib.colors
import pymini

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


    def scroll(self, axis, dir = 1):
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
        self.canvas.draw()

        """
        need to link this to the scrollbar once the trace is opened
        """

    def zoom(self, axis, dir = 1, event=None):
        """

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

        if pymini.cp.style_tab.get_value('apply_axis_limit') != "1":
            self.ax.autoscale(enable=True, axis='x', tight=True)
            self.ax.autoscale(enable=True, axis='y')
        else:
            self.ax.autoscale(enable=False, axis='x')
            self.ax.autoscale(enable=False, axis='y')

        self.plot(self.trace)


    def plot(self, trace):
        xs = trace.get_xs()
        ys = trace.get_ys()
        line, = self.ax.plot(
            xs,
            ys,
            linewidth = pymini.cp.style_tab.get_value('line_width'),
            c=pymini.cp.style_tab.get_value('line_color')
        )
        if pymini.cp.style_tab.get_value('apply_axis_limit') == '1':
            self.ax.set_xlim(
                (
                    float(pymini.cp.style_tab.get_value('min_x')),
                    float(pymini.cp.style_tab.get_value('max_x'))
                )
            )
            self.ax.set_ylim(
                (
                    float(pymini.cp.style_tab.get_value('min_y')),
                    flaot(pymini.cp.style_tab.get_value('max_y'))
                )
            )
        self._draw()

    def _clear(self):
        # for l in self.ax.lines:
        #     l.remove()
        # print(self.ax.lines)
        for l in self.ax.lines:
            self.ax.lines.remove(l)
        print(self.ax.lines)
        for c in self.ax.collections:
            self.ax.collections.remove(i)
        self.ax.clear()
        self._draw()

    def _draw(self):
        self.canvas.draw()


        pass



