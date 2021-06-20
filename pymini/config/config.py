import yaml
import os
import inspect
import pymini
from tkinter import font, filedialog

import time


def convert_to_path(paths):
    """

    :param paths: path in a list
    :return:
    """
    if isinstance(paths, str):
        return paths
    p = [i if i != "DIR" else DIR for i in paths]
    return os.path.join(*p)



# Constants
global DIR
DIR = os.path.dirname(os.path.realpath(inspect.getfile(pymini)))

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
        if c[0:15] == 'system_default_':
            globals()[c[15:]] = v
            system_vars[c[15:]] = v

# Load user configurations

system_config_path = os.path.join(DIR, "config", "pymini_config.yaml")

try:
    with open(system_config_path) as f:
        configs = yaml.safe_load(f)
        for c, v in configs.items():
            globals()[c] = v
            system_vars[c] = v
except:
    pass

if config_autoload == 1 or config_autoload == '1':
    try:
        user_config_path = convert_to_path(config_path)
    except:
        user_config_path = convert_to_path('')
    try:
        print('loading {}'.format(user_config_path))
        with open(user_config_path) as f:
            configs = yaml.safe_load(f)
            for c, v in configs.items():
                globals()[c] = v
                user_vars[c] = v
    except:
        pass




def set_fontsize(fontsize):
    fonts = [
        "TkDefaultFont",
        "TkTextFont",
        "TkMenuFont",
        "TkHeadingFont"
    ]
    for f in fonts:
        def_font = font.nametofont(f)
        def_font.configure(size=fontsize)


def dump_user_config(path, tabs, ignore=None):
    print('Writing out configuration variables....')
    with open(path, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini user configurations\n")
        f.write("#################################################################\n")
        f.write("\n")
        pymini.pb.initiate()
        for i, t in enumerate(tabs):
            if t not in ignore:
                f.write(tabs[t].safe_dump_vars())
                pymini.pb.progress((i + 1) / (len(tabs.keys()) - len(ignore)))
        pymini.pb.clear()

        # f.write(yaml.safe_dump(user_vars))
    print('Completed')

def dump_system_config():
    print('Saving config options....')
    with open(system_config_path, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini system configurations\n")
        f.write("#################################################################\n")
        f.write("\n")

        f.write(pymini.tabs['settings_tab'].safe_dump_vars())
    print('Completed')


def load_config(e=None):
    f = filedialog.askopenfile()
    if not f:
        return None
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        for t in pymini.tabs:
            try:
                tabs[t].widgets[c].set(v)
                break
            except:
                pass



