from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire.utils import custom_widgets
from simplyfire import app

from tkinter import ttk

tab_label = 'Style'
menu_label = 'Style'
name = 'style'

controller = PluginController(
    name = 'style',
    menu_label = 'Style',
)

#### modify PluginForm class ####
class StyleForm(PluginForm):
    def apply_parameters(self, undo=True):
        super().apply_parameters(undo=undo)
        app.trace_display.trace_color = form.inputs['style_trace_line_color'].get()
        app.trace_display.trace_width = float(form.inputs['style_trace_line_width'].get())
        for s in app.trace_display.sweeps.keys():
            app.trace_display.sweeps[s].set_color(app.trace_display.trace_color)
            app.trace_display.sweeps[s].set_linewidth(app.trace_display.trace_width)
        form.trace_color = app.trace_display.trace_color
        form.trace_width = app.trace_display.trace_width
        app.trace_display.draw_ani()

form = StyleForm(plugin_controller=controller, tab_label=tab_label, scrollbar=True, notebook=app.cp_notebook)
#### functions ####
def apply_styles(event=None, undo=True):
    if undo and app.interface.is_accepting_undo():
        undo_stack = []
        if form.trace_color != form.inputs['style_trace_line_color'].get():
            undo_stack.append(lambda c=form.trace_color:form.inputs['style_trace_line_color'].set(c))
        if form.trace_width != float(form.inputs['style_trace_line_width'].get()):
            undo_stack.append(lambda w=form.trace_width:form.inputs['style_trace_line_width'].set(w))
        if len(undo_stack) > 0:
            undo_stack.append(lambda u=False:form.apply_parameters(undo=u))
            controller.add_undo(undo_stack)
    app.trace_display.trace_color = form.inputs['style_trace_line_color'].get()
    app.trace_display.trace_width = float(form.inputs['style_trace_line_width'].get())
    for s in app.trace_display.sweeps.keys():
        app.trace_display.sweeps[s].set_color(app.trace_display.trace_color)
        app.trace_display.sweeps[s].set_linewidth(app.trace_display.trace_width)
    form.trace_color = app.trace_display.trace_color
    form.trace_width = app.trace_display.trace_width
    app.trace_display.draw_ani()
    # app.interface.plot(fix_y=True, fix_x=True)
    app.interface.focus()

def apply_default(event=None):
    form.set_to_default()
    # apply_styles()
    form.apply_parameters()

############ format form #################
form.main_panel = form.make_panel(separator=False)
form.main_panel.grid_columnconfigure(0, weight=1)
form.main_panel.grid_columnconfigure(1, weight=1)
form.main_panel.grid_columnconfigure(2, weight=1)

color_width = 10
size_width = 5
label_column = 1
size_column = 2
color_column = 3

form.trace_color = app.trace_display.trace_color
form.trace_width = app.trace_display.trace_width

form.default_color = 'black'
form.default_size = 1

row = 0
ttk.Label(form.main_panel, text='size', justify='center').grid(column=size_column, row=row, sticky='news')
ttk.Label(form.main_panel, text='color', justify='center').grid(column=color_column, row=row, sticky='news')

row += 1
def insert_VarEntry(column, row, name, width, validate_type, default):
    entry = custom_widgets.VarEntry(parent=form.main_panel, validate_type=validate_type, width=width, default=default)
    entry.grid(column=column, row=row, sticky='news')
    form.inputs[name] = entry
    form.inputs[name].bind('<Return>', form.apply_parameters, add='+')
    form.inputs[name].bind('<FocusOut>', form.apply_parameters, add='+')

ttk.Label(form.main_panel, text='Trace plot').grid(column=label_column, row=row, sticky='news')
insert_VarEntry(column=size_column, row=row, name='style_trace_line_width', width=size_width,
                validate_type='float', default=form.default_size)
insert_VarEntry(column=color_column, row=row, name='style_trace_line_color', width=color_width,
                validate_type='color', default=form.default_color)

form.insert_button(text='Apply', command=form.apply_parameters)
form.insert_button(text='Default', command=apply_default)

controller.children.append(form)
controller.load_values()
controller.update_plugin_display()

app.plugin_manager.get_plugin('style').save = controller.save
form.apply_parameters(undo=False)