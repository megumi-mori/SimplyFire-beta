import yaml
import os
import pkg_resources

# set up default parameters during module import

# Constants
global CONFIG_DIR # package config file path
CONFIG_DIR = pkg_resources.resource_filename('PyMini', 'config/')

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

