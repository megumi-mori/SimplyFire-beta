from PyMini.Modules.base_module import BaseModule

class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='process_recording',
            menu_label='Process Recording',
            tab_label='Process',
            filename=__file__
        )