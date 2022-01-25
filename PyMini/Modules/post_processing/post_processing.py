from PyMini import app
from PyMini.Modules.base_control_module import BaseControlModule

class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
                 name='post_processing',
                 menu_label = 'Process Recording',
                 tab_label = 'Process',
                 parent=app.root,
                 scrollbar=True,
                 filename=__file__,
                 has_table=False
                 )
        pass