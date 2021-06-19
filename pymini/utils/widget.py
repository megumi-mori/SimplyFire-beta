import tkinter as Tk
from tkinter import ttk, font
from config import config
from utils import validation
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class VarWidget():
    def __init__(
            self,
            parent,
            value="",
            default=""
    ):
        self.var = Tk.StringVar(parent)
        self.var.set(value)
        self.default=default

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def get_default(self):
        return self.default

    def set_to_default(self):
        self.set(self.default)

    def get_widget(self):
        return self

class VarEntry(VarWidget, Tk.Entry):
    def __init__(
            self,
            parent,
            value="",
            default="",
            validate_type=None
    ):
        self.prev = value
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        Tk.Entry.__init__(
            self,
            master=parent,
            textvariable=self.var,
            width=config.entry_width,
            justify=Tk.RIGHT
        )
        self.prev = value
        self.validate_type = validate_type
        self.bind('<FocusOut>', lambda e, v=validate_type: self.validate(e, v))
        self.bind('<Return>', lambda e, v=validate_type: self.validate(e, v), add="+")

    def revert(self):
        self.set(self.prev)

    def set(self, value=""):
        # cannot use Tk.StringVar.set() due to validatecommand conflict
        self.delete(0, len(self.get()))
        self.insert(0, value)
        print(value)

    def validate(self, event, validation_type, c=None):
        value = self.get()
        if validation.validate(validation_type, self.get()):
            self.prev = value
            return True
        elif validation_type == 'int':
            try:
                new_value = str(int(float(value)))
                self.set(new_value)
                return True
            except:
                self.revert()
                return False
        else:
            self.revert()
            return False


class VarOptionmenu(VarWidget, ttk.OptionMenu):
    def __init__(
            self,
            parent,
            value=None,
            default="",
            options=None,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        if options is None:
            options = []
        if value is None:
            value = default
        self.command = command
        ttk.OptionMenu.__init__(
            self,
            parent,
            self.var,
            value,
            *options,
            command=command,
            **kwargs
        )

    def replace_options(self, options=None):
        if options is None:
            options = []
        self['menu'].delete(0, 'end')
        for i in options:
            self['menu'].add_command(
                label=i,
                command=self.command
            )

    def clear_options(self):
        self['menu'].delete(0, 'end')

    def add_option(self, *args, **kwargs):
        self['menu'].add_command(*args, **kwargs)

class VarCheckbutton(VarWidget, ttk.Checkbutton):
    def __init__(
            self,
            parent,
            value=None,
            default=None,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default

        )
        ttk.Checkbutton.__init__(
            self,
            master=parent,
            variable=self.var,
            command=command,
            **kwargs
        )

class VarText(VarWidget, Tk.Text):
    def __init__(
            self,
            parent,
            name="",
            value="",
            default=""
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        Tk.Text.__init__(
            self,
            master=parent,
        )
        self.set(value)

    def set(self, value):
        disable = False
        if self['state'] == 'disabled':
            disable = True
            self.config(state='normal')
        self.delete(1.0, Tk.END)
        self.insert(1.0, value)
        self.var.set(value)
        if disable:
            self.config(state='disabled')

class VarScale(VarWidget, ttk.Scale):
    def __init__(
            self,
            parent,
            value="",
            default="",
            from_=100,
            to=100,
            orient=Tk.VERTICAL,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        ttk.Scale.__init__(
            self,
            master=parent,
            variable=self.var,
            from_=from_,
            to=to,
            orient=orient,
            command=command,
            **kwargs
        )

class NavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        self.toolitems = [t for t in self.toolitems if t[0] in ('Pan', 'Zoom', 'Save')]
        NavigationToolbar2Tk.__init__(self, canvas, parent)



