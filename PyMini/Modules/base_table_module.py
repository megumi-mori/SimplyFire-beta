from tkinter import BooleanVar
from PyMini.utils.widget import DataTable
from PyMini import app
import tkinter as Tk
from tkinter import Frame
from PyMini.Modules.base_module import BaseModule
class BaseTableModule(DataTable):
    def __init__(self,
                 module:BaseModule
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

    def add(self, datadict, parent="", index='end'):
        self.disable_tab()
        super().add(datadict, parent, index)
        self.enable_tab()

    def append(self, dataframe):
        self.disable_tab()
        super().append(dataframe)
        self.enable_tab()

    def set(self, dataframe):
        self.disable_tab()
        super().set(dataframe)
        self.enable_tab()

    def update_module_display(self):
        if self.status_var.get():
            self.show_tab()
            if self.enabled:
                app.data_notebook.select(self)

            self.fit_columns()
        else:
            self.hide_tab()

    def show_tab(self):
        if self.enabled:
            app.data_notebook.tab(self, state='normal')
        else:
            app.data_notebook.tab(self, state='dosabled')

    def hide_tab(self):
        app.data_notebook.tab(self, state='hidden')

    def enable_tab(self):
        self.enabled = True
        if self.is_visible():
            app.data_notebook.tab(self, state='normal')
            app.data_notebook.select(self)

    def disable_tab(self):
        self.disabled = True
        if self.is_visible():
            app.data_notebook.tab(self, state='disabled')

    def is_visible(self):
        state = app.data_notebook.tab(self, option='state')
        return state == 'normal' or state == 'disabled'

    def set_focus(self):
        app.cp_notebook.select(self)


