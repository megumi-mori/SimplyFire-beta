from PyMini.Modules.base_module import BaseModule

class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='process_recording',
            menu_label='Process Recording',
            tab_label='Process',
            filename=__file__
        )

        self._load_batch()

    def _load_batch(self):
        self.control_tab.add_batch_category()
        self.control_tab.add_batch_command('Apply baseline subtraction', self.control_tab.subtract_baseline)
        self.control_tab.add_batch_command('Average sweeps', self.control_tab.average_sweeps)
        self.control_tab.add_batch_command('Filter recording', self.control_tab.filter_data)

