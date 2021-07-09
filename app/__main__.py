from config import config

import tkinter as Tk
if __name__ == '__main__':
    splash = Tk.Tk()
    Tk.Label(splash, text='Now Loading').grid(column=0, row=0)
    splash.update()
    splash.after(0, splash.destroy)

    import pymini
    import Layout
    import utils
    import DataVisualizer
    import Backend

    splash.mainloop()

    root = pymini.load()

    ### testing purposes:
    # Backend.interface.open_trace('D:\\megum\\Documents\\GitHub\\PyMini\\test_recordings\\20112011-EJC test.abf')
    # root=pymini.root
    # pymini.plot_area.open_trace('D:\\megum\\Documents\\GitHub\\PyMini\\test_recordings\\19911002-2.abf')
    root.mainloop()