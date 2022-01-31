from PyMini.Modules.base_table_module import BaseTableModule
from PyMini import app
from PyMini.Backend import analyzer2
import pandas as pd
import numpy as np
from tkinter import messagebox
class ModuleTable(BaseTableModule):
    def __init__(self):
        super().__init__(
            name='evoked',
            menu_label='Evoked Analysis',
            tab_label='Evoked',
            parent=app.root
        )
        self.table.bind('<<OpenRecordings>>', self.clear)
        self.define_columns(('sweep','channel'))
        self.set_iid('index')

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
                    data[c] == int(data[c])
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
                'channel':app.interface.recordings[0].channel
            })
            return None
        df = pd.DataFrame.from_dict(df, orient='index')
        output = {'filename': app.interface.recordings[0].filename,
                  'analysis': 'evoked'}
        for c in columns:
            if 'unit' in c:
                output[c] = self.summarize_column(df[c])
            elif 'sweep' in c:
                output[c] = analyzer2.format_list_indices(df[c])
            elif 'channels' in c:
                output[c] = analyzer2.format_list_indices(df[c])

            else:
                try:
                    output[f'{c}_avg'] = self.average_column(df[c])
                    output[f'{c}_std'] = self.std_column(df[c])
                except:
                    output[c] = self.summarize_column(df[c])
        app.results_display.dataframe.add(output)

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