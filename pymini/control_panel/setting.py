from utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from utils import widget
from config import  config
def load(parent):

    frame = ScrollableOptionFrame(parent)
    ##################################################
    #               Parameter Options                #
    ##################################################

    browse_panel = frame.insert_frame()
    browse_panel.grid_columnconfigure(0, weight =1)
    dir_var = Tk.StringVar()
    dir_entry = Tk.Entry(
        browse_panel,
        textvariable=dir_var,
        justify=Tk.RIGHT
    )
    dir_entry.grid(column=0, row=0, sticky='news')
    new_panel = frame.insert_frame()
    new_panel.grid_columnconfigure(0, weight=1)
    test_entry = widget.LinkedEntry(
        parent = new_panel,
        name = 'test',
        value = 'test',
        default = 'none',
        validate_type = "string"

    )
    test_entry.grid(column=0, row=0, sticky='news')

    return frame
    pass
