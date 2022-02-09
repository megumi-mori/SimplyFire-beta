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
# from utils.scrollable_frame import ScrollableFrame
import tkinter as Tk
from tkinter import ttk
from simplyfire.utils import custom_widgets
from simplyfire.config import config
import yaml
import textwrap
from simplyfire.backend import interface


from functools import wraps

class OptionFrame(Tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.num_row = 0
        self.col_button = 0
        self.num_frames = 0

    def insert_label_widget_panel(self, frame, name, separator=True):
        """
        Inserts a frame containing label and a widget.VarWidget

        Note: the frame must contain the widget.VarWidget as an attribute 'widget'
        """
        self.insert_panel(frame, separator)


    def insert_label_widget(func):
        def call(
                self,
                name="",
                text="",
                value=None,
                default=None,
                separator=config.default_separator,
                **kwargs
        ):
            panel = self.make_panel(separator=separator)
            frame = ttk.Frame(panel)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            wrapped_label = textwrap.wrap(text, width=config.default_label_length)
            formatted_text='\n'.join(wrapped_label)
            label = ttk.Label(frame, text=formatted_text)
            label.grid(column=0, row=0, sticky='news')
            frame.grid(column=0,row=0, sticky='news')
            w = func(self, parent=frame, name = name, value=value, default=default,**kwargs)
            w.origin = 'OptionFrame'
            w.base_frame = panel
            return w
        return call
    #
    @insert_label_widget
    def insert_label_entry(
            self,
            parent,
            name,
            value,
            default,
            validate_type=None,
            **kwargs

    ):
        w = custom_widgets.VarEntry(
            parent=parent,
            name=name,
            value=value,
            default=default,
            validate_type=validate_type,
            **kwargs
        )
        w.grid(column=1, row=0, sticky='ews')

        return w

    @insert_label_widget
    def insert_label_optionmenu(
            self,
            parent,
            name=None,
            value=None,
            default=None,
            options=None,
            command=None,
            **kwargs
    ):
        w = custom_widgets.VarOptionmenu(
            parent=parent,
            name=name,
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
            name=None,
            value=None,
            default=None,
            command=None,
            **kwargs
    ):
        w = custom_widgets.VarCheckbutton(
            parent=parent,
            name=name,
            value=value,
            default=default,
            command=command,
            **kwargs
        )
        w.grid(column=1, row=0, sticky='news')
        return w


    def insert_title(
            self,
            name="",
            text="",
            separator=config.default_separator,
            justify=Tk.CENTER
    ):
        panel = self.make_panel(separator=separator)
        label = Tk.Label(panel, text=text, justify=justify)
        label.grid(column=0, row=0, sticky='news')
        label.base_frame = panel
        return label

    def make_panel(
            self,
            separator=True
    ):
        panel = Tk.Frame(self)
        self.num_frames += 1
        panel.grid_columnconfigure(0, weight=1)
        self.insert_panel(panel, separator)
        panel.base_frame = panel
        return panel

    def insert_panel(self, frame, separator=True):
        frame.grid(row=self.num_row, column=0,sticky='news')
        if separator:
            separator = ttk.Separator(frame, orient='horizontal')
            separator.grid(column=0, row=1, sticky='news')
        self.num_row += 1
        self.col_button = 0

    def insert_widget(self, widget):
        widget.grid(row=self.num_row, column=0, sticky='news')
        self.num_row += 1
        # if separator:
        #     separator = ttk.Separator(self, orient=Tk.HORIZONTAL)
        #     separator.grid(column=0, row=self.num_row, sticky='news')
        #     self.num_row += 1
        self.col_button = 0
        widget.base_frame = widget

    def insert_separator(self):

        s = ttk.Separator(self, orient='horizontal')
        s.grid(row=self.num_row, column=0, sticky='news')

        self.num_row += 1
        self.col_button = 0

        return s

    def isolate_button(self):
        self.col_button = 0

    def insert_button(
            self,
            name="",
            text="",
            command=None,

    ):
        if self.col_button > 0:
            panel = self.children['!frame{}'.format(self.num_frames if self.num_frames>1 else "")]
            panel.grid_columnconfigure(1, weight=1)
            row = self.num_row - 1
        else:
            panel = Tk.Frame(self)
            self.num_frames += 1
            panel.grid_columnconfigure(0, weight=1)

            row = self.num_row
        b = ttk.Button(
            panel,
            text=text,
            command=command,
        )
        b.configure()
        # b.bind('<Configure>', lambda e, c = b:self.adjust_button_width(c))

        b.grid(column=self.col_button, row=0, sticky='news')

        if self.col_button > 0:
            self.col_button = 0
        else:
            panel.grid(column=0, row=row, sticky='news')
            self.num_row += 1
            self.col_button += 1
        return b

    #
    # def adjust_button_width(self, button):
    #     print('adjust button')
    #     width = self.winfo_width()
    #     button.config(width=int(width/2))#, wraplength= int(width / 2) - 4)

    def default(self, keys=None, filter=None, widgets=None):
        if keys is None:
            keys = widgets.keys()
        if filter is not None:
            for key in keys:
                if filter in key:
                    widgets[key].set_to_default()
            return
        for key in keys:
            widgets[key].set_to_default()


class ScrollableOptionFrame(Tk.Frame):
    def __init__(self, parent, scrollbar=True):
        super().__init__(parent)
        # self.container = Tk.Frame(parent, bg='red')
        # self.scrollbar = scrollbar

        if scrollbar:
            self.canvas = Tk.Canvas(self)
            self.frame = OptionFrame(self.canvas)

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
            self.frame = OptionFrame(self)
            self.frame.grid(column=0, row=0, sticky='news')
            self.frame.grid_columnconfigure(0, weight=1)

        self.num_row = 0
        self.col_button = 0

    def adjust_width(self, e):
        # called during <Configure> event
        self.canvas.itemconfigure('option', width=e.width-4)
        pass

    def get_frame(self):
        if self.scrollbar:
            return self.frame
        else:
            return self

    def _bind_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        if self.frame.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # def insert_label_entry(self, *args, **kwargs):
    #     return self.frame.insert_label_entry(*args, **kwargs)
    #
    # def insert_label_optionmenu(self, *args, **kwargs):
    #     return self.frame.insert_label_optionmenu(*args, **kwargs)
    #
    # def insert_label_checkbox(self, *args, **kwargs):
    #    return self.frame.insert_label_checkbox(*args, **kwargs)
    #
    #
    # def insert_title(self, *args, **kwargs):
    #     return self.frame.insert_title(*args, **kwargs)
    #
    # def make_panel(self, *args, **kwargs):
    #     return self.frame.make_panel(*args, **kwargs)
    #
    # def insert_panel(self, *args, **kwargs):
    #     self.frame.insert_panel(*args, **kwargs)
    #
    # def insert_separator(self):
    #     self.frame.insert_separator()
    #
    # def isolate_button(self):
    #     self.frame.isolate_button()
    #
    # def insert_button(self, *args, **kwargs):
    #     return self.frame.insert_button(*args, **kwargs)
    #
    #
    # def default(self, *args, **kwargs):
    #     self.frame.default(*args, **kwargs)
    #
    # def get_value(self, key):
    #     return self.frame.get_value(key)
    #
    # def set_value(self, key, value):
    #     self.frame.set_value(key, value)
    #
    # def set_all(self, *args, **kwargs):
    #     self.frame.set_all(*args, **kwargs)
    #
    #
    # def get_keys(self, filter=None):
    #     return self.frame.get_keys(filter)
