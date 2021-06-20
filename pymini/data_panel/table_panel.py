import tkinter as Tk
from tkinter import ttk
import pandas as pd
import pymini
from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict #Python 3.7+ can use dict


header2config = OrderedDict([
        ('t', 'data_display_time'),
        ('amp', 'data_display_amplitude'),
        ('amp_unit', 'data_display_amp_unit'),
        ('decay_const', 'data_display_decay_constant'),
        ('decay_unit', 'data_display_decay_unit'),
        ('decay_t', 'data_display_decay_time'),
        ('rise_const', 'data_display_rise_constant'),
        ('rise_unit', 'data_display_rise_unit'),
        ('baseline', 'data_display_baseline'),
        ('baseline_unit', 'data_display_baseline_unit'),
        ('t_start', 'data_display_start'),
        ('t_end', 'data_display_end'),
        ('channel', 'data_display_channel', )
    ])





def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    table = InteractiveTable(frame)
    table.grid(column=0, row=0, sticky='news')

    vsb = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=table.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    table.configure(yscrollcommand=vsb.set)

    frame.table = table

    hsb = ttk.Scrollbar(frame, orient=Tk.HORIZONTAL, command=table.xview)
    hsb.grid(column=0, row=1, sticky='ew')
    table.configure(xscrollcommand=hsb.set)

    columns = [
        # panel -- make sure this matches with the config2header dict
        't',
        'amp',
        'amp_unit',
        'decay_const',
        'decay_unit',
        'decay_t',
        'rise_const',
        'rise_unit',
        'baseline',
        'baseline_unit',
        't_start',
        't_end',
        'channel',
        # plot
        'peak_coord',  # (x,y)
        'decay_coord',
        'start_coord',
        'end_coord'
    ]

    table.config(columns=columns, show='headings')

    return frame

class InteractiveTable(ttk.Treeview):
    def __init__(
            self,
            parent,
            **kwargs
    ):
        super().__init__(parent, **kwargs)

    def config(self, *args, **kwargs):
        super().config(*args, **kwargs)
        if "columns" in kwargs:
            self.data = EventDataFrame(columns=kwargs['columns'])
            for i, col in enumerate(kwargs['columns']):
                self.heading(i, text=col, command=lambda _col=col: self._sort(_col, False))
                self.column(i, width=80, stretch=Tk.NO)
            self.columns = kwargs['columns']

    def fit_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        indices = [i for i, e in enumerate(header2config) if cols[header2config[e]]]
        w = int(self.winfo_width() / len(indices))
        for i in indices:
            self.column(i, width=w)

    def show_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        self.config(displaycolumns=tuple([i for i, e in enumerate(header2config) if cols[header2config[e]]]))

    ##################################################
    #                      Data                      #
    ##################################################
    def add_event(self, data, iid=None):
        """
        adds data to the dataframe and the table
        :param data: dict of data obtained from analysis
        :return:
        """
        # self.data.append(data, ignore_index=True)


        # print(pd.DataFrame(list(data.items()), columns=self.columns))
        for col in self.columns:
            try:
                data[col]
            except:
                data[col] = None
        new_row = None
        self.data = self.data.append(pd.Series(data=data, name=iid), ignore_index=False)
        self.data.sort_values(by=['t'], inplace=True, ascending=True)

        self.insert("", 'end',
                    values=[data[i] for i in self.columns],
                    iid=iid)


    ##################################################
    #                Sortable Columns                #
    ##################################################

    def _sort(self, col, reverse):
    # sort based on tutorial from Tek Recipes
    # https://tekrecipes.com/2019/04/20/tkinter-treeview-enable-sorting-upon-clicking-column-headings/
        try:
            selected_iids = self.selection()  # may need to debug this later - keeping a finger on all selected values
        except:
            pass
        try:
            l = [(float(self.set(k, col)), k) for k in self.get_children('')]
        except:
            l = [(self.set(k, col), k) for k in self.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.move(k, '', index)
        self.heading(col, command=lambda _col=col: self._sort(_col, not reverse))
















