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

# set up default parameters during module import

# Constants
global CONFIG_DIR # package config file path
CONFIG_DIR = pkg_resources.resource_filename('simplyfire', 'config/')
IMG_DIR = pkg_resources.resource_filename('simplyfire', 'img/')
TEMP_DIR = pkg_resources.resource_filename('simplyfire', 'temp/')
MODULES_DIR =pkg_resources.resource_filename('simplyfire', 'Modules/')

# Load defaults
default_vars = {}
system_vars = {}
user_vars = {}
keymap_vars = {}

print('loading default config')
default_config_path = os.path.join(CONFIG_DIR, "default_config.yaml") #config/default_config.yaml
with open(default_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        default_vars[c] = v
        if c[0:8] == 'default_' and 'config' not in c:
            globals()[c[8:]] = v
            user_vars[c[8:]] = v
        elif 'config' in c:
            globals()[c[8:]] = v
            system_vars[c[8:]] = v
print('completed')

def load():
    # Load user configurations
    global config_system_path
    config_system_path = os.path.join(CONFIG_DIR, default_config_system_path)
    try:
        with open(config_system_path) as f:
            configs = yaml.safe_load(f)
            for c, v in configs.items():
                globals()[c] = v
                # system_vars[c] = v
                user_vars[c] = v
    except:
        pass

    global config_keymap_path
    config_keymap_path = os.path.join(CONFIG_DIR, default_config_keymap_path)
    try:
        with open(config_keymap_path) as f:
            configs = yaml.safe_load(f)
            for c, v in configs.items():
                globals()[c] = v
                user_vars[c] = v
    except:
        pass

    global config_user_path
    if config_autoload == 1 or config_autoload == '1': # info stored in system_config
        try:
            d, f = os.path.split(config_user_path)
            if not os.path.isdir(d):
                config_user_path = os.path.join(CONFIG_DIR, config_user_path)
        except Exception as e:
            print('config load error: {}'.format(e))
            config_user_path = convert_to_path('')
        try:
            print('loading {}'.format(config_user_path))
            with open(config_user_path) as f:
                configs = yaml.safe_load(f)
                for c, v in configs.items():
                    globals()[c] = v
                    user_vars[c] = v
        except:
            pass
    print('config user path at config: {}'.format(config_user_path))


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

