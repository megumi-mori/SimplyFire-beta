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



