from utils.scrollable_frame import ScrollableFrame
import tkinter as Tk
from tkinter import ttk
from utils import widget
from config import config

class ScrollableOptionFrame(ScrollableFrame):
    def __init__(self, parent, scrollbar=True):
        super().__init__(parent)

        if not scrollbar:
            print('forget scrollbar')
            self.scrollbar.grid_forget()

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0,weight=1)
        self.widgets = {}
        self.num_row = 0
        self.col_button = 0

    def insert_entry(self,
                     name,
                     label="Enter value",
                     value="default value",
                     default=None,
                     validate_type=None,
                     command=None
                     ):
        panel = Tk.Frame(self.frame)
        panel.grid_columnconfigure(0, weight=1)

        w = widget.LabeledEntry(
            parent=panel,
            label=label,
            value=value,
            default=default,
            validate_type=validate_type,
            command=command)
        w.grid(column=0, row=0, stick='news')
        self.widgets[name] = w

        self.insert_panel(panel)
        return w

    def insert_optionmenu(
            self,
            name,
            label="Label",
            default=None,
            value=None,
            options=[],
            command=None
    ):
        panel = Tk.Frame(self.frame)
        panel.grid_columnconfigure(0, weight=1)

        w = widget.LabeledOptionMenu(
            parent=panel,
            label=label,
            value=value,
            default=default,
            options=options,
            command=command
        )

        w.grid(column=0, row=0, stick='news')
        self.widgets[name] = w

        self.insert_panel(panel)
        return w

    def insert_checkbox(
            self,
            name,
            label="Label",
            default=None,
            value=None,
            command=None
    ):
        panel = Tk.Frame(self.frame)
        panel.grid_columnconfigure(0, weight=1)

        w = widget.LabeledCheckbox(
            parent=panel,
            label=label,
            value=value,
            default=default,
            command=command
        )

        w.grid(column=0, row=0, stick='news')
        self.widgets[name] = w

        self.insert_panel(panel)
        return w

    def insert_panel(self, panel):
        panel.grid(row=self.num_row, column=0,sticky='news')
        if config.separator:
            separator = ttk.Separator(panel, orient='horizontal')
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
            wraplength=85
        )
        b.configure()

        b.grid(column=self.col_button, row=0, sticky='news')
        if self.col_button > 0:
            self.col_button = 0
        else:
            panel.grid(column=0, row=row, sticky='news')
            self.num_row += 1
            self.col_button += 1
        pass

    def default(self):
        for key in self.widgets:
            self.widgets[key].set_to_default()

    def update_width(self, fontsize):
        for key in self.widgets:
            self.widgets[key].set_wraplength(fontsize / 9 * config.label_length)





