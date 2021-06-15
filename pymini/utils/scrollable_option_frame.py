from utils.scrollable_frame import ScrollableFrame
import tkinter as Tk
from tkinter import ttk
from utils import widget
from config import config
import yaml

class ScrollableOptionFrame():
    def __init__(self, parent, scrollbar=True):
        self.container = Tk.Frame(parent, bg='red')
        self.canvas = Tk.Canvas(self.container, bg='orange')
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.frame = Tk.Frame(self.canvas, bg='green')

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        self.canvas.create_window((0, 0), window=self.frame, anchor='nw', tag='option')

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.container.grid(column=0, row=0, sticky='news')
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.canvas.grid(column=0, row=0, sticky='news')
        self.canvas.grid_columnconfigure(0, weight=1)
        self.canvas.grid_rowconfigure(0, weight=1)
        if scrollbar:
            self.scrollbar.grid(column=2, row=0, sticky='ns')

        self.canvas.bind('<Configure>', self.adjust_width)

        # bind mousewheel
        # Windows only for now:
        self.frame.bind('<Enter>', self._bind_mousewheel)
        self.frame.bind('<Leave>', self._unbind_mousewheel)

        # if not scrollbar:
        #     print('forget scrollbar')
        #     self.scrollbar.grid_forget()

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0,weight=1)
        self.widgets = {}
        self.buttons = {}
        self.num_row = 0
        self.col_button = 0
    def adjust_width(self, e):
        self.canvas.itemconfigure('option', width=e.width-4)
        pass

    def get_frame(self):
        return self.container

    def get_canvas(self):
        return self.canvas

    def _bind_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel')

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def insert_entry(self,
                     name,
                     label="Enter value",
                     value="default value",
                     default=None,
                     validate_type=None,
                     command=None
                     ):
        """
        :param name: name used to store the widget for later retrieval
        :param label: Text used as the label describing the widget
        :param value: Value of the Entry widget
        :param default: Default value of the Entry widget
        :param validate_type: Text validation type supports ("int", "float", "auto", "color").
        To allow for multiple validation types, separate type by "/"
        :param command: command linked to the Entry widget (currently not supported)
        :return:
        """
        panel = Tk.Frame(self.frame)
        panel.grid_columnconfigure(0, weight=1)

        w = widget.LabeledEntry(
            parent=panel,
            name=name,
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
            name=name,
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
            name=name,
            label=label,
            value=value,
            default=default,
            command=command
        )

        w.grid(column=0, row=0, stick='news')
        self.widgets[name] = w

        self.insert_panel(panel)
        return w

    def insert_frame(
            self,
            name="",
    ):
        panel = Tk.Frame(self.frame)
        self.insert_panel(panel)
        return panel

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

        button.config(wraplength=button.winfo_width() - 4)
    def default(self):
        for key in self.widgets:
            self.widgets[key].set_to_default()

    def update_width(self, fontsize):
        print('update_width')
        for key in self.widgets:
            self.widgets[key].set_wraplength(fontsize / 9 * config.label_length)
        for key in self.buttons:
            self.buttons[key].config(wraplength = self.buttons[key].winfo_width() - 4)

    def get_value(self, key):
        return self.widgets[key].get()

    def safe_dump_vars(self):
        vars = [(key, self.widgets[key].get()) for key in self.widgets]
        d = dict(vars)
        return yaml.safe_dump(d)
