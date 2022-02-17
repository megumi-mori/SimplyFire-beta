"""
simplyfire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tkinter

from simplyfire import app
from tkinter import BooleanVar, Frame
from simplyfire.utils.scrollable_option_frame import ScrollableOptionFrame, OptionFrame
from simplyfire.utils import custom_widgets
import yaml
import os
from tkinter import ttk
import tkinter as Tk
from simplyfire.utils.plugin_GUI import PluginGUI
from simplyfire.utils.plugin_controller import PluginController
class PluginForm(ScrollableOptionFrame, PluginGUI):
    def __init__(self,
                 plugin_controller:PluginController,
                 tab_label: str="",
                 scrollbar:bool=True,
                 notebook:ttk.Notebook=app.cp_notebook
                 ) -> None:
        ScrollableOptionFrame.__init__(self, app.root, scrollbar)
        PluginGUI.__init__(self, plugin_controller)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.insert_panel = self.frame.insert_panel
        self.make_panel = self.frame.make_panel
        self.insert_separator = self.frame.insert_separator
        self.insert_widget = self.frame.insert_widget

        self.notebook = notebook
        self.tab_label = tab_label
        if notebook:
            self.notebook.add(self, text=self.tab_label)
        self.parameters = {}

    def apply_parameters(self, undo=True):
        if undo and app.interface.is_accepting_undo():
            undo_params = {}
            for i in self.inputs.keys():
                try:
                    if self.parameters[i] != self.inputs[i].get():
                        undo_params[i] = self.parameters[i]
                except:
                    pass
            if len(undo_params.keys()) > 0:
                self.controller.add_undo([lambda p=undo_params: self.apply_undo(p)])
        self.parameters = {k:w.get() for k, w in self.inputs.items()}
        app.interface.focus()
    def apply_undo(self, params):
        for key, value in params.items():
            self.inputs[key].set(value)
        self.apply_parameters(undo=False)

    def insert_title(self, **kwargs):
        # title = self.optionframe.insert_title(**kwargs)
        title = self.frame.insert_title(**kwargs)
        try:
            self.inputs[kwargs['name']] = title
        except Exception as e:
            pass
        return title

    def insert_label_entry(self, **kwargs):
        if 'command' not in kwargs.keys():
            kwargs['command'] = self.apply_parameters
        entry = self.frame.insert_label_entry(**kwargs)
        entry.bind('<Return>', kwargs['command'], add="+")
        entry.bind('<FocusOut>', kwargs['command'], add="+")
        try:
            self.inputs[kwargs['name']] = entry
        except:
            pass
        return entry

    def insert_button(self, **kwargs):
        button = self.frame.insert_button(self, **kwargs)
        try:
            self.inputs[kwargs['name']] = button
        except:
            pass
        return button

    def insert_label_checkbox(self, **kwargs):
        if 'command' not in kwargs.keys():
            kwargs['command'] = self.apply_parameters
        checkbox = self.frame.insert_label_checkbox(**kwargs)
        try:
            self.inputs[kwargs['name']] = checkbox
        except:
            pass
        return checkbox

    def insert_label_optionmenu(self, **kwargs):
        if 'command' not in kwargs.keys():
            kwargs['command'] = self.apply_parameters
        optionmenu = self.frame.insert_label_optionmenu(**kwargs)
        try:
            self.inputs[kwargs['name']] = optionmenu
        except:
            pass

    def insert_StringVar(self, name):
        self.inputs[name] = Tk.StringVar(self, value=self.load_config_value(name))

    def make_entry(self, parent, **kwargs):
        # if 'value' not in kwargs.keys():
        #     kwargs['value'] = self.values.get(kwargs['name'], None)
        # if 'default' not in kwargs.keys():
        #     kwargs['default'] = self.defaults.get(kwargs['name'], None)
        self.inputs[kwargs['name']] = custom_widgets.VarEntry(parent=parent,
                                                               **kwargs)
        return self.inputs[kwargs['name']]

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
        return self.controller.is_visible()

    def is_enabled(self):
        return self.controller.is_enabled()

    def hide_widget(self, widgetname=None, target=None):
        if widgetname:
            target = self.inputs.get(widgetname, None)
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
            target = self.inputs.get(widgetname, None)
        if target is None:
            return
        if target is None:
            return
        try:
            target.base_frame.grid()
        except:
            target.grid()

    def set_to_default(self, filter="", undo=True):
        for k, v in self.inputs.items():
            if filter:
                if filter in k:
                    try:
                        self.inputs[k].set_to_default()
                    except:
                        pass
                    # self.inputs[k].set(self.defaults[k])
            else:
                # self.inputs[k].set_to_default()
                try:
                    self.inputs[k].set_to_default()
                except:
                    pass
        self.apply_parameters(undo=undo)
        app.interface.focus()

    def get_widget_dict(self):
        return {k:self.inputs[k].get() for k in self.inputs}

    def load_config_value(self, name):
        return self.values.get(name, self.defaults.get(name, None))



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
