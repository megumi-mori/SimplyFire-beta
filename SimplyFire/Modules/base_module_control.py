import tkinter

from SimplyFire import app
from tkinter import BooleanVar, Frame
from SimplyFire.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from SimplyFire.utils import custom_widgets
import yaml
import os
from tkinter import ttk
import tkinter as Tk
from .base_module import BaseModule
from .base_module_layout import BaseModuleLayout
class BaseModuleControl(ScrollableOptionFrame, BaseModuleLayout):
    def __init__(self,
                 module:BaseModule,
                 name:str='control_tab',
                 scrollbar:bool=True,
                 notebook:ttk.Notebook=app.cp_notebook
                 ) -> None:
        ScrollableOptionFrame.__init__(self, app.root, scrollbar)
        BaseModuleLayout.__init__(self, module)

        self.defaults = self.module.defaults
        self.values = self.module.values
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.widgets = self.module.widgets
        # app.menubar.window_menu.add_checkbutton(label=self.menu_label, command=self.update_module_display, variable=self.status_var,
        #                                onvalue=True, offvalue=False)
        # if scrollbar:
        #     self.frame = ScrollableOptionFrame(self)
        #     self.optionframe = self.frame.frame
        # else:
        #     self.frame = OptionFrame(self)
        #     self.optionframe = self.frame

        # pass
        # self.frame.grid(row=0, column=0, sticky='news')
        self.insert_panel = self.frame.insert_panel
        self.make_panel = self.frame.make_panel
        self.insert_separator = self.frame.insert_separator
        self.insert_widget = self.frame.insert_widget

        self.notebook = notebook
        self.notebook.add(self, text=self.module.tab_label)

        self.name = name

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
        # title = self.optionframe.insert_title(**kwargs)
        title = self.frame.insert_title(**kwargs)
        try:
            self.widgets[kwargs['name']] = title
        except Exception as e:
            pass
        return title

    def insert_label_entry(self, **kwargs):
        if 'value' not in kwargs.keys():
            kwargs['value'] = self.values.get(kwargs['name'], None)
        if 'default' not in kwargs.keys():
            kwargs['default'] = self.defaults.get(kwargs['name'], None)
        entry = self.frame.insert_label_entry(**kwargs)
        try:
            self.widgets[kwargs['name']] = entry
        except:
            pass
        return entry

    def insert_button(self, **kwargs):
        button = self.frame.insert_button(self, **kwargs)
        try:
            self.widgets[kwargs['name']] = button
        except:
            pass
        return button

    def insert_label_checkbox(self, **kwargs):
        if 'value' not in kwargs.keys():
            kwargs['value'] = self.values.get(kwargs['name'], None)
        if 'default' not in kwargs.keys():
            kwargs['default'] = self.defaults.get(kwargs['name'], None)
        checkbox = self.frame.insert_label_checkbox(**kwargs)
        try:
            self.widgets[kwargs['name']] = checkbox
        except:
            pass
        return checkbox

    def insert_label_optionmenu(self, **kwargs):
        if 'value' not in kwargs.keys():
            kwargs['value'] = self.values.get(kwargs['name'], None)
        if 'default' not in kwargs.keys():
            kwargs['default'] = self.defaults.get(kwargs['name'], None)
        optionmenu = self.frame.insert_label_optionmenu(**kwargs)
        try:
            self.widgets[kwargs['name']] = optionmenu
        except:
            pass

    def insert_StringVar(self, name):
        self.widgets[name] = Tk.StringVar(self, value=self.load_config_value(name))

    def make_entry(self, parent, **kwargs):
        if 'value' not in kwargs.keys():
            kwargs['value'] = self.values.get(kwargs['name'], None)
        if 'default' not in kwargs.keys():
            kwargs['default'] = self.defaults.get(kwargs['name'], None)
        self.widgets[kwargs['name']] = custom_widgets.VarEntry(parent=parent,
                                                               **kwargs)
        return self.widgets[kwargs['name']]

    def make_label(self, parent, **kwargs):
        return ttk.Label(parent, **kwargs)

    def make_button(self, parent, **kwargs):
        return ttk.Button(parent, **kwargs)

    def has_focus(self):
        # use this method to check if the tab is in focus
        return self.notebook.select() == str(self)

    def set_focus(self):
        app.cp_notebook.select(self)

    def is_visible(self):
        return self.module.is_visible()

    def is_enabled(self):
        return self.module.is_enabled()

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
        app.interface.focus()

    def get_widget_dict(self):
        return {k:self.widgets[k].get() for k in self.widgets}

    def load_config_value(self, name):
        return self.values.get(name, self.default.get(name, None))



    def enable(self):
        self.notebook.tab(self, state='normal')
        try:
            self.notebook.index(self.notebook.select())
        except:
            self.notebook.select(self)

    def disable(self):
        self.notebook.tab(self, state='disabled')

    def hide(self):
        self.notebook.tab(self, state='hidden')

    def select(self):
        self.notebook.select(self)
