import os
import yaml
import importlib
from tkinter import BooleanVar
from PyMini import app
class BaseModule():
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
        self.menu_var = BooleanVar(value=False)
        self.disable_stack = []

        self._load_components()

        app.menubar.window_menu.add_checkbutton(label=self.menu_label,
                                                command=self.toggle_module_display,
                                                variable=self.menu_var,
                                                onvalue=True,
                                                offvalue=False)

    def toggle_module_display(self, event=None):
        if self.menu_var.get():
            self.show_tab()
            if not self.disable_stack:
                self.select()
        else:
            self.hide()

    def update_module_display(self, event=None):
        if self.menu_var.get(): # menu checkbutton is ON
            self.show_tab()
        else:
            self.hide()

    def show_tab(self, event=None):
        try:
            current_tab = app.cp_notebook.index(app.cp_notebook.select())
        except:
            current_tab = None
        print(f'showing tab for {self.name}: {self.disable_stack}')
        if not self.disable_stack:
            if self.control_tab:
                app.config_cp_tab(self.control_tab, state='normal')
            if self.data_tab:
                app.config_data_tab(self.data_tab, state='normal')
                print(self.name)
                self.data_tab.fit_columns()
        else:
            if self.control_tab:
                app.config_cp_tab(self.control_tab, state='disabled')
            if self.data_tab:
                app.config_data_tab(self.data_tab, state='disabled')
        try:
            app.cp_notebook.select(current_tab)
        except:
            pass

    def _disable(self, event=None, source:str=None):
        source = self.name
        if source not in self.disable_stack:
            self.disable_stack.append(source)
        print(f'_disable was called for {self.name}: {self.disable_stack}')
        self.update_module_display()

    def force_enable(self):
        self.disable_stack = []
        self.update_module_display()

    def _enable(self, event=None, source:str=None):
        source = self.name
        try:
            self.disable_stack.remove(source)
        except ValueError:
            self._error_log(f'{source} is not part of the disable stack')
        print(f'_enable was called for {self.name}: {self.disable_stack}')
        self.update_module_display()

    def disable_module(self, modulename):
        app.modules_dict[modulename]._disable(source=self.name)

    def enable_module(self, modulename):
        app.modules_dict[modulename]._enable(source=self.name)
    def is_visible(self):
        return self.menu_var.get()

    def is_enabled(self):
        return self.is_visible() and not self.disable_stack


    def hide(self, event=None):
        if self.control_tab:
            app.config_cp_tab(self.control_tab, state='hidden')
        if self.data_tab:
            app.config_data_tab(self.data_tab, state='hidden')

    def select(self, event=None):
        if self.control_tab:
            app.cp_notebook.select(self.control_tab)
        if self.data_tab:
            app.data_notebook.select(self.data_tab)

    def _error_log(self, msg):
        # connect to log later
        print(f'module load error: {msg}')

    def _load_components(self):
        component_dict = self.config.get('GUI_components', None)
        if not component_dict:
            return
        # make empty components:
        self.control_tab = None
        self.data_tab = None
        for component, details in component_dict.items(): # 'py file name': {dict of details}
            if details['location'] == 'control_panel':
                module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                # try:
                self.control_tab = getattr(module_py, 'ModuleControl', None)(self)
                # except TypeError:
                #     self._error_log(f'component {component} does not have attribute ModuleControl')
            elif details['location'] == 'data_notebook':
                module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
                try:
                    self.data_tab = getattr(module_py, 'ModuleTable', None)(self)
                except TypeError:
                    self._error_log(f'component {component} does not have attribute ModuleTable')
                    pass


    def insert_file_menu(self):
        self.file_menu = Tk.Menu(app.menubar.file_menu, tearoff=0)
        app.menubar.file_menu.add_cascade(label=self.name, menu=self.file_menu)
