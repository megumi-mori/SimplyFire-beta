import yaml
import os
import inspect
import pymini
from tkinter import font


version = "b0.1.0"

# Constants
DIR = os.path.dirname(os.path.realpath(inspect.getfile(pymini)))
print(DIR)

# Load defaults
default_vars = {}
default_config_path = os.path.join(DIR,"config", "default_config.yaml")
with open(default_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        default_vars[c] = v

user_vars = {}
user_config_path = os.path.join(DIR, "config", "pymini_config.yaml")
with open(user_config_path) as f:
    configs = yaml.safe_load(f)
    for c, v in configs.items():
        globals()[c] = v
        user_vars[c] = v

# global_font=font.Font.copy()


def set_fontsize(fontsize):
    def_font = font.nametofont("TkDefaultFont")
    def_font.configure(size=fontsize)
    def_font = font.nametofont("TkTextFont")
    def_font.configure(size=fontsize)



# control panel

