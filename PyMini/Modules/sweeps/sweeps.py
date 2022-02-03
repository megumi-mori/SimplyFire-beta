from PyMini.Modules.base_module import BaseModule
from PyMini import app
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