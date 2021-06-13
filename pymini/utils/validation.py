valid_types = [
    "float",
    "int",
    "auto"
]
def validate(validate_type, value):
    types = validate_type.split('/')
    print(types)
    for type in types:
        if type == 'float':
            if is_float(value):
                return True
        elif type == 'int':
            if is_int(value):
                return True
        elif type == 'auto':
            if is_auto(value):
                return True
    return False
    if validate_type == 'float':
        return is_float(value)
    if validate_type == 'int':
        return is_int(value)

def is_auto(s):
    return (s.casefold()).__eq__("auto".casefold())

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

def is_color(s):
    pass