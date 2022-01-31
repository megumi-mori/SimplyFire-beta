from PyMini.Modules.base_control_module import BaseControlModule
from PyMini import app
from PyMini.Backend import analyzer2 as analyzer
from PyMini.utils import widget
import tkinter as Tk
from tkinter import filedialog, messagebox, ttk
import gc


class ModuleControl(BaseControlModule):
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

        self.recordings = []
        self.panel_list = []

        self._load_layout()
        self._load_binding()
    def reset_recording_list(self, event=None):
        for p in self.panel_list:
            for w in p:
                try:
                    w.forget()
                    w.destroy()
                    del w
                except:
                    del w
        recording = app.interface.recordings[0]
        self.add_recording(recording)

    def ask_add_recording(self, event=None):
        if len(app.interface.recordings) == 0:
            app.menubar.ask_open_recording()
            record = app.interface.recordings[0]
        else:
            record = self.ask_open_recording()
        if record is None:
            return None
        self.add_recording(record)

    def add_recording(self, recording):
        panel_dict = self.create_control_set(recording)
        if len(self.panel_list) == 0:
            panel_dict['remove_button'].config(state='disabled')
        self.panel_list.append(panel_dict)
        pass

    def remove_recording(self, index = None):
        pass
    def apply_params(self, index=None):
        pass
    def create_control_set(self, recording:analyzer.Recording, index=None):
        if not index:
            index = len(self.panel_list)
        panel_dict = {}
        panel = Tk.Frame(self.list_panel)
        remove_button = ttk.Button(panel, text='Remove', command=lambda e, i=index:self.remove_recording(i))
        apply_button = ttk.Button(panel, text='Apply', command=lambda e, i=index:self.apply_params(i))
        fname_label = ttk.Label(panel, text=recording.filename)
        idx_label = ttk.Label(panel, text='Sweeps:')
        default_sweeps = analyzer.format_list_indices(range(recording.sweep_count))
        idx_entry = widget.VarEntry(panel, validate_type='indices', value=default_sweeps, default=0)
        color_label = ttk.Label(panel, text='Color:')
        color_entry = widget.VarEntry(panel, validate_type='color',
                                      value=self.values.get('color', self.default['color']),
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
        app.root.bind('<<OpenedRecording>>', self.reset_recording_list)