from PyMini.Modules.base_control_module import BaseControlModule

class TabModule(BaseTabModule):
    def __init__(self):
        super(TabModule, self).__init__(
            name='Test Module',
            label='Test',
        )