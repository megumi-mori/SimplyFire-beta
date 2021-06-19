import tkinter as Tk
from tkinter import ttk, font
from config import config
from utils import validation
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

import textwrap
import pymini

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

class LinkedWidget():
    """
    This is a parent class for making modified tkinter widgets
    The modified widget allows for easy getter and setter access to the Tk.StringVar associated with the widget
    The widget can store a default value
    The widget can revert to the previously accepted value if the validation does not return True
    """
    def __init__(
            self,
            parent,
            name,
            value="",
            default=""
    ):
        self.parent = parent
        self.name = name
        self.var = Tk.StringVar()
        self.var.set(value)
        self.default = default
        self.prev = value
        self.widget = None

    def get(self):
        return self.var.get()

    def get_widget(self):
        return self.widget

    def set(self, value):
        self.var.set(value)
        self.prev = value

    def get_default(self):
        return self.default

    def set_to_default(self):
        self.set(self.default)

    def revert(self):
        self.set(self.prev)

    def grid(self, *args, **kargs):
        self.widget.grid(*args, **kargs)




class LinkedEntry(LinkedWidget):
    def __init__(
            self,
            parent,
            name="",
            value="",
            default="",
            validate_type=""
        ):
        super().__init__(parent, name, value, default)
        self.widget = Tk.Entry(
            master=parent,
            textvariable=self.var,
            width=config.entry_width,
            justify=Tk.RIGHT
        )
        self.widget.bind('<FocusOut>', lambda e, v=validate_type: self.validate(e, v))
        self.widget.bind('<Return>', lambda e, v=validate_type: self.validate(e, v), add="+")

    def set(self, value=""):
        # cannot use Tk.StringVar.set() due to validatecommand conflict
        self.widget.delete(0, len(self.get()))
        self.widget.insert(0, value)

    def validate(self, event, validation_type, c=None):
        print('validate')
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

class LinkedOptionMenu(LinkedWidget):
    def __init__(self, parent, name, value, default=None, options=None, command=None):
        super().__init__(parent, name, value, default)

        if options is None:
            options = []

        if value is None:
            value = default
            print("lom: {}, {}".format(value, default))

        self.command = command
        self.widget = ttk.OptionMenu(
            parent,
            self.var,
            value,
            *options,
            command=command
        )

    def replace_options(self, options=None):
        if options is None:
            options = []
        self.widget['menu'].delete(0, 'end')
        for i in options:
            self.widget['menu'].add_command(
                label=i,
                command=self.command
            )

class LinkedText(LinkedWidget):
    def __init__(self,
            parent,
            name="",
            value="",
            default=""
                 ):
        super().__init__(parent=parent,
                         name=name,
                         value=value,
                         default=default)
        self.widget = Tk.Text(master=parent)
        self.set(value)

    def set(self, value):
        disable = False
        if self.widget['state'] == 'disabled':
            disable = True
            self.widget.config(state='normal')
        self.widget.delete(1.0, Tk.END)
        self.widget.insert(1.0, value)
        self.var.set(value)
        if disable:
            self.widget.config(state='disabled')

class LinkedScale(LinkedWidget):
    def __init__(self,
                 parent,
                 name="",
                 value="",
                 default='',
                 from_=0,
                 to=100,
                 orient=Tk.VERTICAL,
                 command=None):
        super().__init__(parent=parent,
                         name=name,
                         value="",
                         default=""
                         )
        self.var = Tk.DoubleVar()
        self.widget = ttk.Scale(master=parent,
                                 variable=self.var,
                                 from_=from_,
                                 to=to,
                                 orient=orient,
                                 command=command)





class LabeledWidget():
    def __init__(self,
                 parent,
                 name,
                 label,
                 value="",
                 default="",
                 command=None):
        self.parent = parent
        self.name = name
        self.frame = Tk.Frame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        # Format the label text - wrap text according to specified length
        wrapped_label = textwrap.wrap(label, width=config.default_label_length)
        text = '\n'.join(wrapped_label)
        self.label = ttk.Label(self.frame, text=text)

        # self.label.config(width=20)
        # self.label.bind('<Configure>', self.adjust_width)

        self.var = Tk.StringVar()
        self.var.set(value)
        self.default = default
        self.prev = value
        self.widget = None
        self.command = command

        self.label.grid(column=0, row=0, sticky='news')

    def get(self):
        return self.var.get()

    def get_default(self):
        return self.default

    def set(self, value=""):
        self.var.set(value)

    def set_to_default(self):
        self.set(self.default)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def revert(self):
        print('revert')
        self.set(self.prev)

    def get_widget(self):
        return self.widget


    def bind(self, command):
        try:
            self.widget.bind(command)
        except:
            pass


class LabeledEntry(LabeledWidget):
    def __init__(self,
                 parent,
                 name=None,
                 label="Enter value",
                 value="default value",
                 default=None,
                 validate_type="float",
                 command=None):
        LabeledWidget.__init__(
            self,
            parent,
            name,
            label,
            value,
            default,
        )

        self.widget = Tk.Entry(
            self.frame,
            textvariable=self.var,
            width=config.entry_width,
            justify=Tk.RIGHT,
            command=command
        )

        self.widget.grid(column=1, row=0, sticky='sew')
        self.widget.bind('<FocusOut>', lambda e, v=validate_type: self.validate(e, v), add='+')
        self.widget.bind('<Return>', lambda e, v=validate_type: self.validate(e, v), add="+")

    def set(self, value=""):
        # cannot use Tk.StringVar.set() due to validatecommand conflict
        self.widget.delete(0, len(self.get()))
        self.widget.insert(0, value)

    def validate(self, event, validation_type, c=None):
        value = self.get()
        if validation.validate(validation_type, self.get()):
            self.prev = value
            return True
        elif validation_type == 'int':
            try:
                new_value = str(int(float(value)))
                self.set(new_value)
                self.prev = new_value
                return True
            except:
                self.revert()
                return False
        else:
            self.revert()
            return False


class LabeledOptionMenu(LabeledWidget):
    def __init__(
            self,
            parent,
            name=None,
            label="",
            value="",
            default=None,
            options=[],
            command=None
    ):
        LabeledWidget.__init__(
            self,
            parent,
            name=name,
            label=label,
            value=value,
            default=default
        )

        if value is None:
            value = default

        self.widget = ttk.OptionMenu(
            self.frame,
            self.var,
            value,
            *options,
            command=command
        )
        self.command=command
        # self.widget.bind('<FocusOut>', self.test, add='+')
        self.widget.grid(column=1, row=0, sticky='ews')
        self.widget.replace_options = self.replace_options
        self.widget.clear_options = self.clear_options
        self.widget.add_option = self.add_option

    def clear_options(self):
        self.widget['menu'].delete(0, 'end')
    def add_option(self, *args, **kwargs):
        self.widget['menu'].add_command(*args, **kwargs)
    def replace_options(self, options):
        print('replace option')
        self.widget['menu'].delete(0, 'end')
        try:
            for i in options:
                self.widget['menu'].add_command(i)
            self.set(options[0])
        except:
            pass

    def test(self, event=None):
        print('testing')


class LabeledCheckbox(LabeledWidget):
    def __init__(
            self,
            parent,
            name=None,
            label=None,
            value=None,
            default=None,
            command=None
    ):
        LabeledWidget.__init__(
            self,
            parent,
            name,
            label,
            value,
            default,
        )
        self.widget = ttk.Checkbutton(
            self.frame,
            variable=self.var,
            command=command
        )
        if value is None:
            value = default
        self.set(value)

        self.bind(command)
        self.widget.grid(column=1, row=0, sticky='ews')

class NavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        self.toolitems = [t for t in self.toolitems if t[0] in ('Pan', 'Zoom', 'Save')]
        NavigationToolbar2Tk.__init__(self, canvas, parent)



