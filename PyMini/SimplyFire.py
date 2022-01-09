from PyMini import app

import tkinter as Tk
if __name__ == '__main__':
    splash = Tk.Tk()
    Tk.Label(splash, text='Now Loading').grid(column=0, row=0)
    splash.update()
    splash.after(0, splash.destroy)

    splash.mainloop()

    root = app.load()
    root.mainloop()