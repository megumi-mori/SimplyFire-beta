from PyMini.Modules.base_parent_module import BaseParentModule
class ParentModule(BaseParentModule):
    def __init__(self):
        super().__init__(name='style',
                         menu_label='Style',
                         tab_label='Style',
                         filename=__file__)