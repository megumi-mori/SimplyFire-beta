from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire import app
from simplyfire.backend import plugin_manager
tab_label = 'Mini'
menu_label = 'Mini Analysis'
name = 'mini_analysis'

form = PluginForm(tab_label=tab_label, scrollbar=True, notebook=app.cp_notebook)

#### modify the controller ####
class MiniController(PluginController):
    def update_plugin_display(self, event=None):
        super().update_plugin_display()
        print('udpdate plugin display')
        try:
            if self.is_visible():
                form.update_event_markers(draw=True)
            else:
                for m in form.markers:
                    try:
                        form.markers[m].remove()
                    except:
                        pass
                app.trace_display.draw_ani()
        except:
            pass
    app.pb['value'] = 0
    app.pb.update()

controller = MiniController(
    name=name,
    menu_label=menu_label,
    file_menu=True
)

controller.create_batch_category()

controller.children.append(form)
controller.load_values()
if app.inputs['trace_mode'].get() != 'continuous':
    try:
       controller.disable_module()
    except:
        pass
plugin_manager.mini_analysis.save = controller.save