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

import yaml
import os
import pkg_resources
import sys

# set up default parameters during module import
# Constants
global CONFIG_DIR  # package config file path
CONFIG_DIR = pkg_resources.resource_filename('simplyfire', 'setting/')
global IMG_DIR
IMG_DIR = pkg_resources.resource_filename('simplyfire', 'img/')
global TEMP_DIR
TEMP_DIR = pkg_resources.resource_filename('simplyfire', 'temp/')

# Load defaults
global default_vars
default_vars = {}
global system_vars
system_vars = {}
global user_vars
user_vars = {}
global keymap_vars
keymap_vars = {}

print('loading default config')
default_config_path = os.path.join(CONFIG_DIR, "default_config.yaml")  # config/default_config.yaml
with open(default_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        default_vars[c] = v
        if 'system' not in c:
            globals()[c] = v
            user_vars[c] = v
        elif 'system' in c:
            globals()[c] = v
            system_vars[c] = v
global default_config_user_dir
default_system_user_dir = pkg_resources.resource_filename('simplyfire', '')
global system_user_dir
system_user_dir = default_system_user_dir
print('completed')

def load():
    # Load user configurations
    global system_setting_path
    system_setting_path = os.path.join(CONFIG_DIR, default_vars['system_setting_path'])
    try:
        with open(system_setting_path) as f:
            configs = yaml.safe_load(f)
            for c, v in configs.items():
                globals()[c] = v
                # system_vars[c] = v
                user_vars[c] = v
    except:
        pass
    global sysetm_user_dir
    global PLUGIN_DIR
    PLUGIN_DIR = os.path.join(system_user_dir, 'plugins')
    sys.path.insert(0, system_user_dir)

    # global config_keymap_path
    # config_keymap_path = os.path.join(CONFIG_DIR, default_config_keymap_path)
    # try:
    #     with open(config_keymap_path) as f:
    #         configs = yaml.safe_load(f)
    #         for c, v in configs.items():
    #             globals()[c] = v
    #             user_vars[c] = v
    # except:
    #     pass

    # global config_user_path
    # if config_autoload == 1 or config_autoload == '1': # info stored in system_config
    #     try:
    #         d, f = os.path.split(config_user_path)
    #         if not os.path.isdir(d):
    #             config_user_path = os.path.join(CONFIG_DIR, config_user_path)
    #     except Exception as e:
    #         print('config load error: {}'.format(e))
    #         config_user_path = convert_to_path('')
    #     try:
    #         print('loading {}'.format(config_user_path))
    #         with open(config_user_path) as f:
    #             configs = yaml.safe_load(f)
    #             for c, v in configs.items():
    #                 globals()[c] = v
    #                 user_vars[c] = v
    #     except:
    #         pass

    global user_config_load_error
    user_config_load_error = None
    if system_autoload == 1 or system_autoload == '1':
        try:
            print(f'loading user_config.yaml from {system_user_dir}')
            system_user_path = os.path.join(system_user_dir, 'user_config.yaml')
            with open(system_user_path) as f:
                configs = yaml.safe_load(f)
                for c, v in configs.items():
                    globals()[c] = v
                    user_vars[c] = v
        except FileNotFoundError:
            pass
        except AttributeError as e:
            user_config_load_error = e
            pass

    try:
        active_plugin_path = os.path.join(system_user_dir, 'active_plugins.yaml')
        with open(active_plugin_path) as f:
            configs = yaml.safe_load(f)
            globals()['active_plugins'] = configs['active_plugins']
            user_vars['active_plugins'] = configs['active_plugins']
    except FileNotFoundError:
        pass
    except (AttributeError, KeyError) as e:
        print(f'Error loading active plugins: {e}')
        pass


def convert_to_path(paths):
    """
    :param paths: path in a list
    :return:
    """
    if isinstance(paths, str):
        return paths.strip()
    # p = [i if i != "DIR" else DIR for i in paths]
    p = [i for i in paths]
    return os.path.join(*p)

def get_value(key, none_value=None):
    return user_vars.get(key, none_value)

def get_default_value(key, none_value=None):
    return default_vars.get(key, none_value)

def get_plugin_value(plugin, key, none_value=None):
    p = user_vars.get(plugin, None)
    if p:
        return user_vars[plugin].get(key, none_value)
    return none_value