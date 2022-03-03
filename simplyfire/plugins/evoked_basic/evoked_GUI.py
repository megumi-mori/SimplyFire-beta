"""
evoked_basic plugin - Handles UI component of the plugin
Must be loaded from the base UI system.
Analyze evoked synaptic events.

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
from simplyfire.utils.plugin_table import PluginTable
from simplyfire.utils import formatting, custom_widgets
from simplyfire import app
from . import evoked_analysis
import os
from tkinter import messagebox
import tkinter as Tk
import pandas as pd
import numpy as np

#### default values ####
sweep_target = 'All sweeps'
channel_target = '1'
range_target = 'Entire sweep'
range_left = 0
range_right = 1

#### variables ####
index = 0
range_option_panels = {}
parameters = {}



#### custome classes ####
class EvokedTable(PluginTable):
    def report(self, event=None):
        report()
    def report_selected(self, event=None):
        report_selected()

    def add(self, data, **kwargs):
        if data.get('#', None) is None:
            if len(self.datatable.table.get_children())>0:
                data['#'] = max([int(i) for i in self.datatable.table.get_children()]) + 1  # 1 greater than max index
            else:
                data['#'] = 0
        super().add(data, **kwargs)

class EvokedForm(PluginForm):
    def apply_parameters(self, undo=True):
        super().apply_parameters(undo=undo)
        _populate_xlim_mode()
#### define functions ####

# batch processing
def batch_calculate_min_max():
    # check visibility and show warning
    pass
def batch_export_results():
    if len(datapanel.datatable.table.get_children())== 0:
        app.batch_popup.batch_log.insert('Warning: Exporting an empty data table\n')
    fname = formatting.format_save_filename(
        os.path.splitext(app.batch_popup.file_list[app.batch_popup.file_idx])[0] + '_EvokedAnalysis.csv',
        overwrite=False)
    datapanel.export(fname, overwrite=False)
    app.batch_popup.batch_log.insert(f"Saved evoked analysis results to: {fname}\n")
# analysis
def calculate_min_max(event=None):
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    target_sweeps = []
    if form.inputs['sweep_target'].get() == 'All sweeps':
        target_sweeps = range(app.interface.recordings[0].sweep_count)
    elif form.inputs['sweep_target'].get() == 'Visible sweeps':
        target_sweeps = getattr(app.plugin_manager, 'sweeps.sweeps_GUI').get_visible_sweeps()
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get() == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    elif form.inputs['sweep_target'].get() == 'Highlighted sweeps':
        target_sweeps = getattr(app.plugin_manager, 'sweeps.sweeps_GUI').get_highlighted_sweeps()
        # account for more recordings being open (consider only the main file open)
        if app.inputs['trace_mode'].get() == 'continuous' and 0 in target_sweeps:
            target_sweeps = range(app.interface.recordings[0].sweep_count)
        elif app.inputs['trace_mode'].get() == 'overlay':
            # account for more recordings being open (consider only the main file open)
            target_sweeps = [i for i in target_sweeps if i < app.interface.recordings[0].sweep_count]
    if form.inputs['channel_target'].get():
        target_channels = [app.interface.current_channel]
    else:
        target_channels = range(app.interface.recordings[0].channel_count)

    xlim=None
    window = form.inputs['range_target'].get()
    if window == 'Visible window':
        xlim = app.trace_display.ax.get_xlim()
    elif window == 'Defined range':
        xlim = (float(form.inputs['range_left'].get()), float(form.inputs['range_right'].get()))

    recording = app.interface.recordings[0]
    mins, mins_std = evoked_analysis.calculate_min_sweeps(recording,
                                                          plot_mode=app.inputs['trace_mode'].get(),
                                                          channels=target_channels,
                                                          sweeps=target_sweeps,
                                                          xlim=xlim)
    maxs, maxs_std = evoked_analysis.calculate_max_sweeps(recording,
                                                          plot_mode=app.inputs['trace_mode'].get(),
                                                          channels=target_channels,
                                                          sweeps=target_sweeps,
                                                          xlim=xlim)
    # report
    if app.inputs['trace_mode'].get() == 'continuous':
        target_sweeps = [0] # continuous mode only has 1 sweep
    for i,c in enumerate(target_channels):
        for j,s in enumerate(target_sweeps):
            datapanel.add({
                'filename': recording.filename,
                'channel': c,
                'sweep': s,
                'min': mins[i, j, 0],
                'min_unit': recording.y_unit,
                'max': maxs[i, j, 0],
                'max_unit': recording.y_unit
            }, undo=False)
    if app.interface.is_accepting_undo():
        new_list = tuple(datapanel.datatable.table.get_children()[-len(target_sweeps)*len(target_channels):])
        controller.add_undo([
            lambda l=new_list: datapanel.datatable.delete(l)
        ])
    controller.log(msg=f'Calculate min/max')
    controller.log(msg=f'Analysis mode: {window}', header=False)
    controller.log(msg=f'xlim: {xlim}', header=False)
    controller.log(msg=f'Sweeps: {formatting.format_list_indices(target_sweeps)}, Channels: {formatting.format_list_indices(target_channels)}', header=False)
    app.interface.focus()

def delete_all(event=None, undo=True):
    datapanel.delete_all(undo=undo)
    app.interface.focus()
# reporting
def report(event=None):
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    columns = datapanel.datatable.columns
    items = datapanel.datatable.table.get_children()
    df = {}
    # initiate dict
    # print(pandas.DataFrame.from_dict({'row1':{'col1':1, 'col2': 2}, 'row2':{'col1':3, 'col2':4}}, orient='index'))
    for i in items:
        data = datapanel.datatable.table.set(i)
        for c in columns:
            if data[c] == 'None':
                data[c] = None
            elif c == 'sweep':
                data[c] = int(data[c])
            elif c == 'channel':
                data[c] = int(data[c])
            else:
                try:
                    data[c] = float(data[c])
                except:
                    pass
        df[i] = data
    if len(df) == 0:
        app.results_display.dataframe.add({
            'filename': app.interface.recordings[0].filename,
            'analysis': 'evoked',
            'sweep': None,
            'channel': app.interface.current_channel
        }, )
        return None
    df = pd.DataFrame.from_dict(df, orient='index')
    output = {'filename': app.interface.recordings[0].filename,
              'analysis': 'evoked'}
    for c in columns:
        if 'unit' in c:
            output[c] = summarize_column(df[c])
        elif 'sweep' in c:
            output[c] = formatting.format_list_indices(df[c])
        elif 'channel' in c:
            output[c] = formatting.format_list_indices(df[c])
        elif c == '#':
            pass
        else:
            try:
                output[f'{c}_avg'] = average_column(df[c])
                output[f'{c}_std'] = std_column(df[c])
            except:
                output[c] = summarize_column(df[c])
    app.results_display.dataframe.add(output)
    app.interface.focus()

def report_selected(event=None):
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    columns = datapanel.datatable.columns
    items = datapanel.datatable.table.selection()
    df = {}
    # initiate dict
    # print(pandas.DataFrame.from_dict({'row1':{'col1':1, 'col2': 2}, 'row2':{'col1':3, 'col2':4}}, orient='index'))
    for i in items:
        data = datapanel.datatable.table.set(i)
        for c in columns:
            if data[c] == 'None':
                data[c] = None
            elif c == 'sweep':
                data[c] = int(data[c])
            elif c == 'channel':
                data[c] = int(data[c])
            else:
                try:
                    data[c] = float(data[c])
                except:
                    pass
        df[i] = data
    if len(df) == 0:
        app.results_display.dataframe.add({
            'filename': app.interface.recordings[0].filename,
            'analysis': 'evoked',
            'sweep': None,
            'channel': app.interface.current_channel
        }, )
        return None
    df = pd.DataFrame.from_dict(df, orient='index')
    output = {'filename': app.interface.recordings[0].filename,
              'analysis': 'evoked'}
    for c in columns:
        if 'unit' in c:
            output[c] = summarize_column(df[c])
        elif 'sweep' in c:
            output[c] = formatting.format_list_indices(df[c])
        elif 'channel' in c:
            output[c] = formatting.format_list_indices(df[c])
        elif c == '#':
            pass
        else:
            try:
                output[f'{c}_avg'] = average_column(df[c])
                output[f'{c}_std'] = std_column(df[c])
            except:
                output[c] = summarize_column(df[c])
    app.results_display.dataframe.add(output)
    app.interface.focus()

# report helper
def summarize_column(data):
    output = []
    for d in data:
        if d is not None:
            if not d in output:
                output.append(d)
    return ','.join(output)

def average_column(data):
    return np.average(data)


def std_column(data):
    return np.std(data)

def _select_xlim_mode(event=None, undo=True):
    _apply_parameters(undo=undo)

def _populate_xlim_mode(event=None):
    selection = form.inputs['range_target'].get()
    for key in range_option_panels:
        if key != selection:
            form.hide_widget(target=range_option_panels[key])
        else:
            form.show_widget(target=range_option_panels[key])
    app.interface.focus()

#### make GUI Components ####
controller = PluginController(name='evoked_basic', menu_label='Evoked Analysis')
form = EvokedForm(controller, tab_label='Evoked', scrollbar=True, notebook=app.cp_notebook)
datapanel = EvokedTable(controller, tab_label='Evoked', notebook=app.data_notebook)
#### load layout ####
form.insert_title(text='Evoked Analysis', separator=True)
form.insert_title(text='Target setting', separator=False)
form.insert_title(text='Apply processing to the following sweeps', separator=False)

form.insert_label_optionmenu(name='sweep_target', text='',
                             options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
                             separator=False, default=sweep_target)
form.insert_label_checkbox(name='channel_target', text='Limit analysis to the current channel',
                           onvalue='1', offvalue='', separator=False, default=channel_target)
form.insert_title(text='Limit x-axis for analysis to:', separator=False)

form.insert_label_optionmenu(name='range_target', text='',
                             options=['Entire sweep', 'Visible window', 'Defined range'],
                             separator=False, default=range_target)

range_option_panels['Entire sweep'] = form.make_panel(separator=False)
range_option_panels['Visible window'] = form.make_panel(separator=False)
range_option_panels['Defined range'] = form.make_panel(separator=False)

panel = Tk.Frame(range_option_panels['Defined range'])
panel.grid(row=0, column=0, sticky='news')
panel.grid_columnconfigure(0, weight=1)
panel.grid_columnconfigure(1, weight=1)

form.inputs['range_left'] = custom_widgets.VarEntry(parent=panel, name='range_left',
                                                     validate_type='float',
                                                     default=range_left)
form.inputs['range_left'].grid(column=0, row=0, sticky='news')
form.inputs['range_left'].bind('<Return>', form.apply_parameters, add='+')
form.inputs['range_left'].bind('<FocusOut>', form.apply_parameters, add='+')
form.inputs['range_right'] = custom_widgets.VarEntry(parent=panel, name='range_right',
                                                      validate_type='float',
                                                      default=range_right)
form.inputs['range_right'].grid(column=1, row=0, sticky='news')
form.inputs['range_right'].bind('<Return>', form.apply_parameters, add='+')
form.inputs['range_right'].bind('<FocusOut>', form.apply_parameters, add='+')
form.insert_separator()

form.insert_title(text='Min/Max', separator=False)
form.insert_button(text='Calculate Min/Max', command=calculate_min_max)

form.insert_separator()
form.insert_button(text='Report stats', command=report)
form.insert_button(text='Delete all', command=delete_all)
#### datapanel ####
datapanel.datatable.define_columns(('#', 'sweep', 'channel'), iid_header='#')


#### add commands to batch ####
controller.create_batch_category()
controller.add_batch_command('Calculate min/max', calculate_min_max)
controller.add_batch_command('Report results', report)
controller.add_batch_command('Export results', batch_export_results)

#### modify GUI ####
controller.add_file_menu_command(label='Export data table', command=datapanel.ask_export_data)


#### load binding ####
controller.listen_to_event('<<OpenRecording>>', lambda u=False:delete_all(undo=u))
controller.listen_to_event('<<LoadCompleted>>', datapanel.datatable.fit_columns)

controller.load_values()
controller.update_plugin_display()
app.plugin_manager.get_plugin('evoked_basic').save = controller.save
app.plugin_manager.get_plugin('evoked_basic').load_values = controller.load_values

form.apply_parameters(undo=False)
