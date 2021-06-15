from matplotlib import colors
import os

valid_types = [
    "float",
    "int",
    "auto",
    "dir"
]


def validate(validate_type, value):
    if validate_type is None:
        return True
    if len(validate_type) == 0:
        return True
    types = validate_type.split('/')

    for type in types:
        if type == 'float':
            if is_float(value):
                return True
        elif type == 'int':
            if is_int(value):
                return True
        elif type == 'color':
            if is_color(value):
                return True
        elif type == 'auto':
            if is_auto(value):
                return True
        elif type == "string":
            return True
        elif type == "dir":
            if os.path.isdir(value):
                return True
        else:
            pass
    return False


def is_auto(s):
    return (s.casefold()).__eq__("auto".casefold())


def is_color(s):
    return colors.is_color_like(s)


def is_int(s):
    try:
        return s.isnumeric()
    except:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except:
        return False

