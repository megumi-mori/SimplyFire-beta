import tkinter as Tk
from tkinter import ttk
import pandas as pd
import pymini
from data_panel.event_dataframe import EventDataFrame
from collections import OrderedDict #Python 3.7+ can use dict




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

    config2header = OrderedDict([
        ('data_display_time', 't'),
        ('data_display_amplitude','amp'),
        ('data_display_amp_unit', 'amp_unit'),
        ('data_display_decay_constant', 'decay_const'),
        ('data_display_decay_unit', 'decay_unit'),
        ('data_display_decay_time', 'decay_t'),
        ('data_display_rise_constant', 'rise_const'),
        ('data_display_rise_unit', 'rise_unit'),
        ('data_display_baseline', 'baseline'),
        ('data_display_baseline_unit', 'baseline_unit'),
        ('data_display_start', 't_start'),
        ('data_display_end', 't_end'),
        ('data_display_channel', 'channel')
    ])

    table.config(columns=[k for k in config2header.keys()], show='headings')
    for i, col in enumerate(config2header):
        table.heading(i, text=config2header[col], command=lambda _col=col: table._sort(_col, False))
        table.column(i, width=80, stretch=Tk.NO)

    return frame
class InteractiveTable(ttk.Treeview):
    def __init__(
            self,
            parent,
            **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.data = EventDataFrame(
            # need data for table panel AND for event markers!
            columns=[
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
        )

    ##################################################
    #                      Data                      #
    ##################################################
    def add_event(self, data):
        """
        adds data to the dataframe and the table
        :param data: dict of data obtained from analysis
        :return:
        """
        self.data.append(data)
        # self.table.



    ##################################################
    #                Sortable Columns                #
    ##################################################

    def _sort(table, col, reverse):
    # sort based on tutorial from Tek Recipes
    # https://tekrecipes.com/2019/04/20/tkinter-treeview-enable-sorting-upon-clicking-column-headings/
        try:
            selected_iids = self.selection()  # may need to debug this later - keeping a finger on all selected values
        except:
            pass
        try:
            l = [(float(table.set(k, col)), k) for k in table.get_children('')]
        except:
            l = [(table.set(k, col), k) for k in table.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            table.move(k, '', index)
        table.heading(col, command=lambda _col=col: table._sort(_col, not reverse))

    def show_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        self.config(displaycolumns=tuple([i for i, e in enumerate(cols) if cols[e]]))

    def fit_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        indices = [i for i, e in enumerate(cols) if cols[e]]
        w = int(self.winfo_width() / len(indices))
        for i in indices:
            self.column(i, width=w)














