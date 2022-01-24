from PyMini.Modules.base_control_module import BaseControlModule
from PyMini import app
from PyMini.utils.widget import VarEntry
from tkinter import ttk
import tkinter as Tk
class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
            name='style',
            menu_label='Style',
            tab_label='Style',
            parent=app.root,
            scrollbar=True,
            filename=__file__,
            has_table=False
        )

        self.insert_title(
            text='Basic plot style'
        )
        self.main_style_panel = self.make_panel(separator=False)
        self.main_style_panel.grid_columnconfigure(0, weight=1)
        self.main_style_panel.grid_columnconfigure(1, weight=1)
        self.main_style_panel.grid_columnconfigure(2, weight=1)
        self.color_width = 10
        self.size_width =5

        self.label_column=1
        self.size_column=2
        self.color_column=3

        self.row=0

        ttk.Label(self.main_style_panel, text='size', justify=Tk.CENTER).grid(column=size_column, row=row, sticky='news')
        ttk.Label(self.main_style_panel, text='color', justify=Tk.CENTER).grid(column=color_column, row=row, sticky='news')

        row+= 1
        ttk.Label(self.main_style_panel, text='Trace plot').grid(column=label_column, row=row, sticky='news')
        self.place_VarEntry(name='style_trace_line_width', column=size_column, row=row, frame=self.main_style_panel,
                       width=size_width, validate_type='float')
        self.place_VarEntry(name='style_trace_line_color', column=color_column, row=row, frame=self.main_style_panel,
                       width=color_width, validate_type='color')

        for w in self.widgets:
            self.widgets[w].bind('<Return>', self.apply_styles, add='+')
        self.insert_button(text='Apply', command=self.apply_styles)
        self.insert_button(text='Default', command=self.apply_default)

    def place_VarEntry(self, name, column, row, frame, width=None, validate_type=""):
        self.widgets[name] = VarEntry(frame, name=name, width=width, validate_type=validate_type,
                                      value=self.values.get(name,None), default=self.default.get(name, None))
        self.widgets[name].grid(column=column, row=row, sticky='news')

    def apply_styles(self, event=None):
        app.trace_display.trace_color = self.widgets['style_trace_line_color'].get()
        app.trace_display.trace_width = float(self.widgets['style_trace_line_width'].get())
        app.interface.plot()
        pass

    def apply_default(self, event=None):
        self.set_to_default()
        pass