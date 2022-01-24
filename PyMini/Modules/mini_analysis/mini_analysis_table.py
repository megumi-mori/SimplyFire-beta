from PyMini import app
from PyMini.Modules.base_table_module import BaseTableModule
from collections import OrderedDict
from PyMini.utils.widget import DataTable

class ModuleTable(BaseTableModule):
    def __init__(self):
        super(ModuleTable, self).__init__(
            name='mini_analysis',
            menu_label='Mini Analysis',
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
        for key in app.config.key_delete:
            self.table.bind(key, self.delete_selected, add="")
        self.define_columns(tuple([key for key in self.mini_header2config]),iid_header='t')
        self.bind("<<OpenRecording>>", self.clear)

        self.table.bind('<<TreeviewSelect>>', self.report_selected)

    def report_selected(self, event=None):
        self.module_control.select_from_table(self.table.selection())

    def clear(self, event=None):
        self.module_control.delete_all(True)

    def delete_selected(self, event=None):
        self.module_control.delete_selection([float(s) for s in self.table.selection()])

    def report(self, event=None):
        self.module_control.report_results()

