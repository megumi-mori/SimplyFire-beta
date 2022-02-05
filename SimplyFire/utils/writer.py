import os


def format_save_filename(filename: str, overwrite=True, suffix_num: int = 0):
    # reformat file name to avoid errors
    # filename should contain the extension
    if suffix_num > 0:
        fname = f'{os.path.splitext(filename)[0]}({suffix_num}){os.path.splitext(filename)[1]}'
    else:
        fname = filename
    if not overwrite:
        if os.path.exists(fname):
            return format_save_filename(filename, overwrite, suffix_num+1)
        else:
            return fname
    return fname
