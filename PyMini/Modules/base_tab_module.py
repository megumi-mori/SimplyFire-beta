import tkinter

from PyMini import app
from tkinter import BooleanVar, Frame
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
import yaml
import os
class BaseControlModule(Frame):
    def __init__(self,
                 name:str,
                 menu_label:str,
                 tab_label:str,
                 parent:object,
                 scrollbar:bool=True,
                 filename=__file__,
                 has_table=False
                 ) -> None:
        try:
            with open(os.path.join(os.path.dirname(filename), 'default_values.yaml'), 'r') as f:
                self.default = yaml.safe_load(f)
        except:
            self.default = {}
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.name = name
        self.menu_label = menu_label
        self.tab_label = tab_label
        self.status_var = BooleanVar()
        self.widgets = {}
        app.menubar.window_menu.add_checkbutton(label=self.menu_label, command=lambda t=has_table:self.update_module_display(t), variable=self.status_var,
                                       onvalue=True, offvalue=False)
        if scrollbar:
            self.frame = ScrollableOptionFrame(self)
            self.optionframe = self.frame.frame
        else:
            self.frame = OptionFrame(self)
            self.optionframe = self.frame
        pass
        self.frame.grid(row=0, column=0, sticky='news')
        self.insert_panel = self.optionframe.insert_panel
        self.make_panel = self.optionframe.make_panel

    def update_module_display(self, table=False):
        if self.status_var.get():
            app.cp_notebook.tab(self, state='normal')
            if table:
                app.data_notebook.tab(app.get_data_frame(self.name), state='normal')
        else:
            app.cp_notebook.tab(self, state='hidden')
            if table:
                app.data_notebook.tab(app.get_data_frame(self.name), state='hidden')

    def insert_title(self, **kwargs):
        title = self.optionframe.insert_title(**kwargs)
        try:
            self.widgets[kwargs['name']] = title
        except Exception as e:
            pass
        return title

    def insert_label_entry(self, **kwargs):
        entry = self.optionframe.insert_label_entry(default=self.default[kwargs['name']], **kwargs)
        try:
            self.widgets[kwargs['name']] = entry
        except:
            pass
        return entry

    def insert_button(self, **kwargs):
        button = self.optionframe.insert_button(**kwargs)
        try:
            self.widgets[kwargs['name']] = button
        except:
            pass
        return button

    def insert_label_checkbox(self, **kwargs):
        checkbox = self.optionframe.insert_label_checkbox(default=self.default[kwargs['name']], **kwargs)
        try:
            self.widgets[kwargs['name']] = checkbox
        except:
            pass
        return checkbox

    def insert_label_optionmenu(self, **kwargs):
        optionmenu = self.optionframe.insert_label_optionmenu(default=self.default[kwargs['name']], **kwargs)
        try:
            self.widgets[kwargs['name']] = optionmenu
        except:
            pass

    def has_focus(self):
        # use this method to check if the tab is in focus
        # use dict to allow for other locations for modules in the future
        return app.get_tab_focus()['control_panel'] == str(self)
    def hide_label_widget(self, widget):
        widget.master.master.grid_remove()

    def show_label_widget(self, widget):
        widget.master.master.grid()

    def set_to_default(self, filter=""):
        for k, v in self.widgets.items():
            if filter:
                if filter in k:
                    self.widgets[k].set(self.default[k])
            else:
                self.widgets[k].set(self.default[k])