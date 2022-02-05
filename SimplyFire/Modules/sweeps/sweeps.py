from SimplyFire.Modules.base_module import BaseModule
from SimplyFire import app
class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='sweeps',
            menu_label='Sweeps',
            tab_label='Sweeps',
            filename=__file__
        )

        if app.widgets['trace_mode'].get() != 'overlay':
            try:
                self._add_disable()
            except:
                pass

        self._load_batch()


    def _load_batch(self):
        self.control_tab.add_batch_category()
        self.control_tab.add_batch_command('Show All', lambda u=False:self.control_tab.show_all(undo=u))
        self.control_tab.add_batch_command('Hide All', lambda u=False:self.control_tab.hide_all(undo=u))
