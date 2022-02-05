from SimplyFire.Modules.base_module import BaseModule
class Module(BaseModule):
    def __init__(self):
        super().__init__(name='style',
                         menu_label='Style',
                         tab_label='Style',
                         filename=__file__)