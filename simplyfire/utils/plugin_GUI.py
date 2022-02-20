"""
Base class for plugin-UI components.

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
from simplyfire import app
from .plugin_controller import PluginController
class PluginGUI():
    """
    parent class for module GUI components
    the child class must implement the following fucntions that returns a bool for the event binding to work:

    is_enabled
    has_focus
    is_visible


    """
    def __init__(self,
                 plugin_controller:PluginController):
        self.inputs = {}
        self.controller = plugin_controller
        self.controller.children.append(self)
        pass

    def call_if_enabled(self, function):
        if self.is_enabled():
            function()

    def call_if_focus(self, function):
        if self.has_focus():
            function()

    def call_if_visible(self, function):
        if self.is_visible():
            function()

    def listen_to_event(self, event:str, function, condition:str=None, target=app.root):
        assert condition in {'focused', 'enabled', 'visible', None}, 'condition must be None, "focus", or "enabled"'
        # assert callable(function), f'{function} is not callable'
        if condition is None:
            target.bind(event, lambda e:function(), add="+")
        elif condition == 'enabled':
            target.bind(event, lambda e, f=function:self.call_if_enabled(f), add='+')
        elif condition == 'focused':
            target.bind(event, lambda e, f=function:self.call_if_focus(f), add="+")
        elif condition == 'visible':
            target.bind(event, lambda e, f=function: self.call_if_visible(f), add='+')

    def apply_vales(self, values):
        # this function is called whenever user_config files are read and user parameters are changed
        # implement this function for effects that need to take place whenever parameters are changed
        pass

    def save(self):
        return {k:self.inputs[k].get() for k in self.inputs.keys()}

    def load_values(self, data):
        for key in self.inputs.keys():
            self.inputs[key].set(data.get(key, self.inputs[key].get())) # keep the same value if no data available