from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire import app
from simplyfire.loader import config
from simplyfire.backend import analyzer2
from simplyfire.utils.scrollable_option_frame import ScrollableOptionFrame
import numpy as np
from tkinter import ttk
import tkinter as Tk

#### Variables ####
sweep_vars = []
sweep_labels = []
sweep_buttons = []
sweep_namevars = []
panels = []

highlight_color = 'red'
highlight_width = 1

#### Functions ####
def canvas_draw_rect(event=None):
    selection = []
    xlim = (app.interpreter.drag_coord_start[0], app.interpreter.drag_coord_end[0])
    ylim = (app.interpreter.drag_coord_start[1], app.interpreter.drag_coord_end[1])
    xlim = (min(xlim), max(xlim))
    ylim = (min(ylim), max(ylim))
    for i, name in enumerate(app.trace_display.sweeps.keys()):  # get keys
        if sweep_vars[i].get():
            xs = app.trace_display.sweeps[name].get_xdata()
            ys = app.trace_display.sweeps[name].get_ydata()
            if analyzer2.contains_line(xlim, ylim, xs, ys, app.interface.recordings[0].sampling_rate):
                selection.append(name)
    set_highlight(selection, draw=True)

def canvas_mouse_release(event=None):
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
    for i, var in enumerate(sweep_vars):
        if var.get():
            line = app.trace_display.sweeps[sweep_namevars[i].get()] # consider making this part of module calc
            d, idx, _ = analyzer2.point_line_min_distance(
                (app.interpreter.mouse_event.xdata, app.interpreter.mouse_event.ydata),
                xs=line.get_xdata(), ys=line.get_ydata(),
                sampling_rate=app.interface.recordings[0].sampling_rate, radius=radius,
                xy_ratio=x2y)
            if d and d < min_d:
                min_d = d
                pick = i
    if pick is None:
        remove_highlight([namevar.get() for namevar in sweep_namevars], draw=False)
    else:
        if app.interpreter.multi_select:
            set_highlight([sweep_namevars[pick].get()], draw=False)
        else:
            remove_highlight([namevar.get() for namevar in sweep_namevars], draw=False)
            set_highlight([sweep_namevars[pick].get()], draw=False)
    app.trace_display.draw_ani()

def reset_sweep_list(event=None, sweep_name_suffix='Sweep'):
    # only call when new traces are being opened
    sweep_num = app.interface.recordings[0].sweep_count
    frame = list_frame.get_frame() #get the internal frame in list_frame
    for i in range(sweep_num):
        sweepname = f'{sweep_name_suffix}_{i}'
        if i < len(sweep_vars):
            sweep_namevars[i].set(sweepname)
            sweep_vars[i].set(True)
        else:
            f = Tk.Frame(frame)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(0, weight=1)
            f.grid(column=0, row=i, sticky='news')
            namevar = Tk.StringVar(f, value=sweepname)
            label = Tk.Label(f, textvariable=namevar, justify=Tk.LEFT)
            label.grid(column=0, row=i, sticky='news')
            sweep_namevars.append(namevar)
            sweep_labels.append(label)
            var = Tk.BooleanVar(f, True)
            button = ttk.Checkbutton(master=f,
                                     variable=var,
                                     command=lambda x=sweepname, idx=i, v=var.get:
                                     toggle_sweep(name=x, index=idx, value=v()))
            sweep_buttons.append(button)
            button.grid(column=1, row=i, sticky='es')
            sweep_vars.append(var)
            panels.append(f)
    j = len(sweep_vars)
    while len(sweep_vars) > sweep_num:
        temp = panels.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_buttons.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_labels.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_namevars.pop()
        del temp

        temp = sweep_vars.pop()
        del temp
    apply_sweep_list()


def synch_sweep_list(event=None):
    # only call when new traces are being opened
    frame = list_frame.get_frame()  # get the internal frame in list_frame
    for i, sweepname in enumerate(app.trace_display.sweeps.keys()):
        if i < len(sweep_vars):
            sweep_namevars[i].set(sweepname)
            sweep_vars[i].set(app.trace_display.sweeps[sweepname].get_linestyle() == '-')
        else:
            f = Tk.Frame(frame)
            f.grid_columnconfigure(0, weight=1)
            f.grid_rowconfigure(0, weight=1)
            f.grid(column=0, row=i, sticky='news')
            namevar = Tk.StringVar(f, value=sweepname)
            label = Tk.Label(f, textvariable=namevar, justify=Tk.LEFT)
            label.grid(column=0, row=i, sticky='news')
            sweep_namevars.append(namevar)
            sweep_labels.append(label)
            visible = app.trace_display.sweeps[sweepname].get_linestyle() == '-'
            var = Tk.BooleanVar(f, visible)
            button = ttk.Checkbutton(master=f,
                                     variable=var,
                                     command=lambda x=sweepname, idx=i, v=var.get:
                                     toggle_sweep(name=x, index=idx, value=v()))
            sweep_buttons.append(button)
            button.grid(column=1, row=i, sticky='es')
            sweep_vars.append(var)
            panels.append(f)
    while len(sweep_vars) > len(app.trace_display.sweeps):
        temp = panels.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_buttons.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_labels.pop()
        temp.forget()
        temp.destroy()
        del temp

        temp = sweep_namevars.pop()
        del temp

        temp = sweep_vars.pop()
        del temp


def apply_sweep_list(event=None, draw=True):
    selection = [i for i, v in enumerate(sweep_vars) if not v.get()]
    hide_list(selection=selection, draw=draw, undo=False)

def toggle_sweep(name=None, index=0, value=None, undo=True):
    if undo and app.interface.is_accepting_undo():
        controller.add_undo(
            [lambda n=name, i=index, v=not value, u=False:toggle_sweep(n, i, v, u),
             lambda v=not value: sweep_vars[index].set(v)]
        )
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


def show_all(event=None, draw=True, undo=True):
    if undo and app.interface.is_accepting_undo():
        list_to_hide = tuple([i for i, v in enumerate(sweep_vars) if not v.get()])
        controller.add_undo(
            [
                lambda l=list_to_hide: hide_list(selection=l, draw=True, undo=False)
            ]
        )
    show_list(selection=range(len(sweep_vars)), undo=False)
    # for v in self.sweep_vars:
    #     v.set(True)
    # for v in self.sweep_namevars:
    #     app.trace_display.sweeps[v.get()].set_linestyle('-')
    # if draw:
    #     app.trace_display.draw_ani()
    app.interface.focus()

def hide_all(event=None, draw=True, undo=True):
    if undo and app.interface.is_accepting_undo():
        list_to_show = tuple([i for i, v in enumerate(sweep_vars) if v.get()])
        controller.add_undo(
            [
                lambda l=list_to_show: show_list(selection=l, draw=True, undo=False)
            ]
        )
    hide_list(selection=range(len(sweep_vars)), undo=False)
    app.interface.focus()

def hide_selected(event=None, draw=True):
    list_to_hide = [i for i, v in enumerate(sweep_vars) if
                 app.trace_display.sweeps[sweep_namevars[i].get()].get_color() == highlight_color]
    hide_list(selection=list_to_hide, draw=draw)

def hide_list(event=None, selection=None, draw=True, undo=True):
    if selection is None:
        return None
    if undo and app.interface.is_accepting_undo():
        controller.add_undo(
            [
                lambda l=selection: show_list(selection=l, draw=True, undo=False)
            ]
        )
    for s in selection:
        try:
            sweep_vars[s].set(False)
            sweep = app.trace_display.sweeps[sweep_namevars[s].get()]
            sweep.set_linestyle('None')
            sweep.set_color(app.trace_display.trace_color)
            sweep.set_linewidth(app.trace_display.trace_width)
        except:
            pass
    if draw:
        app.trace_display.draw_ani()

def show_list(event=None, selection=None, draw=True, undo=True):
    if selection is None:
        return None
    if undo and app.interface.is_accepting_undo():
        controller.add_undo(
            [
                lambda l=selection: hide_list(selection=l, draw=True, undo=False)
            ]
        )
    for s in selection:
        sweep_vars[s].set(True)
        sweep = app.trace_display.sweeps[sweep_namevars[s].get()]
        sweep.set_linestyle('-')
        sweep.set_color(app.trace_display.trace_color)
        sweep.set_linewidth(app.trace_display.trace_width)
    if draw:
        app.trace_display.draw_ani()

##### control sweep highlight #####
def set_highlight(selection: list, draw=True):
    for name in selection:
        app.trace_display.sweeps[name].set_color(highlight_color)
        app.trace_display.sweeps[name].set_linewidth(float(highlight_width))
    if draw:
        app.trace_display.draw_ani()

def remove_highlight(selection: list, draw=True):
    for name in selection:
        app.trace_display.sweeps[name].set_color(app.trace_display.trace_color)
        app.trace_display.sweeps[name].set_linewidth(float(
            app.trace_display.trace_width))
    if draw:
        app.trace_display.draw_ani()

def clear_higlight(event=None, draw=True):
    for namevar in sweep_namevars:
        app.trace_display.sweeps[namevar.get()].set_color(app.trace_display.trace_color)
        app.trace_display.sweeps[namevar.get()].set_linewidth(
            app.trace_display.trace_width)
    if draw:
        app.trace_display.draw_ani()

def highlight_all(event=None, draw=True):
    for namevar in sweep_namevars:
        app.trace_display.sweeps[namevar.get()].set_color(highlight_color)
        app.trace_display.sweeps[namevar.get()].set_linewidth(highlight_width)
    if draw:
        app.trace_display.draw_ani()

#### retrive info
def get_visible_sweeps(event=None):
    return [i for i, v in enumerate(sweep_vars) if v.get()]

def get_highlighted_sweeps(event=None):
    return [i for i, v in enumerate(sweep_namevars) if
            app.trace_display.sweeps[v.get()].get_color() == highlight_color]




#### Make GUI Components ####
controller = PluginController(name='sweeps', menu_label='Sweeps')
form = PluginForm(controller, tab_label='Sweeps', scrollbar=False, notebook=app.cp_notebook)

#### Form GUI ####
form.insert_title(text='Sweep Selector')
form.insert_button(text='Hide All', command=hide_all)
form.insert_button(text='Show All', command=show_all)
form.grid_rowconfigure(0, weight=0)
form.grid_rowconfigure(2, weight=1)
list_frame = ScrollableOptionFrame(form)
form.insert_panel(list_frame, separator=False)
list_frame.grid(sticky='news')


#### load batch commands ####
controller.create_batch_category()
controller.add_batch_command('Show All', lambda u=False:show_all(undo=u))
controller.add_batch_command('Hide All', lambda u=False:hide_all(undo=u))

#### bind events ####
controller.listen_to_event('<<OpenedRecording>>', reset_sweep_list)
controller.listen_to_event('<<LoadCompleted>>', controller.update_plugin_display)
controller.listen_to_event('<<ChangeToOverlayView>>', controller.enable_plugin)
# controller.listen_to_event('<<Plotted>>', apply_sweep_list)
controller.listen_to_event('<<ChangeToContinuousView>>', controller.disable_plugin)
controller.listen_to_event("<<CanvasMouseRelease>>", canvas_mouse_release, condition_function=form.has_focus)
controller.listen_to_event('<<CanvasDrawRect>>', canvas_draw_rect, condition_function=form.has_focus)

for key in config.key_deselect:
    app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=clear_higlight: form.call_if_focus(func),
                                                  add='+')
for key in config.key_select_all:
    app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=highlight_all: form.call_if_focus(func),
                                                  add='+')
for key in config.key_delete:
    app.trace_display.canvas.get_tk_widget().bind(key, lambda e, func=hide_selected: form.call_if_focus(func),
                                                  add='+')
if app.inputs['trace_mode'].get() != 'overlay':
    controller.disable_plugin()
