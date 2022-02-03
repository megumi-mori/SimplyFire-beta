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
                 menu_target=app.menubar.window_menu
                 ):
        self.widgets = {}
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

        menu_target.add_checkbutton(label=self.menu_label,
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
        set_to_self = False
        if not self.disable_stack:
            for c in self.children:
                c.enable()
        else:
            for c in self.children:
                c.disable()

    def _disable(self, event=None, source:str=None):
        source = self.name
        if source not in self.disable_stack:
            self.disable_stack.append(source)
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
        self.update_module_display()

    def disable_module(self, modulename):
        app.modules_dict[modulename]._disable(source=self.name)

    def enable_module(self, modulename):
        app.modules_dict[modulename]._enable(source=self.name)
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
                c.notebook.select(c)
            except:
                pass

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
        self.popup_list = []
        self.children = []
        for component, object in component_dict.items(): # 'py file name': {dict of details}
            module_py = importlib.import_module(f'PyMini.Modules.{self.name}.{component}')
            try:
                tab = getattr(module_py, object, None)(self)
                if tab.name:
                    setattr(self, tab.name, tab)
                self.children.append(tab)
            except:
                pass
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



    def insert_file_menu(self):
        self.file_menu = Tk.Menu(app.menubar.file_menu, tearoff=0)
        app.menubar.file_menu.add_cascade(label=self.name, menu=self.file_menu)

    def log(self, msg, header=True):
        if header:
            app.log_display.log(f'{self.name}: {msg}', True)
        else:
            app.log_display.log(msg, False)

    def add_undo(self, tasks):
        assert not isinstance(tasks, str)
        tasks.insert(0, self.select)
        app.interface.add_undo(tasks)