from utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from utils import widget
from config import  config
def load(parent):

    frame = ScrollableOptionFrame(parent)
    ##################################################
    #               Parameter Options                #
    ##################################################

    dir_panel = frame.make_panel(separator=False)
    frame.make_entry('test', value="hello")

    return frame
    pass
