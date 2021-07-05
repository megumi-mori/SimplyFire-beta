import yaml
import os
import inspect
from tkinter import font, filedialog

import time


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





# Constants
global DIR
# DIR = os.path.dirname(os.path.realpath(inspect.getfile(pymini)))
DIR=os.getcwd()
# DIR=os.path.join(DIR, 'pymini')
print(DIR)

# Load defaults
default_vars = {}
system_vars = {}
user_vars = {}
default_config_path = os.path.join(DIR, "config", "default_config.yaml")
with open(default_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        default_vars[c] = v
        if c[0:8] == 'default_':
            globals()[c[8:]] = v
            user_vars[c[8:]] = v
        # if c[0:15] == 'system_default_':
        #     globals()[c[15:]] = v
        #     system_vars[c[15:]] = v
# Load user configurations

config_system_path = os.path.join(DIR, "config", "pymini_config.yaml")
try:
    with open(config_system_path) as f:
        configs = yaml.safe_load(f)
        for c, v in configs.items():
            print(c)
            globals()[c] = v
            # system_vars[c] = v
            user_vars[c] = v
except:
    pass

if config_autoload == 1 or config_autoload == '1':
    try:
        config_user_path = convert_to_path(config_user_path)
    except:
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





