import tkinter

from PyMini import app
from tkinter import BooleanVar, Frame
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
import yaml
import os
import tkinter as Tk
from .base_parent_module import BaseParentModule
class BaseControlModule(Frame):
    def __init__(self,
                 name:str,
                 menu_label:str,
                 parent_module:BaseParentModule,
                 scrollbar:bool=True,
                 filename=__file__,
                 has_table=False
                 ) -> None:
        self.parent_module = parent_module
        self.default = self.parent_module.default
        self.values = self.parent_module.values

        super().__init__(app.root)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.name = name
        self.menu_label = menu_label
        self.status_var = BooleanVar()
        self.enabled = True
        self.disable_stack = []

        self.widgets = {}
        self.module_table = None
        # app.menubar.window_menu.add_checkbutton(label=self.menu_label, command=self.update_module_display, variable=self.status_var,
        #                                onvalue=True, offvalue=False)
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
        self.insert_separator = self.optionframe.insert_separator
        self.insert_widget = self.optionframe.insert_widget

    # def update_module_display(self, event=None):
    #     if self.status_var.get():
    #         self.show_tab()
    #         if self.enabled:
    #             app.cp_notebook.select(self)
    #     else:
    #         self.hide_tab()
    #     try:
    #         self.module_table.update_module_display()
    #     except:
    #         pass

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

    def insert_StringVar(self, name):
        self.widgets[name] = Tk.StringVar(self, value=self.load_config_value(name))

    def has_focus(self):
        # use this method to check if the tab is in focus
        # use dict to allow for other locations for modules in the future
        return app.get_tab_focus()['control_panel'] == str(self)

    def is_visible(self):
        return self.parent_module.is_visible()

    def is_enabled(self):
        return self.parent_module.is_enabled()

    def hide_label_widget(self, widget):
        widget.master.master.grid_remove()

    def show_label_widget(self, widget):
        widget.master.master.grid()

    def hide_widget(self, widgetname=None, target=None):
        if widgetname:
            target = self.widgets.get(widgetname, None)
        if target is None:
            return
        try:
            target.base_frame.grid_remove()
        except:
            target.grid_remove()
        # if getattr(target, 'origin', None) == 'OptionFrame':
        #     target.master.master.grid_remove()
        # else:
        #     target.master.grid_remove()

    def show_widget(self, widgetname=None, target=None):
        if widgetname:
            target = self.widgets.get(widgetname, None)
        if target is None:
            return
        if target is None:
            return
        try:
            target.base_frame.grid()
        except:
            target.grid()

    def set_to_default(self, filter=""):
        for k, v in self.widgets.items():
            if filter:
                if filter in k:
                    # try:
                    #     self.widgets[k].set_to_default()
                    # except:
                    self.widgets[k].set(self.default[k])
            else:
                # self.widgets[k].set_to_default()
                self.widgets[k].set(self.default[k])
    def insert_file_menu(self):
        self.file_menu = Tk.Menu(app.menubar.file_menu, tearoff=0)
        app.menubar.file_menu.add_cascade(label=self.name, menu=self.file_menu)

    def get_widget_dict(self):
        return {k:self.widgets[k].get() for k in self.widgets}

    def call_if_focus(self, function):
        if self.has_focus():
            function()

    def call_if_visible(self, function):
        if self.is_visible():
            function()

    def call_if_enabled(self, function):
        if self.is_enabled():
            function()

    def load_config_value(self, name):
        return self.values.get(name, self.default.get(name, None))