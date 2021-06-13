import tkinter as Tk
from tkinter import ttk, font
from config import config
from utils import validation
class LabeledWidget():

    def __init__(self,
                 parent,
                 label,
                 value="",
                 default="",
                 command=None):
        self.parent = parent
        self.frame = Tk.Frame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        self.label = ttk.Label(self.frame, text=label)
        self.label.config(wraplength=config.label_width)
        self.label.bind('<Configure>',self.adjust_width)

        self.var = Tk.StringVar()
        self.var.set(value)
        self.default = default
        self.prev = value
        self.widget = None
        self.command=command

        self.label.grid(column=0, row=0, sticky='news')

    def get(self):
        return self.var.get()

    def get_default(self):
        return self.default

    def set(self, value=""):
        self.var.set(value)

    def set_to_default(self):
        self.set(self.default)

    def adjust_width(self, e):
        self.adjust_label_width()

    def adjust_label_width(self):
        self.label.config(wraplength=int(self.parent.winfo_width() - self.widget.winfo_width()))

    def adjust_widget_width(self):
        self.widget.config(width = int(self.parent.winfo_width() * config.relative_widget_width))



    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def revert(self):
        print('revert')
        self.set(self.prev)

    def is_int(self, value):
        if validatoin.is_int(value):
            self.prev = value
            return True
        else:
            self.set(self.prev)
            return False

    def is_float(self, value):
        if validation.is_float(value):
            self.prev = value
            return True
        else:
            # self.set(self.prev)
            return False

    def bind(self, command):
        try:
            self.widget.bind(command)
        except:
            pass

class LabeledEntry(LabeledWidget):
    def __init__(self,
                 parent,
                 label="Enter value",
                 value="default value",
                 default=None,
                 validate_type = "float",
                 command=None):
        LabeledWidget.__init__(
            self,
            parent,
            label,
            value,
            default,
            command
        )

        self.widget = Tk.Entry(
            self.frame,
            textvariable=self.var,
            validate='focus',
            width=config.entry_width,
            validatecommand=(self.frame.register(self.validate), validate_type, '%P'),
            justify=Tk.RIGHT
        )



        self.bind(command)

        self.widget.grid(column=1, row=0, sticky='sew')

    def set(self, value):
        #cannot use Tk.StringVar.set() due to validatecommand conflict
        self.widget.delete(0, len(self.get()))
        self.widget.insert(0, value)

    def validate(self, validate_type, value):
        if validate_type == 'float':
            if validation.is_float(value):
                self.prev = value
                return True
            self.revert()
            return False
        elif validate_type == 'int':
            if validation.is_int(value):
                self.prev = value
                return True
            try:
                new_value = int(float(value))
                self.set(new_value)
                self.prev = new_value
                return True
            except:
                self.revert()
                return False


class LabeledOptionMenu(LabeledWidget):
    def __init__(
            self,
            parent,
            label,
            value,
            default=None,
            options=[],
            command=None
    ):
        LabeledWidget.__init__(
            self,
            parent,
            label,
            value,
            default,
            command
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
        self.bind(command)
        self.widget.grid(column=1, row=0, sticky='ews')

    def replace_options(self, options=[]):
        self.widget.delete(0, 'end')
        for i in options:
            self.widget.add_command(
                label=i,
                command=self.command
            )


class LabeledCheckbox(LabeledWidget):
    def __init__(
            self,
            parent,
            label=None,
            value=None,
            default=None,
            command=None
    ):
        LabeledWidget.__init__(
            self,
            parent,
            label,
            value,
            default
        )
        self.widget = ttk.Checkbutton(
            self.frame,
            variable=self.var
        )
        if value is None:
            value = default
        self.set(value)

        self.bind(command)
        self.widget.grid(column=1, row=0, sticky='ews')