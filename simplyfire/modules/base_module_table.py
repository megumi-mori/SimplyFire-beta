"""
simplyfire - Customizable analysis of electrophysiology data
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
from simplyfire.modules.base_module import BaseModule
from simplyfire.modules.base_module_layout import BaseModuleLayout
import pandas as pd
import os
class BaseModuleDataTable(DataTable, BaseModuleLayout):
    def __init__(self,
                 module:BaseModule,
                 name:str='data_tab',
                 notebook: ttk.Notebook = app.data_notebook,
                 data_overwrite=True
                 ):
        super().__init__(app.root)

        self.module=module
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        self.status_var = BooleanVar()
        self.enabled = True
        # self.datatable=DataTable(self)
        # self.datatable.grid(column=0, row=0, sticky='news')
        # self.table=self.datatable.table

        # self.menu = Tk.Menu(self.table, tearoff=0)
        #
        # self.table.bind("<Button-3>", self.popup, add="+")

        # try:
        #     app.menubar.window_menu.index(self.menu_label)
        # except:
        #     app.menubar.window_menu.add_checkbutton(label=self.menu_label,
        #                                         command=self.update_module_display,
        #                                         variable=self.status_var,
        #                                         onvalue=True, offvalue=False)
        self.module_control = None
        self.add_menu_command(label='Copy selection', command=self.copy)
        self.add_menu_command(label='Select all', command=self.select_all)
        self.add_menu_command(label='Delete selected', command=self.delete_selected)

        self.add_menu_separator()
        self.add_menu_command(label='Fit columns', command=self.fit_columns)
        self.add_menu_command(label='Clear data', command=self.clear)
        self.add_menu_command(label='Report all', command=self.report)
        self.add_menu_command(label='Report selected', command=self.report_selected)

        self.notebook = notebook
        self.notebook.add(self, text=self.module.tab_label)

        self.data_overwrite=data_overwrite
        self.name = name
        self._loaded = False
    def add(self, datadict, parent="", index='end', undo=True):
        if self.is_visible():
            self.disable()
        super().add(datadict, parent, index)
        if self.is_visible():
            self.enable()
        if self.module.control_tab.has_focus():
            self.select()
        if undo and app.interface.is_accepting_undo():
            d = (datadict[self.iid_header],)
            self.module.add_undo(
                [lambda l=d: self.delete(l)]
            )

    def append(self, dataframe, undo=True):
        if self.is_visible():
            self.disable()
        super().append(dataframe)
        if self.is_visible():
            self.enable()
        if self.module.control_tab.has_focus():
            self.select()
        if undo and app.interface.is_accepting_undo():
            if dataframe is not None:
                sel = tuple([i for i in dataframe[self.iid_header]])
                self.module.add_undo([
                   lambda l=sel:self.delete(l)
                ])

    def set_data(self, dataframe):
        if self.is_visible():
            self.disable()
        super().set_data(dataframe)
        if self.is_visible():
            self.enable()
        if self.module.control_tab.has_focus():
            self.select()

    def delete_selected(self, e=None, undo=True):
        selection = self.table.selection()
        if undo and app.interface.is_accepting_undo():
            undo_df = {}
            for i in selection:
                undo_df[i] = self.table.set(i)
            undo_df = pd.DataFrame.from_dict(undo_df, orient='index')
            self.module.add_undo(
                [lambda df = undo_df, u=False: self.append(df, u)]
            )
        super().delete_selected()

    def is_visible(self):
        state = self.notebook.tab(self, option='state')
        return state == 'normal' or state == 'disabled'

    def enable(self):
        self.notebook.tab(self, state='normal')
        try:
            self.notebook.index(self.notebook.select())
        except Exception as e:
            self.select()
        if not self._loaded:
            if self.winfo_width() > 1:
                self.fit_columns()
                self._loaded = True

    def disable(self):
        self.notebook.tab(self, state='disable')

    def hide(self):
        self.notebook.tab(self, state='hidden')

    def select(self):
        self.notebook.select(self)
        if not self._loaded:
            if self.winfo_width() > 1:
                self.fit_columns()
                self._loaded = True

    def export(self, filename, overwrite=False, mode=None):
        if not mode:
            if overwrite:
                mode = 'w'
            else:
                mode = 'x'
        super().export(filename, mode)

    def ask_export_data(self, event=None, overwrite=None, mode=None):
        if overwrite is None and mode is None:
            overwrite = self.data_overwrite
        if len(app.interface.recordings) == 0:
            messagebox.showerror('Error', 'Please open a recording file first')
            app.interface.focus()
            return None
        if len(self.table.get_children())==0:
            if not messagebox.askyesno('Warning', 'The data table is empty. Proceed?'):
                app.interface.focus()
                return None
        initialfilename = os.path.splitext(app.interface.recordings[0].filename)[0] + '_'+self.module.name
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
            messagebox.showerror('Error', f'Cojuld not write data to {filename}.\nError:{e}')
            app.clear_progress_bar()
        app.interface.focus()






