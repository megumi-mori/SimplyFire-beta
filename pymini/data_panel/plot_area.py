import tkinter as Tk
from config import config
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils import trace, analysis
import matplotlib.colors
import pymini
import os
import gc
import time
import numpy as np


def search_index(x, l, rate):
    print("{} : {}".format(x, l[0]))
    est = int((x - l[0]) * rate)
    if est >= len(l):
        return len(l)  # out of bounds
    elif l[est] == x:
        return est
    elif l[est] > x:  # overshot
        while est >= 0:
            if l[est] < x:
                return est + 1
            est -= 1
    elif l[est] < x:  # need to go higher
        while est < len(l):
            if l[est] > x:
                return est
            est += 1
    return est  # out of bounds

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

        #initialize cid
        self.canvas.mpl_connect('key_press_event', self._on_key)
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)

        self.trace = None # take this off later once the event finding is completed and can be handled in try/except

    ##################################################
    #                 User Interface                 #
    ##################################################

    def _on_key(self, e):
        """
        Keyboard key press event
        :param e:
        :return:
        """
        print(e)

    def _on_mouse_press(self, e):
        self.focus()
        self.press = True
        if self.canvas.toolbar.mode == "":
            # pymini.data_table.add_event({
            #     't':e.xdata
            # })
            pass

    def _on_mouse_release(self, e):
        self.press = False
        if pymini.get_value('trace_mode') == 'continuous' and self.trace is not None: # remove the None case later, when the finder is completed
            try:
                if self.drag:
                    self.drag = False
                    return None
            except:
                pass
            print('click!')
            self._find_event_manual(e.xdata)
    def _on_mouse_move(self, e):
        try:
            if self.press:
                self.drag = True
        except:
            pass

    ##################################################
    #                    Analysis                    #
    ##################################################
    def _find_event_manual(self, x):
        print('find event manual')
        xs = np.array(self.ax.lines[0].get_xdata())
        ys = np.array(self.ax.lines[0].get_ydata())
        x_idx = search_index(x, xs, self.trace.sampling_rate)  # should be the only line on the plot
        if pymini.get_value('detector_direction') == "negative":
            ys = ys * -1 # now can look at either versions with the same algorithm
        # switcher implementation:
        # switch = {
        #     'positive': np.array(self.ax.lines[0].get_ydata())
        #     'negative': np.array(self.ax.lines[0].get_ydata)) * -1
        # }
        # ys = switch.get(pymini.get_value('detector_points_search', None))

        start_idx = x_idx - int(int(pymini.get_value('detector_points_search'))/2)
        end_idx = x_idx + int(int(pymini.get_value('detector_points_search'))/2)
        lag = int(pymini.get_value('detector_points_baseline'))
        max_pt_baseline = int(pymini.get_value('detector_max_points_baseline'))
        data = self._find_event(x_idx, xs, ys, start_idx, end_idx, lag, max_pt_baseline)
        pymini.data_table.add_event(data)




    def _find_event(self, x_idx, xs, ys, start_idx, end_idx, lag, max_pt_baseline):
        print('find event')
        data = {}
        try:
            peak_y = max(ys[start_idx:end_idx])
            peak_idx = np.where(ys[start_idx:end_idx]==peak_y)[0][0] + start_idx #take the earliest time point
        except Exception as e:
            print('find event, find index of max: {}'.format(e)) #erase this if no errors are expected
            return None
        FUDGE = 10 #adjust this if needed

        if peak_idx <= start_idx + FUDGE or peak_idx > end_idx - FUDGE:
            return None # the peak is likely at the very edge - no need to try to expand the search space

        data['t'] = xs[peak_idx] # for the table
        data['peak_coord'] = (xs[peak_idx], ys[peak_idx]) # for the plot

        base_idx = peak_idx - 1
        y_avg = np.mean(ys[base_idx - lag+1:base_idx+1]) # should include the base_idx in the calculation, also, why was it base_idx+2?

        while base_idx > max(start_idx - max_pt_baseline + lag, lag):
            y_avg = (y_avg * (lag) + ys[base_idx - lag] - ys[base_idx])/(lag) # equivalent to np.mean(ys[base_idx - lag: base_idx]))
            if y_avg > ys[base_idx]:
                break
            base_idx -= 1
        else:
            return None #could not find start

        data['start_coord'] = (xs[base_idx], ys[base_idx])

        data['baseline'] = ys[base_idx]
        data['baseline_unit'] = self.trace.y_unit # make sure channel in trace cannot change unexpectedly
        data['t_start'] = xs[base_idx]

        return data


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
        try:
            self.trace = trace.Trace(filename)
        except:
            return None
        #set the default save path for images
        if pymini.get_value('file_autodir'):
            mpl.rcParams['savefig.directory'] = os.path.split(filename)[0]

        if pymini.get_value('force_channel') == '1':
            try:
                self.trace.set_channel(
                    int(pymini.get_value('force_channel_id')) - 1 #1indexing
                )
            except:
                pass
        self._clear()
        gc.collect()

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
        pymini.set_value('channel_option', "{}: {}".format((self.trace.channel+1), self.trace.y_label))

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
        for l in self.ax.lines:
            self.ax.lines.remove(l)
        for c in self.ax.collections:
            self.ax.collections.remove(i)
        self.ax.clear()
        gc.collect()
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







