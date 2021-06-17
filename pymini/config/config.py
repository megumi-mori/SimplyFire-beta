import yaml
import os
import inspect
import pymini
from tkinter import font, filedialog
from control_panel import detector

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


version = "b0.1.0"

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
        "TkMenuFont"
    ]
    for f in fonts:
        def_font = font.nametofont(f)
        def_font.configure(size=fontsize)


def dump_user_config(path):
    print('Writing out configuration variables....')
    with open(path, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini user configurations\n")
        f.write("#################################################################\n")
        f.write("\n")
        pymini.pb.initiate()
        tabs = [pymini.cp.detector_tab, pymini.cp.style_tab]
        for i, t in enumerate(tabs):
            f.write(t.safe_dump_vars())
            pymini.pb.progress((i + 1) / len(tabs))
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

        f.write(pymini.cp.settings_tab.safe_dump_vars())
    print('Completed')


def load_config(e=None):
    f = filedialog.askopenfile()
    configs = yaml.safe_load(f)
    tabs = [pymini.cp.detector_tab, pymini.cp.style_tab]
    for c, v in configs.items():
        for t in tabs:
            try:
                t.widgets[c].set(v)
                break
            except:
                pass



