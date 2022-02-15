"""
SimplyFire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tkinter as Tk
import pkg_resources
from os.path import join, dirname
from threading import Thread
import time

def load_splash():
    global splash
    splash = Tk.Toplevel()
    IMG_DIR = pkg_resources.resource_filename('simplyfire', 'img/')
    frameCount = 28
    frames = [Tk.PhotoImage(file=join(IMG_DIR, 'loading.gif'), format=f'gif -index {i}') for i in range(frameCount)]

    splash.title('SimplyFire')
    splash.wm_attributes('-toolwindow', True)

    label = Tk.Label(splash)
    label.configure(image=frames[0])
    # label.configure(image=Tk.PhotoImage(file=join('img', 'logo.png')))
    global app_start
    app_start =False
    def update(ind):
        global app_start
        frame = frames[ind]
        ind+= 1
        label.configure(image=frame)
        if ind < 28:
            splash.after(30, update, ind)
            
        splash.update()
    label.pack()
    splash.after(0, update, 0)


def load_app():
    from simplyfire import app

    # splash.after(0, splash.destroy)
    app.load(root, splash)



if __name__ == '__main__':
    root = Tk.Tk()
    root.withdraw()
    t = Thread(target = load_splash)
    root.after(0, t.start)
    t2 = Thread(target = load_app)
    root.after(0, t2.start)

    # splash.after(750, load_app)
    root.mainloop()

    # t.root.quit()




