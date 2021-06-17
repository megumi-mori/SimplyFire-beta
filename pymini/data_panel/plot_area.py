import tkinter as Tk
from config import config

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import trace
import matplotlib.colors

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

        self.trace.get_ys()


    def plot(self, trace, maintain_axis=False):
        if maintain_axis:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()




