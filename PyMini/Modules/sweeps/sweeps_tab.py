from PyMini import app
from PyMini.Modules.base_module_control import BaseModuleControl
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from tkinter import ttk
import numpy as np
from PyMini.Backend import analyzer2

# debugging
import time
class ModuleControl(BaseModuleControl):
    def __init__(self, module):
        super(ModuleControl, self).__init__(
            scrollbar=False,
            module=module
        )

        self.sweep_vars = [] # list of Tk.BooleanVars
        self.sweep_labels = [] # list of Tk.Labels
        self.sweep_buttons = [] # list of checkbuttons
        self.sweep_namevars = [] # list of Tk.StringVars
        self.panels = [] # list of frames
        # consider making them as a dict instead (list of dict to contain all info)

        self.highlight_color = 'red'
        self.highlight_width = 1

        self._load_layout()
        self._load_binding()

    def canvas_draw_rect(self, event=None):

        selection = []
        xlim = (app.interpreter.drag_coord_start[0], app.interpreter.drag_coord_end[0])
        ylim = (app.interpreter.drag_coord_start[1], app.interpreter.drag_coord_end[1])
        xlim = (min(xlim), max(xlim))
        ylim = (min(ylim), max(ylim))
        for i, name in enumerate(app.trace_display.sweeps.keys()): # get keys
            if self.sweep_vars[i].get():
                xs = app.trace_display.sweeps[name].get_xdata()
                ys = app.trace_display.sweeps[name].get_ydata()
                if analyzer2.contains_line(xlim, ylim, xs, ys, app.interface.recordings[0].sampling_rate):
                    selection.append(name)
        self.set_highlight(selection, draw=True)

    def canvas_mouse_release(self, event=None):
        if len(app.interface.recordings) == 0:
            return None
        if not app.interpreter.mouse_event.xdata:
            return None
        min_d = np.inf
        pick = None
        # offset = float(app.widgets['style_trace_pick_offset_percent'].get())
        offset = 10 # connect to GUI later
        xlim = app.trace_display.ax.get_xlim()
        radius = abs(xlim[1] - xlim[0]) * offset / 100
        ylim = app.trace_display.ax.get_ylim()
        x2y = (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])
        for i, var in enumerate(self.sweep_vars):
            if var.get():
                line = app.trace_display.sweeps[self.sweep_namevars[i].get()] # consider making this part of module calc
                d, idx, _ = analyzer2.point_line_min_distance((app.interpreter.mouse_event.xdata, app.interpreter.mouse_event.ydata),
                                                              xs=line.get_xdata(), ys=line.get_ydata(),
                                                              sampling_rate=app.interface.recordings[0].sampling_rate, radius=radius,
                                                              xy_ratio=x2y)
                if d and d < min_d:
                    min_d = d
                    pick = i
        if pick is None:
            self.remove_highlight([namevar.get() for namevar in self.sweep_namevars], draw=False)
        else:
            if app.interpreter.multi_select:
                self.set_highlight([self.sweep_namevars[pick].get()], draw=False)
            else:
                self.remove_highlight([namevar.get() for namevar in self.sweep_namevars], draw=False)
                self.set_highlight([self.sweep_namevars[pick].get()], draw=False)
        app.trace_display.draw_ani()

    def reset_sweep_list(self, event=None, sweep_name_suffix='Sweep'):
        # only call when new traces are being opened
        sweep_num = app.interface.recordings[0].sweep_count
        frame = self.list_frame.get_frame() #get the internal frame in list_frame
        for i in range(sweep_num):
            sweepname = f'{sweep_name_suffix}_{i}'
            if i < len(self.sweep_vars):
                self.sweep_namevars[i].set(sweepname)
                self.sweep_vars[i].set(True)
            else:
                f = Tk.Frame(frame)
                f.grid_columnconfigure(0, weight=1)
                f.grid_rowconfigure(0, weight=1)
                f.grid(column=0, row=i, sticky='news')
                namevar = Tk.StringVar(f, value=sweepname)
                label = Tk.Label(f, textvariable=namevar, justify=Tk.LEFT)
                label.grid(column=0, row=i, sticky='news')
                self.sweep_namevars.append(namevar)
                self.sweep_labels.append(label)
                var = Tk.BooleanVar(f, True)
                button = ttk.Checkbutton(master=f,
                                         variable=var,
                                         command=lambda x=sweepname, v=var.get:
                                         self.toggle_sweep(x, v()))
                self.sweep_buttons.append(button)
                button.grid(column=1, row=i, sticky='es')
                self.sweep_vars.append(var)
                self.panels.append(f)
        j = len(self.sweep_vars)
        while len(self.sweep_vars) > sweep_num:
            temp = self.panels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_buttons.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_labels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_namevars.pop()
            del temp

            temp = self.sweep_vars.pop()
            del temp
    def synch_sweep_list(self, event=None):
        # only call when new traces are being opened
        frame = self.list_frame.get_frame()  # get the internal frame in list_frame
        for i, sweepname in enumerate(app.trace_display.sweeps.keys()):
            if i < len(self.sweep_vars):
                self.sweep_namevars[i].set(sweepname)
                self.sweep_vars[i].set(app.trace_display.sweeps[sweepname].get_linestyle() == '-')
            else:
                f = Tk.Frame(frame)
                f.grid_columnconfigure(0, weight=1)
                f.grid_rowconfigure(0, weight=1)
                f.grid(column=0, row=i, sticky='news')
                namevar = Tk.StringVar(f, value=sweepname)
                label = Tk.Label(f, textvariable=namevar, justify=Tk.LEFT)
                label.grid(column=0, row=i, sticky='news')
                self.sweep_namevars.append(namevar)
                self.sweep_labels.append(label)
                visible =app.trace_display.sweeps[sweepname].get_linestyle() == '-'
                var = Tk.BooleanVar(f, visible)
                button = ttk.Checkbutton(master=f,
                                         variable=var,
                                         command=lambda x=sweepname, v=var.get:
                                         self.toggle_sweep(x, v()))
                self.sweep_buttons.append(button)
                button.grid(column=1, row=i, sticky='es')
                self.sweep_vars.append(var)
                self.panels.append(f)
        while len(self.sweep_vars) > len(app.trace_display.sweeps):
            temp = self.panels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_buttons.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_labels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_namevars.pop()
            del temp

            temp = self.sweep_vars.pop()
            del temp

    def apply_sweep_list(self, event=None, draw=True):
        selection = [i for i, v in enumerate(self.sweep_vars) if not v.get()]
        self.hide_list(selection=selection, draw=draw)

    def toggle_sweep(self, name=None, value=None):
        if value:
            try:
                app.trace_display.sweeps[name].set_linestyle('-')
            except:
                pass
        else:
            try:
                app.trace_display.sweeps[name].set_linestyle('None')
                # del sweeps['sweep_{}'.format(idx)]
            except:
                pass
        app.trace_display.draw_ani()
        app.interface.focus()

    ##### control sweep visibility #####
    def show_all(self, event=None, draw=True, undo=True):
        print('show all called')
        if undo and app.interface.is_accepting_undo():
            hide_list = [i for i, v in enumerate(self.sweep_vars) if not v.get()]
            app.interface.add_undo(
                [
                    lambda l=hide_list: self.hide_list(selection=l, draw=True, undo=False)
                ]
            )
        self.show_list(selection=range(len(self.sweep_vars)), undo=False)
        # for v in self.sweep_vars:
        #     v.set(True)
        # for v in self.sweep_namevars:
        #     app.trace_display.sweeps[v.get()].set_linestyle('-')
        # if draw:
        #     app.trace_display.draw_ani()
        app.interface.focus()

    def hide_all(self, event=None, draw=True, undo=True):
        print('hide all called')
        if undo and app.interface.is_accepting_undo():
            show_list = [i for i, v in enumerate(self.sweep_vars) if v.get()]
            app.interface.add_undo(
                [
                    lambda l=show_list: self.show_list(selection=l, draw=True, undo=False)
                ]
            )
        self.hide_list(selection=range(len(self.sweep_vars)), undo=False)
        # for v in self.sweep_vars:
        #     v.set(False)
        # for v in self.sweep_namevars:
        #     app.trace_display.sweeps[v.get()].set_linestyle('None')
        # if draw:
        #     app.trace_display.draw_ani()
        # app.interface.focus()

    def hide_selected(self, event=None, draw=True):
        hide_list = [i for i, v in enumerate(self.sweep_vars) if
                app.trace_display.sweeps[self.sweep_namevars[i].get()].get_color() == self.highlight_color]
        self.hide_list(hide_list, draw=draw)

        # for i, v in enumerate(self.sweep_vars):
        #     sweep = app.trace_display.sweeps[self.sweep_namevars[i].get()]
        #     if sweep.get_color() == self.highlight_color:
        #         v.set(False)
        #         sweep.set_linestyle('None')
        #         sweep.set_color(app.trace_display.trace_color)
        #         sweep.set_linewidth(app.trace_display.trace_width)
        # if draw:
        #     app.trace_display.draw_ani()

    def hide_list(self, event=None, selection=None, draw=True, undo=True):
        if selection is None:
            return None
        if undo and app.interface.is_accepting_undo():
            app.interface.add_undo(
                [
                    lambda l=selection: self.show_list(selection=l, draw=True, undo=False)
                ]
            )
        for s in selection:
            self.sweep_vars[s].set(False)
            sweep = app.trace_display.sweeps[self.sweep_namevars[s].get()]
            sweep.set_linestyle('None')
            sweep.set_color(app.trace_display.trace_color)
            sweep.set_linewidth(app.trace_display.trace_width)
        if draw:
            app.trace_display.draw_ani()

    def show_list(self, event=None, selection=None, draw=True, undo=True):
        if selection is None:
            return None
        if undo and app.interface.is_accepting_undo():
            app.interface.add_undo(
                [
                    lambda l=selection: self.hide_list(selection=l, draw=True, undo=False)
                ]
            )
        for s in selection:
            self.sweep_vars[s].set(True)
            sweep = app.trace_display.sweeps[self.sweep_namevars[s].get()]
            sweep.set_linestyle('-')
            sweep.set_color(app.trace_display.trace_color)
            sweep.set_linewidth(app.trace_display.trace_width)
        if draw:
            app.trace_display.draw_ani()


    ##### control sweep highlight #####
    def set_highlight(self, selection:list, draw=True):
        for name in selection:
            app.trace_display.sweeps[name].set_color(self.highlight_color)
            app.trace_display.sweeps[name].set_linewidth(float(self.highlight_width))
        if draw:
            app.trace_display.draw_ani()

    def remove_highlight(self, selection:list, draw=True):
        for name in selection:
            app.trace_display.sweeps[name].set_color(app.trace_display.trace_color)
            app.trace_display.sweeps[name].set_linewidth(float(app.trace_display.trace_width))
        if draw:
            app.trace_display.draw_ani()

    def clear_higlight(self, event=None, draw=True):
        for namevar in self.sweep_namevars:
            app.trace_display.sweeps[namevar.get()].set_color(app.trace_display.trace_color)
            app.trace_display.sweeps[namevar.get()].set_linewidth(app.trace_display.trace_width)
        if draw:
            app.trace_display.draw_ani()

    def highlight_all(self, event=None, draw=True):
        for namevar in self.sweep_namevars:
            app.trace_display.sweeps[namevar.get()].set_color(self.highlight_color)
            app.trace_display.sweeps[namevar.get()].set_linewidth(self.highlight_width)
        if draw:
            app.trace_display.draw_ani()

    #### retrive info
    def get_visible_sweeps(self, event=None):
        return [i for i, v in enumerate(self.sweep_vars) if v.get()]

    def get_highlighted_sweeps(self, event=None):
        return [i for i, v in enumerate(self.sweep_namevars) if
                app.trace_display.sweeps[v.get()].get_color() == self.highlight_color]

    def _load_layout(self):
        self.insert_title(
            text='Sweep Selector'
        )

        self.insert_button(
            text='Hide All',
            command=self.hide_all
        )
        self.insert_button(
            text='Show All',
            command=self.show_all
        )
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=100)
        self.list_frame = ScrollableOptionFrame(self)  # , scrollbar=True)
        self.list_frame.grid(sticky='news')
        self.insert_panel(self.list_frame, separator=False)

    def _load_binding(self):
        app.root.bind('<<OpenedRecording>>',
                      self.reset_sweep_list, add='+')
        app.root.bind('<<LoadCompleted>>', self.module.update_module_display, add='+')
        app.root.bind('<<OverlayView>>', self.module._enable, add='+')
        app.root.bind('<<Plotted>>', lambda e, func=self.apply_sweep_list:self.call_if_enabled(func), add='+')
        app.root.bind('<<ContinuousView>>', self.module._disable, add='+')

        app.root.bind("<<CanvasMouseRelease>>", lambda e, func=self.canvas_mouse_release: self.call_if_focus(func), add="+")
        app.root.bind("<<CanvasDrawRect>>", lambda e, func=self.canvas_draw_rect: self.call_if_focus(func), add='+')
        for key in app.config.key_deselect:
            app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=self.clear_higlight: self.call_if_focus(func), add='+')
        for key in app.config.key_select_all:
            app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=self.highlight_all: self.call_if_focus(func), add='+')
        for key in app.config.key_delete:
            app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=self.hide_selected: self.call_if_focus(func), add='+')