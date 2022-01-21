from PyMini import app
from PyMini.Modules.base_table_module import BaseTableModule
class ModuleTable(BaseTableModule):
    def __init__(self):
        super(ModuleTable, self).__init__(
            name='Mini Analysis',
            tab_label='Mini',
            parent=app.root
        )

