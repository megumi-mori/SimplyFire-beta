import os
import yaml
import importlib
from tkinter import BooleanVar
from PyMini import app
class BaseParentModule():
    def __init__(self,
                 name:str,
                 menu_label:str,
                 tab_label:str,
                 filename:__file__,
                 ):
        try:
            with open(os.path.join(os.path.dirname(filename), 'default_values.yaml'), 'r') as f:
                self.default = yaml.safe_load(f)
        except:
            self.default = {}

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
        self.menu_var = BooleanVar()
        self.disable_stack = []

        self._load_components()

        app.menubar.window_menu.add_checkbutton(label=self.menu_label,
                                                command=self.update_module_display,
                                                variable=self.menu_var,
                                                onvalue=True,
                                                offvalue=False)


    def update_module_display(self, event=None):
        if self.menu_var.get(): # menu checkbutton is ON
            self.show_tab()
            if not self.disable_stack:
                self.select()
        else:
            self.hide_tab()

    def show_tab(self, event=None):
        if not self.disable_stack:
            if self.control_tab:
                app.config_cp_tab(self.control_tab, state='normal')
            if self.data_tab:
                app.config_data_tab(self.data_tab, state='normal')
        else:
            if self.control_tab:
                app.config_cp_tab(self.control_tab, state='disabled')
            if self.data_tab:
                app.config_data_tab(self.data_tab, state='disabled')

    def disable_tab(self, source:str):
        if source not in self.disable_stack:
            self.disable_stack.append(source)
        self.update_module_display()

    def force_enable_tab(self):
        self.disable_stack = []
        self.update_module_display()

    def enable_tab(self, source:str):
        try:
            self.disable_stack.remove(source)
        except ValueError:
            self._error_log(f'{source} is not part of the disable stack')
        self.update_module_display()

    def is_visible(self):
        return self.menu_var.get()

    def is_enabled(self):
        return self.is_visible() and not self.disable_stack


    def hide_tab(self, event=None):
        if self.control_tab:
            app.config_cp_tab(self.control_tab, state='hidden')
        if self.data_tab:
            app.config_data_tab(self.data_tab, state='hidden')

    def _error_log(self, msg):
        # connect to log later
        print(f'module load error: {msg}')

    def _load_components(self):
        component_dict = self.config.get('GUI_components', None)
        if not component_dict:
            return
        # make empty components:
        self.control_tab = None
        self.table_tab = None
        for component, details in component_dict.items(): # 'py file name': {dict of details}
            if details['location'] == 'control_panel':
                module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                # try:
                self.control_tab = getattr(module_py, 'ModuleControl', None)(self)
                # except TypeError:
                #     self._error_log(f'component {component} does not have attribute ModuleControl')
            elif details['location'] == 'data_notebook':
                module_py = importlib.import_module(f'{self.name}.{component}', package='Modules')
                try:
                    self.data_tab = getattr(module_py, 'ModuleTable', None)(self)
                except TypeError:
                    self._error_log(f'component {component} does not have attribute ModuleTable')
                    pass


