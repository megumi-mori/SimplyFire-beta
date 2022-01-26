import tkinter

from PyMini import app
from tkinter import BooleanVar, Frame
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
import yaml
import os
import tkinter as Tk

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
        try:
            self.values = app.config.user_vars[name]
        except:
            self.values = {}
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.name = name
        self.menu_label = menu_label
        self.tab_label = tab_label
        self.status_var = BooleanVar()
        self.widgets = {}
        self.module_table = None
        app.menubar.window_menu.add_checkbutton(label=self.menu_label, command=self.update_module_display, variable=self.status_var,
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

    def update_module_display(self, event=None):
        print('update module display called')
        if self.status_var.get():
            print('show tab')
            self.show_tab()
        else:
            print('hide tab')
            self.hide_tab()
        try:
            self.module_table.update_module_display()
        except:
            pass

    def insert_title(self, **kwargs):
        title = self.optionframe.insert_title(**kwargs)
        try:
            self.widgets[kwargs['name']] = title
        except Exception as e:
            pass
        return title

    def insert_label_entry(self, **kwargs):
        entry = self.optionframe.insert_label_entry(value=self.values.get(kwargs['name'], None),
                                                    default=self.default.get(kwargs['name'], None), **kwargs)
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
        checkbox = self.optionframe.insert_label_checkbox(value=self.values.get(kwargs['name'], None),
                                                          default=self.default.get(kwargs['name'],None), **kwargs)
        try:
            self.widgets[kwargs['name']] = checkbox
        except:
            pass
        return checkbox

    def insert_label_optionmenu(self, **kwargs):
        optionmenu = self.optionframe.insert_label_optionmenu(value=self.values.get(kwargs['name'],None),
                                                              default=self.default[kwargs['name']], **kwargs)
        try:
            self.widgets[kwargs['name']] = optionmenu
        except:
            pass

    def has_focus(self):
        # use this method to check if the tab is in focus
        # use dict to allow for other locations for modules in the future
        return app.get_tab_focus()['control_panel'] == str(self)

    def is_visible(self):
        try:
            state = app.cp_notebook.tab(self, option='state')
            return state == 'normal' or state == 'disabled'
        except:
            # not yet managed by the notebook widget
            return None

    def is_enabled(self):
        return app.cp_notebook.tab(self, option='state') == 'normal'

    def show_tab(self):
        app.cp_notebook.tab(self, state='normal')
        app.cp_notebook.select(self)

    def hide_tab(self):
        app.cp_notebook.tab(self, state='hidden')

    def enable_tab(self):
        if self.is_visible():
            app.cp_notebook.tab(self, state='normal')
            app.cp_notebook.select(self)

    def disable_tab(self):
        if self.is_visible():
            app.cp_notebook.tab(self, state='disabled')
    def hide_label_widget(self, widget):
        widget.master.master.grid_remove()

    def show_label_widget(self, widget):
        widget.master.master.grid()

    def set_to_default(self, filter=""):
        for k, v in self.widgets.items():
            if filter:
                if filter in k:
                    self.widgets[k].set_to_default()
            else:
                self.widgets[k].set_to_default()

    def insert_file_menu(self):
        self.file_menu = Tk.Menu(app.menubar.file_menu, tearoff=0)
        app.menubar.file_menu.add_cascade(label=self.name, menu=self.file_menu)

    def get_widget_dict(self):
        return {k:self.widgets[k].get() for k in self.widgets}