from PyMini.Modules.base_tab_module import BaseTabModule

class TabModule(BaseTabModule):
    def __init__(self):
        super(TabModule, self).__init__(
            name='Test Module2',
            label='Test',
        )