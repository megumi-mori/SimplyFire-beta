from SimplyFire.Modules.base_module_control import BaseModuleControl

class TabModule(BaseTabModule):
    def __init__(self):
        super(TabModule, self).__init__(
            name='Test Module2',
            label='Test',
        )