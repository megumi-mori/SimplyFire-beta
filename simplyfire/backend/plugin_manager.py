import os
from simplyfire import app
import yaml
import importlib
def load_manifests():
    global manifests
    manifests = {}

    plugins_main_dir = os.path.join(app.config.config_user_dir, 'plugins')
    global plugin_list
    plugin_list = os.listdir(plugins_main_dir)
    # read plugin manifests
    for plugin in plugin_list:
        plugin_dir = os.path.join(plugins_main_dir, plugin)
        with open(os.path.join(plugin_dir, 'plugin.yaml')) as f:
            plugin_manifest = yaml.safe_load(f)
        manifests[plugin_manifest['name']] = plugin_manifest

def load_plugin(plugin_name):
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
        # try:
        temp = globals()[plugin_name].save()
        data[plugin_name] = temp
        print(f'at the manager level: {data[plugin_name]}')
        print(f'at the manager level: {temp}')
        # except IndexError:
        #     data[plugin_name] = getattr(app.config, plugin_name, {}) #keep old save data
    return data

