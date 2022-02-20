"""
Manages active plugins. Load and access plugins.

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
import os
from simplyfire import app
import yaml
import importlib
error_free = True
plugins = {}
def load_manifests():
    global manifests
    manifests = {}

    plugins_main_dir = os.path.join(app.config.get_value('system_data_dir'), 'plugins')
    global plugin_list
    try:
        plugin_list = os.listdir(plugins_main_dir)
    except FileNotFoundError:
        plugin_list = []
    # read plugin manifests
    for plugin in plugin_list:
        plugin_dir = os.path.join(plugins_main_dir, plugin)
        with open(os.path.join(plugin_dir, 'plugin.yaml')) as f:
            plugin_manifest = yaml.safe_load(f)
        manifests[plugin_manifest['name']] = plugin_manifest
        manifests[plugin_manifest['name']]['loaded'] = False # initialize load status

def load_plugins():
    plugin_list = app.config.get_value('active_plugins')
    if plugin_list:
        for plugin_name in plugin_list:
            manifest = manifests.get(plugin_name, None) # get the manifest for the plugin
            if manifest is not None:
                app.plugin_tab.plugin_vars[plugin_name].set(True) # toggle the BooleanVar
                #check for requirements
                # try:
                load_plugin(plugin_name)
                # except Exception as e:
                #     app.log_display.log(f'Error loading {plugin_name}: {e}', 'Load Plug-in')
                    # account for requirements not being met
                    # pass


def load_plugin(plugin_name):
    global manifests
    if manifests[plugin_name]['loaded']: # already loaded
        return
    manifests[plugin_name]['loaded'] = True # should avoid circular requirements?
    for r in manifests[plugin_name].get('requirements', []):
        if r in app.config.get_value('active_plugins'): # check if requirement is in the active plugin list
            load_plugin(r)
        else:
            global error_free
            error_free = False
            app.log_display.log(f'Missing requirement for {plugin_name}: {r}', 'Load Plug-in')
    plugin_manifest = manifests[plugin_name]
    scripts = plugin_manifest.get('scripts', []) # get list scripts to load
    plugin_path = os.path.join(app.config.PLUGIN_DIR, plugin_name)
    # from plugins import style
    plugins[plugin_name] = importlib.import_module(f'plugins.{plugin_name}')
    for filename in scripts:
        plugins[f'{plugin_name}.{filename}'] = importlib.import_module(f'plugins.{plugin_name}.{filename}')
    pass

def save_plugin_data():
    data = {}
    for plugin_name in plugin_list:
        try:
            data[plugin_name] = plugins[plugin_name].save()
        except:
            data[plugin_name] = app.config.get_value(plugin_name, {}) #keep old save data

    return data

def get_plugin(plugin_name):
    return plugins.get(plugin_name, None)

def get_script(plugin_name, script_name):
    return plugins.get(f'{plugin_name}.{script_name}', None)
