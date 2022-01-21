from PyMini import app
from PyMini.Modules.base_table_module import BaseTableModule
from collections import OrderedDict

class ModuleTable(BaseTableModule):
    def __init__(self):
        super(ModuleTable, self).__init__(
            name='Mini Analysis',
            tab_label='Mini',
            parent=app.root
        )
        self.mini_header2config = OrderedDict([
            ('t', 'data_display_time'),
            ('amp', 'data_display_amplitude'),
            ('amp_unit', 'data_display_amplitude'),
            ('decay_const', 'data_display_decay'),
            ('decay_unit', 'data_display_decay'),
            # ('decay_func', 'data_display_decay_func'),
            # ('decay_t', 'data_display_decay_time'),
            ('rise_const', 'data_display_rise'),
            ('rise_unit', 'data_display_rise'),
            ('halfwidth', 'data_display_halfwidth'),
            ('halfwidth_unit', 'data_display_halfwidth'),
            ('baseline', 'data_display_baseline'),
            ('baseline_unit', 'data_display_baseline'),
            ('channel', 'data_display_channel'),
            ('stdev', 'data_display_std'),
            ('stdev_unit', 'data_display_std'),
            ('direction', 'data_display_direction'),
            ('compound', 'data_display_compound')
        ])
        self.define_columns(tuple([key for key in self.mini_header2config]),iid_header='t')

    def add(self, data, index='end'):
        app.data_notebook.tab(self, state='disabled')
        self.add(data, index=index)
        app.data_notebook.tab(self, state='normal')


