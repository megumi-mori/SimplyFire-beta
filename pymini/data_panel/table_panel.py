import tkinter as Tk
from tkinter import ttk
import pandas as pd
import pymini
def load(parent):
    return InteractiveTable(parent)
class InteractiveTable(Tk.Frame):
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent, bg='gray')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self, selectmode='extended')
        self.table.grid(column=0, row=1, sticky='news')

        vsb = ttk.Scrollbar(self, orient=Tk.VERTICAL, command=self.table.yview)
        vsb.grid(column=1, row=1, sticky='ns')
        self.table.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient=Tk.HORIZONTAL, command=self.table.xview)
        hsb.grid(column=0, row=2, sticky='ew')
        self.table.configure(xscrollcommand=hsb.set)

        # add any other columns needed here to translate from name of widget to header info
        self.header = {
            'data_display_time': 't',
            'data_display_amplitude': 'Amp',
            'data_display_amp_unit': 'unit',
            'data_display_decay' : 'Decay (ms)',
            'data_display_decay_time': 't (decay)',
            'data_display_rise': 'Rise (ms)',
            'data_display_start': 't (start)',
            'data_display_end': 't (end)',
            'data_display_channel': 'Ch'
        }

        self.table.config(columns=[k for k in self.header.keys()], show='headings')

        # first show all data
        for i, col in enumerate(self.header):
            self.table.heading(i, text=self.header[col], command=lambda _col=col: self._sort(_col, False))
            self.table.column(i, width=80, stretch=Tk.NO)
        # self.fit_columns()

        # need to bind

    def show_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        self.table.config(displaycolumns=tuple([i for i, e in enumerate(cols) if cols[e]]))

    def fit_columns(self):
        cols = pymini.tabs['detector_tab'].get_value_dict(filter='data_display_')
        indices = [i for i, e in enumerate(cols) if cols[e]]
        w = int(self.table.winfo_width() / len(indices))
        for i in indices:
            self.table.column(i, width=w)


    def _sort(self, col, reverse):
        # sort based on tutorial from Tek Recipes
        # https://tekrecipes.com/2019/04/20/tkinter-treeview-enable-sorting-upon-clicking-column-headings/
        try:
            selected_iids = self.table.selection() #may need to debug this later - keeping a finger on all selected values
        except:
            pass
        try:
            l = [(float(self.table.set(k, col)), k) for k in self.table.get_children('')]
        except:
            l = [(self.table.set(k, col), k) for k in self.table.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.table.move(k, '', index)
        self.table.heading(col, command=lambda _col=col:self._sort(_col, not reverse))





    def display_column(self):
        pass











