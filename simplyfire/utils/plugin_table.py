"""
Base UI for data tables.

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
from tkinter import BooleanVar, ttk, messagebox, filedialog
from simplyfire.utils.custom_widgets import DataTable
from simplyfire import app
import tkinter as Tk
from simplyfire.utils.plugin_GUI import PluginGUI
from simplyfire.utils.plugin_controller import PluginController
import pandas as pd
import os
class PluginTable(Tk.Frame, PluginGUI):
    def __init__(self,
                 plugin_controller:PluginController,
                 tab_label:str="",
                 notebook: ttk.Notebook = app.data_notebook,
                 data_overwrite=True
                 ):
        Tk.Frame.__init__(self, app.root)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.datatable = DataTable(self)
        self.datatable.grid(column=0, row=0, sticky='news')
        PluginGUI.__init__(self, plugin_controller)

        self.status_var = BooleanVar()
        self.enabled = True

        self.datatable.add_menu_command(label='Copy selection', command=self.copy)
        self.datatable.add_menu_command(label='Select all', command=self.select_all)
        self.datatable.add_menu_command(label='Delete selected', command=self.delete_selected)

        self.datatable.add_menu_separator()
        self.datatable.add_menu_command(label='Fit columns', command=self.fit_columns)
        self.datatable.add_menu_command(label='Clear data', command=self.clear)
        self.datatable.add_menu_command(label='Report all', command=self.report)
        self.datatable.add_menu_command(label='Report selected', command=self.report_selected)

        self.notebook = notebook
        self.tab_label = tab_label
        if notebook:
            self.notebook.add(self, text=tab_label)
        self.data_overwrite=data_overwrite
        self._loaded = False

    def add(self, datadict, parent="", index='end', undo=False):
        if self.is_visible():
            self.disable()
        self.datatable.add(datadict, parent, index)
        if self.is_visible():
            self.enable()
            self.select()
        if undo and app.interface.is_accepting_undo():
            d = (datadict[self.datatable.iid_header],)
            self.controller.add_undo(
                [lambda l=d: self.datatable.delete(l)]
            )

    def append(self, dataframe, undo=False):
        if self.is_visible():
            self.disable()
        self.datatable.append(dataframe)
        if self.is_visible():
            self.enable()
            self.select()
        if undo and app.interface.is_accepting_undo():
            if dataframe is not None:
                sel = tuple([i for i in dataframe[self.datatable.iid_header]])
                self.controller.add_undo([
                   lambda l=sel:self.datatable.delete(l)
                ])

    def copy(self, event=None):
        # called by the right-click popup menu
        # overwrite this to get a different response from the menu 'Copy Selected' command
        self.datatable.copy()

    def select_all(self, event=None):
        # called by the right-click popup menu
        # overwrite this to get a different response from the menu 'Select All' command

        self.datatable.select_all()

    def clear(self, event=None):
        self.delete_all()

    def fit_columns(self, event=None):
        self.datatable.fit_columns()

    def menu_delete_selected(self, event=None):
        self.delete_selected()

    def set_data(self, dataframe):
        select = self.has_focus()
        if self.is_visible():
            self.disable()
        self.datatable.set_data(dataframe)
        if self.is_visible():
            self.enable()
            if select:
                self.select()

    def delete_all(self, e=None, undo=True):
        if undo and app.interface.is_accepting_undo():
            undo_df = {}
            for i in self.datatable.table.get_children():
                undo_df[i] = self.datatable.table.set(i)
            undo_df = pd.DataFrame.from_dict(undo_df, orient='index')
            self.controller.add_undo(
                [lambda df=undo_df, u=False: self.append(df, u)]
            )
        self.datatable.clear()

    def delete_selected(self, e=None, undo=True):
        selection = self.datatable.table.selection()
        if undo and app.interface.is_accepting_undo():
            undo_df = {}
            for i in selection:
                undo_df[i] = self.datatable.table.set(i)
            undo_df = pd.DataFrame.from_dict(undo_df, orient='index')
            self.controller.add_undo(
                [lambda df = undo_df, u=False: self.append(df, u)]
            )
        self.datatable.delete_selected()

    def is_visible(self):
        state = self.notebook.tab(self, option='state')
        return state == 'normal' or state == 'disabled'

    def has_focus(self):
        return self.notebook.select() == str(self)

    def enable(self):
        self.notebook.tab(self, state='normal')
        try:
            self.notebook.index(self.notebook.select())
        except Exception as e:
            self.select()
        self.datatable.fit_columns()


    def disable(self):
        self.notebook.tab(self, state='disable')

    def hide(self):
        self.notebook.tab(self, state='hidden')

    def select(self):
        self.notebook.select(self)
        self.datatable.fit_columns()


    def unselect(self):
        self.datatable.unselect()

    def export(self, filename, overwrite=False, mode=None):
        if not mode:
            if overwrite:
                mode = 'w'
            else:
                mode = 'x'
        self.datatable.export(filename, mode)
        self.controller.log(f'Export data: {filename}', header=True)

    def ask_export_data(self, event=None, overwrite=None, mode=None):
        if overwrite is None and mode is None:
            overwrite = self.data_overwrite
        if len(app.interface.recordings) == 0:
            messagebox.showerror('Error', 'Please open a recording file first')
            app.interface.focus()
            return None
        if len(self.datatable.table.get_children())==0:
            if not messagebox.askyesno('Warning', 'The data table is empty. Proceed?'):
                app.interface.focus()
                return None
        initialfilename = os.path.splitext(app.interface.recordings[0].filename)[0] + '_'+self.controller.name
        filename = filedialog.asksaveasfilename(filetypes=[('csv file', '*.csv')],
                                                defaultextension='.csv',
                                                initialfile=initialfilename)
        if not filename:
            app.interface.focus()
            return None
        try:
            self.export(filename,overwrite=overwrite, mode=mode)
            app.clear_progress_bar()
            return filename
        except Exception as e:
            messagebox.showerror('Error', f'Could not write data to {filename}.\nError:{e}')
            app.clear_progress_bar()
        app.interface.focus()






