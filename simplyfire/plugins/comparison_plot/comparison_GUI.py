"""
Comparison Plugin - allows overlay of multiple abf files

SimplyFire - Customizable analysis of electrophysiology data
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
from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire import app
from simplyfire.utils.recording import Recording
from simplyfire.utils import custom_widgets
from simplyfire.utils import formatting

import gc
from tkinter import ttk, filedialog, messagebox
import tkinter as Tk

#### variables ####

show_legend = True

compared_recordings = []
compared_lines = []
panels = []
colors = []
sweeps = []

#### custom class ####
class CompareController(PluginController):
    def toggle_module_display(self, event=None, undo=True):
        super().toggle_module_display(event=event, undo=undo)

        if not self.is_visible():
            clear_lines()
            app.trace_display.draw_ani()
        elif self.is_visible():
            plot_recordings(draw=False)
            for detail_dict in panels:
                apply(detail_dict, draw=False, undo=False)
            app.trace_display.draw_ani()
        if undo and app.interface.is_accepting_undo():
            app.interface.add_undo([
                lambda v=not self.inputs['is_visible'].get():self.inputs['is_visible'].set(v),
                lambda u=False: self.toggle_module_display(undo=u)
            ])

#### functions ####
def add_file(event=None, recording=None, undo=True):
    temp_undo_stack = []
    if app.interface.has_open_recording(): # check if a file is open
        if recording is None:
            recording = ask_open_recording()
            if recording is None:
                return None # no file opened
        compared_recordings.append(recording) # append the file
        try:
            recording.set_channel(app.interface.current_channel)  # 0 indexing
        except (IndexError):  # forced channel does not exist
            temp_undo_stack.append(
                lambda c=app.interface.current_channel: app.interface.change_channel(num=c, save_undo=False))
            app.interface.change_channel(0, save_undo=False)  # revert to the first channel
            pass
    else:
        app.menubar.ask_open_recording() # go through regular file open dialogue
        return
    # make a new panel
    details = populate_panel(recording)

    # plot the data
    plot_recordings(draw=False)
    # apply the initial details
    apply(details, draw=False, undo=False)

    xlim = app.trace_display.ax.get_xlim()
    ylim = app.trace_display.ax.get_ylim()
    app.trace_display.update_default_lim(x=True, y=True, fix_x=True, fix_y=False)
    app.trace_display.set_axis_limit('x', xlim, draw=False)
    app.trace_display.set_axis_limit('y', ylim, draw=False)
    app.trace_display.draw_ani()
    # param_guide.update()

    app.pb['value'] = 0
    app.pb.update()
    app.interface.focus()

    if undo and app.interface.is_accepting_undo():
        # filename =
        # temp_undo_stack.insert(0, lambda i=panel_index:remove(panel_index=i, undo=False))
        # controller.add_undo(temp_undo_stack)
        panel_index=details['index']+1
        controller.add_undo([lambda i=panel_index:remove(panel_index=i, undo=False)])

def apply(details, draw=True, undo=True):
    index = details['index']
    if index < 0:
        recording = app.interface.recordings[0]
    else:
        recording = compared_recordings[index]
    if app.inputs['trace_mode'].get() == 'overlay':
        show_indices = formatting.translate_indices_bool(details['sweeps_entry'].get(), recording.sweep_count)
    elif app.inputs['trace_mode'].get() == 'continuous':
        show_indices = formatting.translate_indices_bool(details['sweeps_entry'].get(), 1)
    if index >= 0:
        for i, b in enumerate(show_indices):
            compared_lines[index][i].set_linestyle({True:'-', False:'None'}[b])
            compared_lines[index][i].set_color(details['color_entry'].get())

    else:
        for i, b in enumerate(show_indices):
            app.trace_display.sweeps[f'Sweep_{i}'].set_linestyle({True:'-', False: 'None'}[b])
            app.trace_display.sweeps[f'Sweep_{i}'].set_color(details['color_entry'].get())
    if draw:
        app.trace_display.draw_ani()
    if undo and app.interface.is_accepting_undo():
        undo_color = details['undo_color']
        undo_indices = details['undo_indices']
        if details['undo_color'] != details['color_entry'].get() or details['undo_indices'] != details[
            'sweeps_entry'].get():
            controller.add_undo([lambda i=index, c=undo_color, x=undo_indices: apply_undo(i, c, x)])
    details['undo_color'] = details['color_entry'].get()
    details['undo_indices'] = details['sweeps_entry'].get()
    app.interface.focus()



def apply_undo(index, color, indices):
    panels[index+1]['sweeps_entry'].set(indices)
    panels[index+1]['color_entry'].set(color)

    apply(panels[index+1], draw=True, undo=False)
    pass


def populate_panel(recording):
    # first make panels as needed
    widgets = {} # store info here?
    widgets['index'] = len(panels)-1 # inex of the recording
    frame = Tk.Frame(control_panel)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid(column=0, row=len(panels), sticky='news')
    widgets['frame'] = frame
    label = ttk.Label(master=frame, text=recording.filename)
    label.grid(column=0, row=0, sticky='news')
    widgets['filename_label'] = label

    # options
    entry_panel = Tk.Frame(frame)
    entry_panel.grid_columnconfigure(0, weight=1)
    entry_panel.grid_columnconfigure(1, weight=1)

    widgets['entry_panel'] = entry_panel
    label = ttk.Label(master=entry_panel, text='Sweeps:')
    label.grid(column=0, row=0, sticky='news')
    widgets['sweeps_label'] = label
    if app.inputs['trace_mode'].get() == 'continuous':
        entry = custom_widgets.VarEntry(parent=entry_panel, validate_type='indices',
                                        default='0')
    elif app.inputs['trace_mode'].get() == 'overlay':
        entry = custom_widgets.VarEntry(parent=entry_panel, validate_type='indices',
                                    default=formatting.format_list_indices(range(recording.sweep_count)))
    entry.grid(column=1, row=0, sticky='news')
    entry.bind('<Return>', lambda e, w=widgets: apply(details=w), add='+')
    entry.bind('<FocusOut>', lambda e, w=widgets: apply(details=w), add='+')
    widgets['sweeps_entry'] = entry
    widgets['undo_indices'] = entry.get()
    label = ttk.Label(master=entry_panel, text='Color:')
    label.grid(column=0, row=1, sticky='news')
    widgets['color_label'] = label
    try:
        color = colors[len(panels)]
    except IndexError:
        color = app.trace_display.trace_color
    entry = custom_widgets.VarEntry(parent=entry_panel, validate_type='color', value=color,
                                    default='black')
    widgets['undo_color'] = 'black'
    entry.grid(column=1, row=1, stick='news')
    entry_panel.grid(column=0, row=1, sticky='news')
    entry.bind('<Return>', lambda e, w=widgets:apply(details=w), add='+')
    entry.bind('<FocusOut>', lambda e, w=widgets: apply(details=w), add='+')
    widgets['color_entry'] = entry
    # buttons
    button_panel = Tk.Frame(frame)
    button_panel.grid_columnconfigure(0, weight=1)
    button_panel.grid_rowconfigure(0, weight=1)
    button_panel.grid(column=0, row=2, sticky='news')
    widgets['button_panel'] = button_panel
    button = ttk.Button(master=button_panel, text='Apply', command=lambda w=widgets:apply(w))
    button.grid(column=0, row=0, sticky='news')
    widgets['apply_button'] = button
    button = ttk.Button(master=button_panel, text='Remove', command=lambda w=widgets:remove(w))
    button.grid(column=1, row=0, sticky='news')
    widgets['remove_button'] = button
    if len(compared_recordings) == 0:
        button.config(state='disabled')

    panels.append(widgets)
    return widgets


def ask_open_recording():
    gc.collect()
    fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
    app.root.update()

    temp_undo_stack = []
    if not fname:
        return None

    try:
        record = Recording(fname)
    except Exception as e:
        messagebox.showerror('Read file error', f'The selected file could not be opened.\nError code: {e}')
        return None
    controller.log(msg=f'Open {fname}')
    return record

def change_channel(event=None):
    plot_recordings(draw=False)
    app.trace_display.update_default_lim(x=False, y=True, fix_x=True, fix_y=False)

def change_mode(event=None):
    clear_lines()
    if app.inputs['trace_mode'].get() == 'continuous':
        for detail_dict in panels:
            detail_dict['sweeps_entry'].set(0)
    elif app.inputs['trace_mode'].get() == 'overlay':
        for detail_dict in panels:
            if detail_dict['index'] < 0:
                recording = app.interface.recordings[0]
            else:
                recording = compared_recordings[detail_dict['index']]
            detail_dict['sweeps_entry'].set(formatting.format_list_indices(range(recording.sweep_count)))
    if len(compared_recordings)>0:
        plot_recordings(draw=False)
        app.trace_display.update_default_lim()
    if controller.is_visible():
        for detail_dict in panels:
            apply(detail_dict, draw=False, undo=False)


def clear_lines(event=None):
    """
    removes each of the line object, but keeps the list structure
    """
    for lines in compared_lines:
        while len(lines)>0:
            l = lines.pop()
            try:
                l.remove()
            except:
                pass
            try:
                del l
            except:
                pass
    app.interface.plot(fix_y=True, fix_x=True, relim=True)

def on_open(event=None):
    # clear the panels
    while len(panels) > 1:
        remove_file(1)
    try:
        remove_file(0)
    except:
        pass
    populate_panel(app.interface.recordings[0])
    # while len(compared_recordings) > 0:
    #     r = compared_recordings.pop()
    #     del r
    # while len(compared_lines) > 0:
    #     lines = compared_lines.pop()
    #     for l in lines:
    #         try:
    #             l.remove()
    #         except: # line already removed from artist
    #             pass
    #         del l

def remove_file(panel_index):
    # try:
    p = panels[panel_index]
    for key in ['remove_button', 'apply_button', 'button_panel', 'color_entry', 'sweeps_entry', 'entry_panel',
                'filename_label', 'frame', 'index']:
        try:
            p[key].grid_remove()
        except:
            pass
        try:
            p[key].remove()
        except:
            pass
        try:
            del p[key]
        except:
            pass
    p = panels.pop(panel_index)
    del p
    if panel_index < len(panels):
        for panel in panels[panel_index:]:
            panel['index'] -= 1 # update the index of each panel
            panel['frame'].grid(row=panel['index']+1)

    if panel_index>0:
        r = compared_recordings.pop(panel_index-1)
        del r
        lines = compared_lines.pop(panel_index-1)
        while len(lines)>0:
            l = lines.pop()
            try:
                l.remove()
            except:  # line already removed from artist
                pass
            del l
    # except: # nothing in panels yet
    #     pass
def plot_recordings(recordings=None, draw=True):
    if recordings is None:
        recordings = compared_recordings
    mode = app.inputs['trace_mode'].get()
    for i, r in enumerate(recordings):
        if mode == 'overlay':
            for s in range(r.sweep_count):
                plot_trace(r.get_xs(mode=mode, sweep=s, channel=app.interface.current_channel),
                       r.get_ys(mode=mode, sweep=s, channel=app.interface.current_channel),
                       recording_index=i, sweep_num=s)
        else:
            plot_trace(r.get_xs(mode=mode, sweep=0, channel=app.interface.current_channel),
                       r.get_ys(mode=mode, sweep=0, channel=app.interface.current_channel),
                       recording_index=i, sweep_num=0)
    if draw:
        app.trace_display.draw_ani()
    pass

def plot_trace(xs, ys, color=None, recording_index=0, sweep_num=0):
    global compared_lines
    if color is None:
        color = app.trace_display.trace_color
    if recording_index > len(compared_lines)-1:
        compared_lines.append([]) # make a new dict
    if sweep_num > len(compared_lines[recording_index])-1:
        line, = app.trace_display.ax.plot(xs, ys, color=color, linewidth=app.trace_display.trace_width)
        compared_lines[recording_index].append(line)
    else:
        compared_lines[recording_index][sweep_num].set_xdata(xs)
        compared_lines[recording_index][sweep_num].set_ydata(ys)

def remove(details:dict=None, panel_index=None, undo=True):
    if details is None:
        details = panels[panel_index]
    # remove a recording being overlayed
    fname = compared_recordings[details['index']].filepath
    remove_file(panel_index=details['index']+1)
    xlim = app.trace_display.ax.get_xlim()
    ylim = app.trace_display.ax.get_ylim()
    app.trace_display.update_default_lim()
    app.trace_display.set_axis_limit('x', xlim, draw=False)
    app.trace_display.set_axis_limit('y', ylim, draw=False)
    if undo and app.interface.is_accepting_undo():
        controller.add_undo([lambda f=fname:remove_undo(f)])
    app.interface.focus()

def remove_undo(fname):
    record = Recording(fname)
    add_file(recording = record, undo=False)


def comparison_mode(event=None):
    return len(compared_recordings)>0 and controller.is_visible()


#### configure GUI component ####
app.menubar.view_menu.add_separator()
controller = CompareController(name='comparison_plot', menu_label='Comparison', menu_target=app.menubar.view_menu)
form = PluginForm(plugin_controller=controller, tab_label='Compare', scrollbar=False, notebook=app.cp_notebook)

#### GUI layout ####
control_panel = form.make_panel(separator=False)
form.insert_button(text='Add File', command=add_file)
form.grid_rowconfigure(0, weight=0)
form.grid_rowconfigure(1, weight=1)


#### bindings ####
controller.listen_to_event('<<ChangedChannel>>', change_channel, condition_function=comparison_mode)
controller.listen_to_event('<<OpenedRecording>>', on_open)
controller.listen_to_event('<<ChangedToOverlayView>>', change_mode)
controller.listen_to_event('<<ChangedToContinuousView>>', change_mode)

controller.update_plugin_display()