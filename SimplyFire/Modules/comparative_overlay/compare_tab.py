from SimplyFire.Modules.base_module_control import BaseModuleControl
from SimplyFire import app
from SimplyFire.Backend import analyzer2 as analyzer
from SimplyFire.utils import custom_widgets, formatting
import tkinter as Tk
from tkinter import filedialog, messagebox, ttk
import gc


class ModuleControl(BaseModuleControl):
    def __init__(self):
        super().__init__(
            name='comparitive_overlay',
            menu_label='Comparitive Overlay',
            tab_label='Compare',
            parent=app.root,
            scrollbar=True,
            filename=__file__,
            has_table=False
        )
        self.panel_list = []
        self.recording_list = []

        self._load_layout()
        self._load_binding()

        self.file_prefix = 'Compare_File_'
        self.sweep_prefix = "Sweep"
        
    def reset_recording_list(self, event=None):
        while len(self.panel_list) > 0:
            panel = self.panel_list.pop()
            for _, w in panel.items():
                try:
                    w.forget()
                    w.destroy()
                    del w
                except Exception as e:
                    print(f'exception deleting {w}: {e}')
                    del w
            del panel

        while len(self.recording_list) > 0:
            r = self.recording_list.pop()
            del r

    def opened_recording(self, event=None):
        recording = app.interface.recordings[0]
        self.add_recording(recording)
        self.recording_list.append(None)

    def add_recording(self, recording):
        panel_dict = self.create_file_panel(recording)
        if len(self.panel_list) == 0:
            panel_dict['remove_button'].config(state='disabled')
        self.panel_list.append(panel_dict)

    def ask_add_recording(self, event=None):
        if len(app.interface.recordings) == 0:
            app.menubar.ask_open_recording()
            return # take care of file opening via event-generation
        else:
            record = self.ask_open_recording()
        if record is None:
            return None
        self.add_recording(record)
        self.recording_list.append(record)
        self.plot(len(self.recording_list)-1, get_color=True)
        if app.custom_widgets['trace_mode'].get() == 'overlay':
            sweeps_module = app.get_module('sweeps', 'sweeps_tab')
            if sweeps_module:
                sweeps_module.synch_sweep_list() # give all the sweep names
        app.trace_display.draw_ani()
        # plot the new file

    def ask_open_recording(self):
        gc.collect()
        fname = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf"), ('All files', '*.*')])
        app.root.update()
        if not fname:
            return None
        record = analyzer.Recording(fname)
        try:
            record.set_channel(int(app.interface.channel))
        except (IndexError): # does not have the channel
            record.set_channel(0)
            app.interface.change_channel(0) # set to 0th channel
        return record

    def change_channel(self, event=None):
        # for each recording, just change the data
        for file_index in range(1, len(self.recording_list)):
            self.plot(file_index, get_color=False, synch=False)
            # recording = self.recording_list[file_index]
            # if app.widgets['trace_mode'].get() == 'continuous':
            #     app.trace_display.plot_trace(recording.get_xs(mode='continuous', channel=app.interface.channel),
            #                                  recording.get_ys(mode='continuous', channel=app.interface.channel),
            #                                  draw=False,
            #                                  relim=False,
            #                                  name=f'{self.file_prefix}{file_index}_{self.sweep_prefix}_0')
            # else:
            #     for sweep_index in range(recording.sweep_count):
            #         xs = recording.get_xs(mode='overlay', sweep=sweep_index, channel=app.interface.channel)
            #         ys = recording.get_ys(mode='overlay', sweep=sweep_index, channel=app.interface.channel)
            #         app.trace_display.plot_trace(xs, ys,
            #                                      draw=False,
            #                                      relim=False,
            #                                      name=f'{self.file_prefix}{file_index}_Sweep_{sweep_index}')

    def update_plot(self, event=None):
        if len(self.recording_list) > 1:
            for file_index in range(1, len(self.recording_list)):
                self.plot(file_index, get_color=True, synch=True)

    def plot(self, file_index, get_color=False, synch=False):
        # call this the first time plotting on the trace_display
        recording = self.recording_list[file_index]
        color = None
        if get_color:
            color = self.panel_list[file_index]['color_entry'].get()
        if app.custom_widgets['trace_mode'].get() == 'continuous':
            app.trace_display.plot_trace(recording.get_xs(mode='continuous', channel=app.interface.channel),
                                         recording.get_ys(mode='continuous', channel=app.interface.channel),
                                         draw=False,
                                         relim=False,
                                         name=f'{self.file_prefix}{file_index}_{self.sweep_prefix}_0',
                                         color=color)
        else:
            visible_list = []
            if synch:
                # get sweep list from sweeps tab
                sweep_module = app.get_module('sweeps', 'sweeps_tab')
                visible_list = sweep_module.get_visible_sweeps()
                visible_list = [int(sweep_module.sweep_namevars[i].split('_')[-1]) for i in visible_list if
                     f'{self.file_prefix}{file_index}_Sweep_' in sweep_module.sweep_namevars[i]]
                self.panel_list[file_index]['idx_entry'].set(formatting.format_list_indices(visible_list))
                print(visible_list)
            for i in range(recording.sweep_count):
                xs = recording.get_xs(mode='overlay', sweep=i, channel=app.interface.channel)
                ys = recording.get_ys(mode='overlay', sweep=i, channel=app.interface.channel)
                app.trace_display.plot_trace(xs, ys,
                                             draw=False,
                                             relim=False,
                                             name=f'{self.file_prefix}{file_index}_Sweep_{i}',
                                             color=color)
                if synch and i not in visible_list:
                    app.trace_display.sweeps[f'{self.file_prefix}{file_index}_Sweep_{i}'].set_linestyle('None')

    def remove_recording(self, index = None):
        pass

    def apply_params(self, file_index=None):
        panel_dict = self.panel_list[file_index]
        color = panel_dict.get('color_entry', None)
        indices = panel_dict.get('idx_entry', None)
        if not color or not indices:
            return None
        color = color.get()
        indices = indices.get()

        idx_list = formatting.translate_indices(indices)


        if app.custom_widgets['trace_mode'].get() == 'continuous':
            self.apply_continuous(file_index=file_index, color=color, indices=idx_list)
        else:
            self.apply_overlay(file_index=file_index, color=color, indices=idx_list)
        app.trace_display.draw_ani()

        if file_index == 0:
            style_module = app.get_module('style', 'style_tab')
            if style_module:
                style_module.widgets['style_trace_line_color'].set(color)
        if app.custom_widgets['trace_mode'].get() == 'overlay':
            sweeps_module = app.get_module('sweeps', 'sweeps_tab')
            if sweeps_module:
                sweeps_module.synch_sweep_list()
                pass

    def apply_continuous(self, file_index, color=None, indices=None):
        if file_index == 0:
            prefix = ""
            # recording = app.interface.recordings[0]
        else:
            prefix = f'{self.file_prefix}{file_index}_'
            # recording = self.recording_list[file_index]
        l = app.trace_display.sweeps[f'{prefix}{self.sweep_prefix}_0']
        if indices == [0]:
            l.set_linestyle('-')
        else:
            l.set_linestyle('None')
        if color:
            l.set_color(color)

    def apply_overlay(self, file_index, color=None, indices=None):
        if file_index == 0:
            prefix = ""
            recording = app.interface.recordings[0]
        else:
            prefix = f'{self.file_prefix}{file_index}_'
            recording = self.recording_list[file_index]
        for i in range(recording.sweep_count):
            l = app.trace_display.sweeps[f'{prefix}{self.sweep_prefix}_{i}']
            l.set_linestyle('None')
            if color:
                l.set_color(color)
        for i in indices:
            l = app.trace_display.sweeps[f'{prefix}{self.sweep_prefix}_{i}']
            l.set_linestyle('-')
        pass


    def create_file_panel(self, recording:analyzer.Recording, index=None):
        if not index:
            index = len(self.panel_list)
        panel_dict = {}
        panel = Tk.Frame(self.list_panel)
        remove_button = ttk.Button(panel, text='Remove', command=lambda i=index:self.remove_recording(i))
        apply_button = ttk.Button(panel, text='Apply', command=lambda i=index:self.apply_params(i))
        fname_label = ttk.Label(panel, text=recording.filename)
        idx_label = ttk.Label(panel, text='Sweeps:')
        if app.custom_widgets['trace_mode'].get() == 'continuous':
            default_sweeps = analyzer.format_list_indices([0])
        else:
            default_sweeps = analyzer.format_list_indices(range(recording.sweep_count))
        idx_entry = custom_widgets.VarEntry(panel, validate_type='indices', value=default_sweeps, default=0)
        color_label = ttk.Label(panel, text='Color:')
        color = app.get_module('style', 'style_tab').widgets['style_trace_line_color'].get()
        color_entry = custom_widgets.VarEntry(panel, validate_type='color',
                                              value=color,
                                              default=self.default['color'])

        # add in order of removal
        panel_dict['apply_button'] = apply_button
        panel_dict['remove_button'] = remove_button
        panel_dict['color_entry'] = color_entry
        panel_dict['color_entry_var'] = color_entry.var
        panel_dict['idx_entry'] = idx_entry
        panel_dict['idx_entry_var'] = idx_entry.var
        panel_dict['color_label'] = color_label
        panel_dict['idx_label'] = idx_label
        panel_dict['fname_label'] = fname_label
        panel_dict['panel'] = panel

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid(row=len(self.panel_list), column=0, sticky='news')
        fname_label.grid(column=0, row=0, sticky='news')
        idx_label.grid(column=0, row=1, sticky='news')
        idx_entry.grid(column=1, row=1, sticky='news')
        color_label.grid(column=0, row=2, sticky='news')
        color_entry.grid(column=1, row=2, sticky='news')
        remove_button.grid(column=0, row=3, sticky='news')
        apply_button.grid(column=1, row=3, sticky='news')
        color_entry.bind('<Return>', None, add='+')
        idx_entry.bind('<Return>', None, add='+')

        return panel_dict

    def _load_layout(self):
        self.insert_title(
            text='Comparative Overlay'
        )
        self.insert_button(
            text='Add Recording',
            command=self.ask_add_recording
        )
        self.list_panel = self.make_panel()
        self.list_panel.grid_columnconfigure(0, weight=1)



    def _load_binding(self):
        app.root.bind('<<OpenRecording>>', self.reset_recording_list, add='+')
        app.root.bind('<<OpenedRecording>>', self.opened_recording, add='+')
        # app.root.bind('<<ChangedChannel>>', lambda e, func=self.change_channel: self.call_if_enabled(func), add="+")
        app.root.bind('<<Plotted>>', lambda e, func=self.update_plot: self.call_if_enabled(func), add='+')