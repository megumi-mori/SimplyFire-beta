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
from SimplyFire.Modules.base_module import BaseModule

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
        self.create_batch_category()
        self.add_batch_command('Apply baseline subtraction', self.control_tab.subtract_baseline)
        self.add_batch_command('Average sweeps', self.control_tab.average_sweeps)
        self.add_batch_command('Filter recording', self.control_tab.filter_data)

