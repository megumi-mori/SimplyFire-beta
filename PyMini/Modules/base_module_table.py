from tkinter import BooleanVar, ttk
from PyMini.utils.custom_widgets import DataTable
from PyMini import app
import tkinter as Tk
from tkinter import Frame
from PyMini.Modules.base_module import BaseModule
class BaseModuleDataTable(DataTable):
    def __init__(self,
                 module:BaseModule,
                 name:str='data_tab',
                 notebook: ttk.Notebook = app.data_notebook
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
        self.add_menu_command(label='Report stats', command=self.report)

        self.notebook = notebook
        self.notebook.add(self, text=self.module.tab_label)
        self.name = name
    def add(self, datadict, parent="", index='end'):
        self.disable()
        super().add(datadict, parent, index)
        self.enable()

    def append(self, dataframe):
        self.disable()
        super().append(dataframe)
        self.enable()

    def set(self, dataframe):
        self.disable()
        super().set(dataframe)
        self.enable()

    def is_visible(self):
        state = self.notebook.tab(self, option='state')
        return state == 'normal' or state == 'disabled'

    def enable(self):
        self.notebook.tab(self, state='normal')
        try:
            self.notebook.index(self.notebook.select())
        except:
            self.notebook.select(self)
        self.fit_columns()

    def disable(self):
        self.notebook.tab(self, state='disable')

    def hide(self):
        self.notebook.tab(self, state='hidden')




