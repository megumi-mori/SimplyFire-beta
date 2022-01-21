from tkinter import BooleanVar
from PyMini.utils.widget import DataTable
from PyMini import app
class BaseTableModule(DataTable):
    def __init__(self,
                 name: str,
                 tab_label: str,
                 parent: object
                 ):
        self.name = name
        self.tab_label = tab_label
        self.status_var = BooleanVar()
        super().__init__(parent)
        try:
            app.menubar.window_menu.index(self.name)
        except:
            app.menubar.window_menu.add_checkbutton(label=self.name,
                                                command=self.update_module_display,
                                                variable=self.status_var,
                                                onvalue=True, offvalue=False)
        self.menu.add_command(label='Copy selection', command=self.copy)
        self.menu.add_command(label='Select all', command=self.select_all)
        self.menu.add_command(label='Delete selected', command=self.delete_selected)

        self.menu.add_separator()
        self.menu.add_command(label='Fit columns', command=self.fit_columns)
        self.menu.add_command(label='Clear data', command=self.clear)

        # self.frame = Tk.Frame(parent)
        # self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure(0, weight=1)
        #
        # self.datatable = DataTable(self.frame)
        #
        # self.table = self.datatable.table
        # self.table.grid(column=0, row=0, sticky='news')

    def update_module_display(self):
        if self.status_var.get():
            app.data_notebook.tab(self, state='normal')
        else:
            app.data_notebook.tab(self, state='hidden')



