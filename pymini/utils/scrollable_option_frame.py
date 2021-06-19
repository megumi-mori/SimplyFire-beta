from utils.scrollable_frame import ScrollableFrame
import tkinter as Tk
from tkinter import ttk
from utils import widget
from config import config
import yaml
import textwrap

from functools import wraps


def make_label(
        parent,
        name,
        label
):

    wrapped_label = textwrap.wrap(label, width=config.default_label_length)
    text = '\n'.join(wrapped_label)
    label = ttk.Label(parent, text=text)

    return label


class ScrollableOptionFrame(Tk.Frame):
    def __init__(self, parent, scrollbar=True):
        super().__init__(parent)
        # self.container = Tk.Frame(parent, bg='red')
        self.scrollbar = scrollbar

        if scrollbar:
            self.canvas = Tk.Canvas(self)
            self.frame = Tk.Frame(self.canvas, bg='green')

            self.frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(
                    scrollregion=self.canvas.bbox('all')
                )
            )

            self.canvas.create_window((0, 0), window=self.frame, anchor='nw', tag='option')

            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            self.canvas.grid(column=0, row=0, sticky='news')
            self.canvas.grid_columnconfigure(0, weight=1)
            self.canvas.grid_rowconfigure(0, weight=1)

            self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.scrollbar.grid(column=2, row=0, sticky='ns')

            self.canvas.bind('<Configure>', self.adjust_width)

            # bind mousewheel
            # Windows only for now:
            self.frame.bind('<Enter>', self._bind_mousewheel)
            self.frame.bind('<Leave>', self._unbind_mousewheel)

            self.frame.grid_columnconfigure(0, weight=1)
            # self.frame.grid_rowconfigure(0,weight=1)
        else:
            self.frame = Tk.Frame(self)
            self.frame.grid(column=0, row=0, sticky='news')
            self.frame.grid_columnconfigure(0, weight=1)

        self.widgets = {}
        self.buttons = {}
        self.labels = {}
        self.titles = {}
        self.variables = {}
        self.num_row = 0
        self.col_button = 0

    def adjust_width(self, e):
        self.canvas.itemconfigure('option', width=e.width-4)
        pass

    def get_frame(self):
        if scrollable:
            return self.frame
        else:
            return self

    def _bind_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel')

    def _on_mousewheel(self, event):
        if self.frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def get_widget(self, name):
        return self.widgets[name].get_widget()

    def insert_label_widget(func):
        def call(
                self,
                name,
                label="",
                value="",
                default="",
                validate_type="",
                *args,
                **kwargs
        ):
            panel = self.make_panel(separator=config.default_separator)
            frame = ttk.Frame(panel)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            wrapped_label = textwrap.wrap(label, width=config.default_label_length)
            text='\n'.join(wrapped_label)
            self.labels[name] = ttk.Label(frame, text=text)
            self.labels[name].grid(column=0, row=0, sticky='news')
            frame.grid(column=0,row=0, sticky='news')
            w = func(self, parent=frame, value=value, default=default, *args, **kwargs)
            self.widgets[name] = w
        return call
    #
    @insert_label_widget
    def insert_label_entry(
            self,
            parent,
            value,
            default,
            validate_type=None

    ):
        w = widget.VarEntry(
            parent=parent,
            value=value,
            default=default,
            validate_type=validate_type
        )
        w.grid(column=1, row=0, sticky='ews')

        return w

    @insert_label_widget
    def insert_label_optionmenu(
            self,
            parent,
            value=None,
            default='',
            options=None,
            command=None,
            **kwargs
    ):
        w = widget.VarOptionmenu(
            parent=parent,
            value=value,
            default=default,
            options=options,
            command=command,
            **kwargs

        )
        w.grid(column=1, row=0, sticky='news')
        return w

    @insert_label_widget
    def insert_label_checkbox(
            self,
            parent,
            value=None,
            default=None,
            command=None,
            **kwargs
    ):
        w = widget.VarCheckbutton(
            parent=parent,
            value=value,
            default=default,
            command=command,
            **kwargs
        )
        w.grid(column=1, row=0, sticky='news')
        return w

    def insert_checkbox(
            self,
            name,
            label="Label",
            default=None,
            value=None,
            command=None
    ):
        panel = self.make_panel(separator=config.default_separator)
        w = widget.LabeledCheckbox(
            parent=panel,
            name=name,
            label=label,
            value=value,
            default=default,
            command=command
        )
        w.grid(column=0, row=0, stick='news')
        self.widgets[name] = w
        return w

    def insert_title(
            self,
            name="",
            text=""
    ):
        panel = self.make_panel(separator=config.default_separator)
        label = Tk.Label(panel, text=text, justify=Tk.CENTER, font='bold')
        self.titles[name] = label
        label.grid(column=0, row=0, sticky='news')






    def make_panel(
            self,
            separator=True
    ):
        panel = Tk.Frame(self.frame)
        panel.grid_columnconfigure(0, weight=1)
        self.insert_panel(panel, separator)
        return panel

    def insert_panel(self, frame, separator=True):
        frame.grid(row=self.num_row, column=0,sticky='news')
        if separator:
            separator = ttk.Separator(frame, orient='horizontal')
            separator.grid(column=0, row=1, sticky='news')
        self.num_row += 1
        self.col_button = 0

    def insert_separator(self):

        ttk.Separator(self.frame, orient='horizontal').grid(row=self.num_row, column=0, sticky='news')

        self.num_row += 1
        self.col_button = 0

    def isolate_button(self):
        self.col_button = 0

    def insert_button(
            self,
            text="",
            command=None,

    ):
        if self.col_button > 0:
            panel = self.frame.children['!frame{}'.format(self.num_row)]
            panel.grid_columnconfigure(1, weight=1)
            row = self.num_row - 1
        else:
            panel = Tk.Frame(self.frame)
            panel.grid_columnconfigure(0, weight=1)

            row = self.num_row
        b = Tk.Button(
            panel,
            text=text,
            command=command,
            # wraplength=85
        )
        b.configure()
        b.bind('<Configure>', lambda e, c = b:self.adjust_button_width(c))

        b.grid(column=self.col_button, row=0, sticky='news')

        self.buttons[text] = b

        if self.col_button > 0:
            self.col_button = 0
        else:
            panel.grid(column=0, row=row, sticky='news')
            self.num_row += 1
            self.col_button += 1
        pass

    def adjust_button_width(self, button):
        width = self.canvas.winfo_width()
        button.config(width=int(width/2), wraplength= int(width / 2) - 4)

    def default(self, keys=None):
        if keys is None:
            keys = self.widgets.keys()
        for key in keys:
            self.widgets[key].set_to_default()

    def get_value(self, key):
        return self.widgets[key].get()

    def set_value(self, key, value):
        self.widgets[key].set(value)

    def safe_dump_vars(self):
        vars = [(key, self.widgets[key].get()) for key in self.widgets]
        d = dict(vars)
        return yaml.safe_dump(d)
