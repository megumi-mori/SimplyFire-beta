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

form = PluginForm(plugin_controller=controller, tab_label=tab_label, scrollbar=True, notebook=app.cp_notebook)

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
    print(entry.default)
    form.inputs[name] = entry

ttk.Label(form.main_panel, text='Trace plot').grid(column=label_column, row=row, sticky='news')
insert_VarEntry(column=size_column, row=row, name='style_trace_line_width', width=size_width,
                validate_type='float', default=form.default_size)
insert_VarEntry(column=color_column, row=row, name='style_trace_line_color', width=color_width,
                validate_type='color', default=form.default_color)

def apply_styles(event=None, undo=True):
    if undo and app.interface.is_accepting_undo():
        controller.add_undo([
            lambda c=form.trace_color:form.inputs['style_trace_line_color'].set(c),
            lambda w=form.trace_width:form.inputs['style_trace_line_width'].set(w),
            lambda u=False:apply_styles(undo=u)
        ])
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
    apply_styles()

for key in form.inputs.keys():
    form.inputs[key].bind('<Return>', apply_styles, add='+')

form.insert_button(text='Apply', command=apply_styles)
form.insert_button(text='Default', command=apply_default)

controller.listen_to_event('<<LoadCompleted>>', lambda u=False:apply_styles(undo=u))
controller.listen_to_event('<<LoadedConfig>>', controller.load_values)
controller.listen_to_event('<<LoadedConfig>>', lambda u=False:apply_styles(undo=u))

controller.children.append(form)
controller.load_values()
controller.update_plugin_display()

app.plugin_manager.style.save = controller.save
