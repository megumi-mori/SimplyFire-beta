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

        # need to bind

    def fill_data_table(self):
        self.cols = pymini.tabs['detector'].get_value_dict(filter='data_display_')

        data_tag = {
            'data_display_time': 't',
            'data_display_amplitude': 'Amp ({})'.format(pymini.plot_area.get_unit('y')),
            'data_display_decay' : 'Decay (ms)',
            'data_display_decay_time': 't (decay)',
            'data_display_rise': 'Rise (ms)',
            'data_display_baseline': 't (baseline)',
            'data_display_channel': 'Ch'
        }

        self.table.config(columns=[data_tag[key] for key in self.cols if self.cols[key]], show='headings')
        pymini.root.update()

        for i, col in enumerate(self.cols):
            if self.cols[col]:
                self.table.heading(i, text=data_tag[col])
                self.table.column(i, width=80, stretch=Tk.NO)

    # sort based on tutorial from Tek Recipes
    # https://tekrecipes.com/2019/04/20/tkinter-treeview-enable-sorting-upon-clicking-column-headings/










