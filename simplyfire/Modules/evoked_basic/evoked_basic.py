"""
simplyfire - Customizable analysis of electrophysiology data
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

from simplyfire.Modules.base_module import BaseModule
from simplyfire.layout import batch_popup
from simplyfire.utils import formatting
import os
class Module(BaseModule):
    def __init__(self):
        super().__init__(
            name='evoked_basic',
            menu_label='Evoked Analysis',
            tab_label='Evoked',
        )

        self._load_batch()
        self._modify_GUI()

    def _load_batch(self):
        batch_popup.insert_command_category('Evoked Analysis')
        batch_popup.insert_command('Calculate min/max', 'Evoked Analysis', self.control_tab.calculate_min_max)
        batch_popup.insert_command('Report results', 'Evoked Analysis', self.data_tab.report)
        def export_results():
            if len(self.data_tab.table.get_children())== 0:
                batch_popup.batch_log.insert('Warning: Exporting an empty data table\n')
            fname = formatting.format_save_filename(os.path.splitext(batch_popup.file_list[batch_popup.file_idx])[0]+'_EvokedAnalysis.csv', overwrite=False)
            self.data_tab.export(fname, overwrite=False)
            batch_popup.batch_log.insert(f"Saved evoked analysis results to: {fname}\n")
        batch_popup.insert_command('Export results', 'Evoked Analysis', export_results)


    def _modify_GUI(self):
        self.add_file_menu_command(label='Export data table', command=self.data_tab.ask_export_data)


