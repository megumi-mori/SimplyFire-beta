from PyMini.Modules.base_module import BaseModule

class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='evoked_basic',
            menu_label='Evoked Analysis',
            tab_label='Evoked',
        )

