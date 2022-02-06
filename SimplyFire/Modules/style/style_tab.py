from SimplyFire.Modules.base_module_control import BaseModuleControl
from SimplyFire import app
from SimplyFire.utils.custom_widgets import VarEntry
from tkinter import ttk
import tkinter as Tk
class ModuleControl(BaseModuleControl):
    def __init__(self, module):
        super(ModuleControl, self).__init__(
            scrollbar=True,
            module=module,
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

        self.trace_color = app.trace_display.trace_color
        self.trace_width = app.trace_display.trace_width

        row=0

        ttk.Label(self.main_style_panel, text='size', justify=Tk.CENTER).grid(column=self.size_column, row=row, sticky='news')
        ttk.Label(self.main_style_panel, text='color', justify=Tk.CENTER).grid(column=self.color_column, row=row, sticky='news')

        row+= 1
        ttk.Label(self.main_style_panel, text='Trace plot').grid(column=self.label_column, row=row, sticky='news')
        self.place_VarEntry(name='style_trace_line_width', column=self.size_column, row=row, frame=self.main_style_panel,
                       width=self.size_width, validate_type='float')
        self.place_VarEntry(name='style_trace_line_color', column=self.color_column, row=row, frame=self.main_style_panel,
                       width=self.color_width, validate_type='color')

        for w in self.widgets:
            self.widgets[w].bind('<Return>', self.apply_styles, add='+')
        self.insert_button(text='Apply', command=self.apply_styles)
        self.insert_button(text='Default', command=self.apply_default)

        self._load_binding()

    def place_VarEntry(self, name, column, row, frame, width=None, validate_type=""):
        self.widgets[name] = VarEntry(frame, name=name, width=width, validate_type=validate_type,
                                      value=self.values.get(name,None), default=self.defaults.get(name, None))
        self.widgets[name].grid(column=column, row=row, sticky='news')

    def apply_styles(self, event=None, undo=True):
        if undo and app.interface.is_accepting_undo():
            self.module.add_undo([
                lambda c = self.trace_color:self.widgets['style_trace_line_color'].set(c),
                lambda w = self.trace_width:self.widgets['style_trace_line_width'].set(w),
                lambda u=False:self.apply_styles(undo=u)
            ])
        app.trace_display.trace_color = self.widgets['style_trace_line_color'].get()
        app.trace_display.trace_width = float(self.widgets['style_trace_line_width'].get())
        self.trace_color = app.trace_display.trace_color
        self.trace_width = app.trace_display.trace_width
        app.interface.plot()
        app.interface.focus()
        pass

    def apply_default(self, event=None):
        self.set_to_default()
        self.apply_styles()
        pass

    def _revert(self, event=None):
        self.widgets['style_trace_line_color'].set(self.trace_color)
        self.widgets['style_trace_line_width'].set(self.trace_width)
        self.apply_styles(undo=False)


    def _load_binding(self):
        self.listen_to_event('<<LoadCompleted>>', lambda u=False:self.apply_styles(undo=u))