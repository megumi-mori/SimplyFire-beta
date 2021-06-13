import yaml
import os
import inspect
import pymini
from tkinter import font
from control_panel import detector


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
            user_vars[c[8:]]
        except:
            globals()[c[8:]] = v
            user_vars[c[8:]] = v



# global_font=font.Font.copy()


def set_fontsize(fontsize):
    def_font = font.nametofont("TkDefaultFont")
    def_font.configure(size=fontsize)
    def_font = font.nametofont("TkTextFont")
    def_font.configure(size=fontsize)

def dump_config(tabs):
    print('Writing out configuration variables....')
    with open(user_config_path, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini user configurations\n")
        f.write("#################################################################\n")
        f.write("\n")
        for t in tabs:
            f.write(t.safe_dump_vars())
        # f.write(yaml.safe_dump(user_vars))
    print('Completed')





# control panel

