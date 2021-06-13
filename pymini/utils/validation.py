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