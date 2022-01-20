import tkinter

from PyMini import app
from tkinter import BooleanVar
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
class BaseTabModule():
    def __init__(self,
                 name:str,
                 label:str,
                 scrollbar:bool=True
                 ) -> None:
        self.name = name
        self.label=label
        self.status_var = BooleanVar()
        app.menubar.window_menu.add_checkbutton(label=self.name, command=self.display_module, variable=self.status_var,
                                       onvalue=True, offvalue=False)
        if scrollbar:
            self.frame = ScrollableOptionFrame(app.cp)
            self.optionframe = self.frame.frame
        else:
            self.frame = OptionFrame(app.cp)
            self.optionframe = self.frame
        pass

        self.insert_title = self.optionframe.insert_title
        self.insert_

    def display_module(self):
        if self.status_var.get():
            app.cp_notebook.tab(self.frame, state='normal')
            print(app.cp_notebook.index('current'))
        else:
            print(app.cp_notebook.index('current'))
            app.cp_notebook.tab(self.frame, state='hidden')

