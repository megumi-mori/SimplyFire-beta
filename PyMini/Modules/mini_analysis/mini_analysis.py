from PyMini.Modules.base_module import BaseModule
from PyMini import app
class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='mini_analysis',
            menu_label='Mini Analysis',
            tab_label='Mini',
            filename=__file__
        )

        if app.widgets['trace_mode'].get() != 'continuous':
            try:
                self._disable()
            except:
                pass

    def update_module_display(self, table=False):
        super().update_module_display()

        if self.menu_var.get():
            self.control_tab.update_event_markers(draw=True)
        else:
            for m in self.control_tab.markers:
                try:
                    self.control_tab.markers[m].remove()
                except:
                    pass
            app.trace_display.draw_ani()
        app.pb['value'] = 0
        app.pb.update()