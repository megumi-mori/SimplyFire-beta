from PyMini.Modules.base_tab_module import BaseTabModule

class TabModule(BaseTabModule):
    def __init__(self):
        super(TabModule, self).__init__(
            name='Mini Analysis',
            label='Mini',
        )
        self.optionframe.insert_title(
            text="Mini Analysis"
        )
        self.find_all_button = self.optionframe.insert_button(
            text='Find all'
        )
        self.optionframe.insert_button(
            text='Delete all'
        )
        self.optionframe.insert_button(
            text='Find in\nwindow'
        )
        self.optionframe.insert_button(
            text='Delete in\nwindow'
        )
        self.optionframe.insert_button(
            text='Report stats'
        )


