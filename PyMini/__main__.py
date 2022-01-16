import tkinter as Tk
import pkg_resources
from os.path import join
if __name__ == '__main__':
    splash = Tk.Tk()
    splash.title('SimpliFire')
    IMG_DIR = pkg_resources.resource_filename('PyMini', 'img/')
    splash.iconbitmap(join(IMG_DIR, 'logo.ico'))
    Tk.Label(splash, text='Now Loading').grid(column=0, row=0)
    splash.update()
    from PyMini import app
    splash.after(0, splash.destroy)
    splash.mainloop()

    root = app.load()
    root.focus_force()
    root.mainloop()