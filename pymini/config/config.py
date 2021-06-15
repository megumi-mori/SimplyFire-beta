import yaml
import os
import inspect
import pymini
from tkinter import font
from control_panel import detector

import time

version = "b0.1.0"

# Constants
DIR = os.path.dirname(os.path.realpath(inspect.getfile(pymini)))
print(DIR)

# Load user configurations
user_vars = {}
user_config_path = os.path.join(DIR, "config", "pymini_config.yaml")
try:
    with open(user_config_path) as f:
        configs = yaml.safe_load(f)
        for c, v in configs.items():
            globals()[c] = v
            user_vars[c] = v
except:
    pass

# Load defaults
default_vars = {}
default_config_path = os.path.join(DIR,"config", "default_config.yaml")
with open(default_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        default_vars[c] = v
        try:
            if c[0:8] == 'default_':
                var = user_vars[c[8:]]
        except:
            globals()[c[8:]] = v
            user_vars[c[8:]] = v



# global_font=font.Font.copy()


def set_fontsize(fontsize):
    fonts = [
        "TkDefaultFont",
        "TkTextFont",
        "TkMenuFont"
    ]
    for f in fonts:
        def_font = font.nametofont(f)
        def_font.configure(size=fontsize)



def dump_config(tabs):
    print('Writing out configuration variables....')
    with open(user_config_path, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini user configurations\n")
        f.write("#################################################################\n")
        f.write("\n")
        pymini.pb.initiate()
        for i, t in enumerate(tabs):
            f.write(t.safe_dump_vars())
            pymini.pb.progress((i + 1) / len(tabs))

        # f.write(yaml.safe_dump(user_vars))
    print('Completed')





# control panel

