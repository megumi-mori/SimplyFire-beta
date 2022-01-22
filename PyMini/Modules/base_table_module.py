from tkinter import BooleanVar
from PyMini.utils.widget import DataTable
from PyMini import app
import tkinter as Tk
from tkinter import Frame
class BaseTableModule(DataTable):
    def __init__(self,
                 name: str,
                 menu_label:str,
                 tab_label: str,
                 parent: object
                 ):
        super().__init__(parent)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)
        self.name = name
        self.menu_label=menu_label
        self.tab_label = tab_label
        self.status_var = BooleanVar()
        # self.datatable=DataTable(self)
        # self.datatable.grid(column=0, row=0, sticky='news')
        # self.table=self.datatable.table

        # self.menu = Tk.Menu(self.table, tearoff=0)
        #
        # self.table.bind("<Button-3>", self.popup, add="+")

        try:
            app.menubar.window_menu.index(self.menu_label)
        except:
            app.menubar.window_menu.add_checkbutton(label=self.menu_label,
                                                command=self.update_module_display,
                                                variable=self.status_var,
                                                onvalue=True, offvalue=False)
        # self.datatable.menu.add_command(label='Copy selection', command=self.datatable.copy)
        # self.datatable.menu.add_command(label='Select all', command=self.datatable.select_all)
        # self.datatable.menu.add_command(label='Delete selected', command=self.datatable.delete_selected)
        #
        # self.datatable.menu.add_separator()
        # self.datatable.menu.add_command(label='Fit columns', command=self.datatable.fit_columns)
        # self.datatable.menu.add_command(label='Clear data', command=self.datatable.clear)

        self.module_table = None

    def connect_to_control(self, tab):
        # connects the control panel to the table and vice versa
        if tab is None:
            return
        tab.module_table = self
        self.module_control = tab

    def popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def update_module_display(self):
        if self.status_var.get():
            self.enable_tab()
            self.fit_columns()
        else:
            app.data_notebook.tab(self, state='hidden')

    def enable_tab(self):
        app.data_notebook.tab(self, state='normal')
        app.data_notebook.select(self)



    def disable_tab(self):
        app.data_notebook.tab(self, state='disabled')



