from SimplyFire.Modules.base_module_table import BaseModuleDataTable
from SimplyFire import app
from SimplyFire.Backend import analyzer2
from SimplyFire.utils import formatting
import pandas as pd
import numpy as np
from tkinter import messagebox
class ModuleDataTable(BaseModuleDataTable):
    def __init__(self, module):
        super().__init__(
            module=module
        )
        print(f'evoked table name: {self.name}')
        # self.table.bind('<<OpenRecordings>>', self.clear)
        self.define_columns(('#','sweep','channel'), iid_header='#')
        # self.set_iid('index')
        self._load_binding()

    def add(self, data, **kwargs):
        data['#'] = len(self.table.get_children())
        super().add(data, **kwargs)

    def report(self, event=None):
        if len(app.interface.recordings) == 0:
            messagebox.showerror('Error', 'Please open a recording file first')
            return None
        columns = self.columns
        items = self.table.get_children()
        df = {}
        # initiate dict
        # print(pandas.DataFrame.from_dict({'row1':{'col1':1, 'col2': 2}, 'row2':{'col1':3, 'col2':4}}, orient='index'))
        # make dataframe?
        for i in items:
            data = self.table.set(i)
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
                output[c] = self.summarize_column(df[c])
            elif 'sweep' in c:
                output[c] = formatting.format_list_indices(df[c])
            elif 'channel' in c:
                output[c] = formatting.format_list_indices(df[c])
            elif c == '#':
                pass
            else:
                try:
                    output[f'{c}_avg'] = self.average_column(df[c])
                    output[f'{c}_std'] = self.std_column(df[c])
                except:
                    output[c] = self.summarize_column(df[c])
        app.results_display.dataframe.add(output, )
    def report_selected(self, event=None):
        if len(app.interface.recordings) == 0:
            messagebox.showerror('Error', 'Please open a recording file first')
            return None
        columns = self.columns
        items = self.table.selection()
        df = {}
        # initiate dict
        # print(pandas.DataFrame.from_dict({'row1':{'col1':1, 'col2': 2}, 'row2':{'col1':3, 'col2':4}}, orient='index'))
        # make dataframe?
        for i in items:
            data = self.table.set(i)
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
                output[c] = self.summarize_column(df[c])
            elif 'sweep' in c:
                output[c] = formatting.format_list_indices(df[c])
            elif 'channels' in c:
                output[c] = formatting.format_list_indices(df[c])
            if c == '#':
                pass
            else:
                try:
                    output[f'{c}_avg'] = self.average_column(df[c])
                    output[f'{c}_std'] = self.std_column(df[c])
                except:
                    output[c] = self.summarize_column(df[c])
        app.results_display.dataframe.add(output, )

    def summarize_column(self, data):
        output = []
        for d in data:
            if d is not None:
                if not d in output:
                    output.append(d)
        return ','.join(output)

    def average_column(self, data):
        return np.average(data)
        pass

    def std_column(self, data):
        return np.std(data)
        pass

    def _load_binding(self):
        app.root.bind('<<OpenRecording>>', lambda e:self.clear(), add="+")