import pymini
from config import config

import control_panel
import utils
import menubar
import data_panel

if __name__ == '__main__':

    # root = pymini.load()
    root=pymini.root
    pymini.plot_area.open_trace('D:\\megum\\Documents\\GitHub\\PyMini\\test_recordings\\20112011-EJC test.abf')
    root.mainloop()