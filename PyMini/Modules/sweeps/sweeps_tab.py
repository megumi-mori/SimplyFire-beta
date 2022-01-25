from PyMini import app
from PyMini.Modules.base_control_module import BaseControlModule

class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
            name='sweeps',
        menu_label='Sweep Selector',
        tab_label='Sweep',
        parent=app.root,
        scrollbar=False,
        filename=__file__,
        has_table=False)

        pass