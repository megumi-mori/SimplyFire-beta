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
import os
import yaml
import importlib
from tkinter import BooleanVar, ttk
import tkinter as Tk
from simplyfire import app
import inspect
from threading import Thread

class BaseModule():
    def __init__(self,
                 name:str,
                 menu_label:str,
                 tab_label:str,
                 filename:str = None,
                 menu_target=app.menubar.module_menu,
                 file_menu:bool=False
                 ):
        filename = inspect.getfile(self.__class__)
        self.widgets = {}
        try:
            with open(os.path.join(os.path.dirname(filename), 'default_values.yaml'), 'r') as f:
                self.defaults = yaml.safe_load(f)
        except:
            self.defaults = {}

        try:
            with open(os.path.join(os.path.dirname(filename), 'config.yaml'), 'r') as f:
                self.config = yaml.safe_load(f)
        except:
                self.config = {}

        try:
            self.values = app.config.user_vars[name]
        except:
            self.values = {}

        self.name = name
        self.menu_label = menu_label
        self.tab_label = tab_label
        self.menu_var = BooleanVar(value=False)
        self.disable_stack = []

        menu_target.add_checkbutton(label=self.menu_label,
                                                command=self.toggle_module_display,
                                                variable=self.menu_var,
                                                onvalue=True,
                                                offvalue=False)

        self.file_menu = None
        if file_menu:
            self.file_menu = self.create_file_menu_cascade() #expand this later


        self._load_components()
        self._load_binding()


    def toggle_module_display(self, event=None, undo=True):
        if self.menu_var.get():
            self.show_tab()
            if not self.disable_stack:
                self.select()
        else:
            self.hide()

        if undo and app.interface.is_accepting_undo():
            app.interface.add_undo([
                lambda v=not self.menu_var.get(): self.menu_var.set(v),
                lambda u=False: self.toggle_module_display(undo=u)]
            )

    def update_module_display(self, event=None):
        if self.menu_var.get(): # menu checkbutton is ON
            self.show_tab()
        else:
            self.hide()

    def show_tab(self, event=None):
        if not self.disable_stack:
            for c in self.children:
                c.enable()
        else:
            for c in self.children:
                c.disable()

    def select(self, event=None):
        for c in self.children:
            try:
                c.select()
            except:
                pass

    def _add_disable(self, event=None, source:str=None):
        if not source:
            source = self.name
        if source not in self.disable_stack:
            self.disable_stack.append(source)
        self.update_module_display()

    def force_enable(self, event=None):
        self.disable_stack = []
        self.update_module_display()

    def _remove_disable(self, event=None, source:str=None):
        if not source:
            source = self.name
        try:
            self.disable_stack.remove(source)
        except ValueError:
            self._error_log(f'{source} is not part of the disable stack')
        self.update_module_display()

    def disable_module(self, event=None, modulename=None):
        if not modulename:
            self._add_disable()
        else:
            app.modules_dict[modulename]._add_disable(source=self.name)

    def enable_module(self, event=None, modulename=None):
        if not modulename:
            self._remove_disable()
        else:
            app.modules_dict[modulename]._remove_disable(source=self.name)

    def is_visible(self):
        return self.menu_var.get()

    def is_enabled(self):
        return not self.disable_stack


    def hide(self, event=None):
        for c in self.children:
            c.hide()

    def select(self, event=None):
        for c in self.children:
            try:
                c.select()
            except:
                pass

    def _error_log(self, msg):
        # connect to log later
        pass

    def _load_components(self):
        component_dict = self.config.get('GUI_components', None)
        if not component_dict:
            return
        # make empty components:
        self.control_tab = None
        self.data_tab = None
        self.popup_list = []
        self.children = []
        for component, object in component_dict.items(): # 'py file name': {dict of details}
            module_py = importlib.import_module(f'simplyfire.modules.{self.name}.{component}')
            # try:
            tab = getattr(module_py, object, None)(self)
            if tab.name:
                setattr(self, tab.name, tab)
            self.children.append(tab)
            # except Exception as e:
            #     print(f'{self.name}, {e}')
            #     pass
                # if details['location'] == 'control_panel':
                #     module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                #     # try:
                #     tab = getattr(module_py, 'ModuleControl', None)(self)
                #     if tab.name:
                #         setattr(self, tab.name, tab)
                #     self.children.append(tab)
                #     # except TypeError:
                #     #     self._error_log(f'component {component} does not have attribute ModuleControl')
                # elif details['location'] == 'data_notebook':
                #     module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                #     try:
                #         tab = getattr(module_py, 'ModuleDataTable', None)(self)
                #         if tab.name:
                #             setattr(self, tab.name, tab)
                #         self.children.append(self.data_tab)
                #     except TypeError:
                #         self._error_log(f'component {component} does not have attribute ModuleTable')
                #         pass
                # elif details['location'] == 'popup':
                #     module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                #     try:
                #         self.popup_list.append(getattr(module_py, 'ModulePopup', None)(self))
                #         self.children.append(self.popup_list[-1])
                #         if self.popup_list[-1].name:
                #             setattr(self, self.popup_list[-1].name, self.popup_list[-1])
                #     except TypeError:
                #         self._error_log(f'component {component} does not have attribute ModulePopup')
                #         pass



    def create_menubar_cascade(self, target):
        menu = Tk.Menu(target, tearoff=0)
        target.add_cascade(label=self.menu_label, menu=menu)
        return menu

    def add_file_menu_command(self, **kwargs):
        if self.file_menu is None:
            self.create_file_menu_cascade()
        self.file_menu.add_command(**kwargs)
        pass

    def create_file_menu_cascade(self):
        if self.file_menu is None:
            self.file_menu = self.create_menubar_cascade(app.menubar.file_menu)
        return self.file_menu

    def log(self, msg, header=True):
        if header:
            app.log_display.log(f'{self.name}: {msg}', True)
        else:
            app.log_display.log(msg, False)

    def add_undo(self, tasks):
        assert not isinstance(tasks, str)
        tasks.insert(0, self.select)
        app.interface.add_undo(tasks)

    def start_thread(self, target_func, target_interrupt, popup=True):
        t = Thread(target=target_func)
        t.start()
        if popup:
            return self.show_interrupt_popup(target_interrupt)


    def show_interrupt_popup(self, target_interrupt):
        self.popup_window = Tk.Toplevel(app.root)
        app.root.attributes('-disabled', True)
        def disable():
            pass
        self.popup_window.protocol('WM_DELETE_WINDOW', disable)
        label = ttk.Label(master=self.popup_window, text='Running analysis. Press STOP to interrupt')
        label.pack()
        button = ttk.Button(master=self.popup_window, text='STOP', command=lambda t=target_interrupt:self.destroy_interrupt_popup(t))
        button.pack()
        return self.popup_window

    def destroy_interrupt_popup(self, target_interrupt=None):
        if target_interrupt:
            target_interrupt.stop=True
        app.root.attributes('-disabled', False)
        self.popup_window.destroy()
    def _load_binding(self):
        pass

    def create_batch_category(self):
        app.batch_popup.insert_command_category(self.menu_label)

    def add_batch_command(self, name, func, interrupt=None):
        app.batch_popup.insert_command(name, self.menu_label, lambda f=func: self._batch_command_decorator(f), interrupt=interrupt)

    def _batch_command_decorator(self, func):
        if not self.is_enabled():
            app.batch_popup.batch_log.insert(f'WARNING: {self.menu_label} is not enabled. Command not executed.')
            return
        func()

    def call_if_enabled(self, func):
        if self.is_enabled():
            func()
    def call_if_visible(self, func):
        if self.is_visible():
            func()
    def listen_to_event(self, event:str, function, condition:str=None, target=app.root):
        if condition == 'focused':
            raise AssertionError(f'"focused" is not a valid condition at the {type(self)} level.')
        assert condition in {'enabled', 'visible', None}, 'condition must be None, "enabled", or "visible"'
        assert callable(function), f'{function} is not callable'

        if condition is None:
            target.bind(event, lambda e:function(), add="+")
        elif condition == 'enabled':
            target.bind(event, lambda e, f=function:self.call_if_enabled(f), add='+')
        elif condition == 'visible':
            target.bind(event, lambda e, f=function: self.call_if_visible(f), add='+')