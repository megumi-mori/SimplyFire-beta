"""
navigation plugin - UI load and handling
QOL add-ons for easily traversing through the trace plot

SimplyFire - Customizable analysis of electrophysiology data
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
from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire import app

from simplyfire.utils import custom_widgets

#### default values ####
window_min_x = 'auto'
window_max_x = 'auto'
window_min_y = 'auto'
window_max_y = 'auto'
window_force_lim = False

navigation_fps = 12
navigation_scroll_x_percent = 10
navigation_scroll_y_percent = 10
navigation_zoom_x_percent = 10
navigation_zoom_y_percent = 10
navigation_mirror_y_scroll = 1
navigation_mirror_x_scroll = 1

key_show_all = ['<Key-Home>']

#### modify PluginForm class ####
class NaviForm(PluginForm):
    def apply_parameters(self, undo=True):
        super().apply_parameters(undo=undo)
        apply_navigation()
        app.interface.focus()

#### functions ####
def apply_window(event=None):
    min_x = form.inputs['window_min_x'].get()
    if min_x == 'auto':
        min_x = app.trace_display.default_xlim[0]
    else:
        min_x = float(min_x)
    max_x = form.inputs['window_max_x'].get()
    if max_x == 'auto':
        max_x = app.trace_display.default_xlim[1]
    else:
        max_x = float(max_x)
    min_y = form.inputs['window_min_y'].get()
    if min_y == 'auto':
        min_y = app.trace_display.default_ylim[0]
    else:
        min_y = float(min_y)
    max_y = form.inputs['window_max_y'].get()
    if max_y == 'auto':
        max_y = app.trace_display.default_ylim[1]
    else:
        max_y = float(max_y)

    app.trace_display.set_axis_limit('x', (min_x, max_x))
    app.trace_display.set_axis_limit('y', (min_y, max_y))

    app.trace_display.draw_ani()
    app.interface.focus()

def apply_navigation(event=None):
    app.interpreter.navigation_fps = int(form.inputs['navigation_fps'].get())
    app.graph_panel.navigation_fps = int(form.inputs['navigation_fps'].get())
    app.graph_panel.navigation_scroll_x_percent = float(form.inputs['navigation_scroll_x_percent'].get())
    app.graph_panel.navigation_zoom_x_percent = float(form.inputs['navigation_zoom_x_percent'].get())
    app.graph_panel.navigation_scroll_y_percent = float(form.inputs['navigation_scroll_y_percent'].get())
    app.graph_panel.navigation_zoom_y_percent = float(form.inputs['navigation_zoom_y_percent'].get())
    app.graph_panel.navigation_mirror_x_scroll = int(form.inputs['navigation_mirror_x_scroll'].get())
    app.graph_panel.navigation_mirror_y_scroll = int(form.inputs['navigation_mirror_y_scroll'].get())
    app.interface.focus()

def get_current_lim(event=None):
    xlim = app.trace_display.get_axis_limits('x')
    ylim = app.trace_display.get_axis_limits('y')
    form.inputs['window_min_x'].set(xlim[0])
    form.inputs['window_max_x'].set(xlim[1])
    form.inputs['window_min_y'].set(ylim[0])
    form.inputs['window_max_y'].set(ylim[1])
    form.apply_parameters(undo=True)
    app.interface.focus()

def get_current_xlim(event=None):
    xlim = app.trace_display.get_axis_limits('x')
    form.inputs['window_min_x'].set(xlim[0])
    form.inputs['window_max_x'].set(xlim[1])
    app.interface.focus()
    form.apply_parameters(undo=True)

def get_current_ylim(event=None):
    ylim = app.trace_display.get_axis_limits('y')
    form.inputs['window_min_y'].set(ylim[0])
    form.inputs['window_max_y'].set(ylim[1])
    app.interface.focus()
    form.apply_parameters(undo=True)

def on_open(event=None):
    if form.inputs['window_force_lim'].get():
        apply_window()
    app.interface.focus()

def show_all(event=None):
    app.trace_display.set_axis_limit('x', app.trace_display.default_xlim)
    app.trace_display.set_axis_limit('y', app.trace_display.default_ylim)
    app.trace_display.draw_ani()
    app.interface.focus()

#### make GUI components ####
controller = PluginController(name='navigation', menu_label='Navigation')
form = NaviForm(controller, tab_label='Navi', scrollbar=True, notebook=app.cp_notebook)

#### form layout ####
form.insert_title(text='Navigation')
panel = form.make_panel(separator=True)
label = form.make_label(panel, text='x-axis:')
label.grid(column=0, row=0, sticky='news')
entry = custom_widgets.VarEntry(parent=panel, name='window_min_x', default=window_min_x)
entry.grid(column=1, row=0, sticky='news')
entry.bind('<Return>', apply_window, add='+')
form.inputs['window_min_x'] = entry
entry = custom_widgets.VarEntry(parent=panel, name='window_max_x', default=window_max_x)
entry.grid(column=2, row=0, sticky='news')
entry.bind('<Return>', apply_window, add='+')
form.inputs['window_max_x'] = entry
button = form.make_button(panel, text='Get', command=get_current_xlim)
button.grid(column=3, row=0, sticky='news')

panel = form.make_panel(separator=True)
label = form.make_label(panel, text='y-axis:')
label.grid(column=0, row=0, sticky='news')
entry = custom_widgets.VarEntry(panel, name='window_min_y', default=window_min_y)
entry.grid(column=1, row=0, sticky='news')
entry.bind('<Return>', apply_window, add='+')
form.inputs['window_min_y'] = entry
entry = custom_widgets.VarEntry(panel, name='window_max_y', default=window_max_y)
entry.grid(column=2, row=0, sticky='news')
entry.bind('<Return>', apply_window, add='+')
form.inputs['window_max_y'] = entry
button = form.make_button(panel, text='Get',command=get_current_ylim)
button.grid(column=3, row=0, sticky='news')

form.insert_label_checkbox(
    name='window_force_lim',
    text='Force axis limits on open',
    type=bool,
    onvalue=True,
    offvalue=False,
    default=window_force_lim
)

form.insert_button(text='Apply', command=apply_window)
form.insert_button(text='Default', command=lambda filter='window':form.set_to_default(filter=filter))
form.insert_button(text='Show all', command=show_all)
form.insert_button(text='Get current', command=get_current_lim)

form.insert_separator()

form.insert_label_entry(name='navigation_fps', text='Smooth navigation speed (fps)', validate_type='int',
                        default=navigation_fps)
form.insert_label_entry(name='navigation_scroll_x_percent', text='Scroll speed (percent x-axis)',
                        validate_type='float', default=navigation_scroll_x_percent)
form.insert_label_entry(name='navigation_zoom_x_percent', text='Zoom speed (percent x-axis)',
                        validate_type='float', default=navigation_zoom_x_percent)
form.insert_label_entry(name='navigation_scroll_y_percent', text='Scroll speed (percent y-axis)',
                        validate_type='float', default=navigation_scroll_y_percent)
form.insert_label_entry(name='navigation_zoom_y_percent', text='Zoom speed (percent y-axis)',
                        validation_type='float', default=navigation_zoom_y_percent)
for key in form.inputs.keys():
    if 'navigation' in key:
        form.inputs[key].bind('<Return>', form.apply_parameters, add='+')
        form.inputs[key].bind('<FocusOut>', form.apply_parameters, add='+')

form.insert_label_checkbox(name='navigation_mirror_x_scroll', text='Mirror x-axis scroll',
                           onvalue=-1, offvalue=1, type=int,
                           default=navigation_mirror_x_scroll)
form.insert_label_checkbox(name='navigation_mirror_y_scroll', text=' Mirror y-axis scroll',
                           onvalue=-1, offvalue=1, type=int,
                           default=navigation_mirror_y_scroll)

form.insert_button(text='Apply', command=apply_navigation)
form.insert_button(text='Default', command=lambda filter='navigation':form.set_to_default(filter=filter))

#### binding ####
controller.listen_to_event('<<OpenedRecording>>', on_open)

for key in key_show_all:
    app.trace_display.canvas.get_tk_widget().bind(key, show_all, add='+')


#### initialize ####
controller.load_values()
controller.update_plugin_display()
app.plugin_manager.get_plugin('navigation').save = controller.save
form.apply_parameters(undo=False)