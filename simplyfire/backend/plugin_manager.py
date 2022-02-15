import os
from simplyfire import app
import yaml
import importlib
error_free = True
def load_manifests():
    global manifests
    manifests = {}

    plugins_main_dir = os.path.join(app.config.system_user_dir, 'plugins')
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
    globals()[plugin_name] = importlib.import_module(f'plugins.{plugin_name}')
    for filename in scripts:
        globals()[f'{plugin_name}.{filename}'] = importlib.import_module(f'plugins.{plugin_name}.{filename}')
    pass

def save_plugin_data():
    data = {}
    for plugin_name in plugin_list:
        try:
            data[plugin_name] = globals()[plugin_name].save()
        except:
            data[plugin_name] = app.config.get_value(plugin_name, {}) #keep old save data

    return data

