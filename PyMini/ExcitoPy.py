import pymini
from config import config

import Layout
import utils
import DataVisualizer
import Backend

if __name__ == '__main__':

    root = pymini.load()
    ### testing purposes:
    Backend.interface.open_trace('D:\\megum\\Documents\\GitHub\\PyMini\\test_recordings\\20112011-EJC test.abf')
    # root=pymini.root
    # pymini.plot_area.open_trace('D:\\megum\\Documents\\GitHub\\PyMini\\test_recordings\\19911002-2.abf')
    root.mainloop()