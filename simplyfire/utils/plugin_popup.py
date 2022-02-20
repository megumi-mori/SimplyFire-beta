"""
Base UI for plugin popup.

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
from .plugin_GUI import PluginGUI
from tkinter import Toplevel
from simplyfire import app
from .plugin_controller import PluginController
class PluginPopup(Toplevel, PluginGUI):
    def __init__(self,
                 plugin_controller:PluginController
                 ) -> None:
        self.visible=False
        Toplevel.__init__(self, app.root)
        PluginGUI.__init__(self, plugin_controller)
        super().withdraw()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def show_window(self):
        self.visible = True
        self.deiconify()

    def withdraw_window(self):
        self.visible=False
        super().withdraw()
    def _on_close(self, event=None):
        self.visible = False
        super().withdraw()

    def enable(self):
        if self.visible:
            self.deiconify()
            self.lower(belowThis=app.root)
        else:
            pass

    def disable(self):
        super().withdraw()

    def hide(self):
        super().withdraw()

    def is_visible(self):
        return self.visible
