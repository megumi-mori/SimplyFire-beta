"""
SimplyFire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from SimplyFire import app
from SimplyFire.Modules.base_module_table import BaseModuleDataTable
from collections import OrderedDict
from SimplyFire.utils.custom_widgets import DataTable

class ModuleDataTable(BaseModuleDataTable):
    def __init__(self, module):
        super(ModuleDataTable, self).__init__(
            module=module
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
        #
        self.table.bind('<<TreeviewSelect>>', self.treeview_selected)

    def treeview_selected(self, event=None):
        self.module.control_tab.select_from_table(self.table.selection())

    def clear(self, event=None):
        self.module.control_tab.delete_all(True)

    def delete_selected(self, event=None):
        self.module.control_tab.delete_selection([float(s) for s in self.table.selection()])

    def report(self, event=None):
        self.module.control_tab.report_results()

    def report_selected(self, event=None):
        self.module.control_tab.report_selected_results()

    def append(self, dataframe, undo=False):
        super().append(dataframe, undo=False)

