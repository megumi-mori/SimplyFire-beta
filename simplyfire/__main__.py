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

def load_splash():

    # Tk.Label(splash, text='Now Loading').grid(column=0, row=0)

    # canvas = Tk.Canvas(splash, width=650, height=480)
    # canvas.pack()
    # image = Tk.PhotoImage(file=join('img', 'loading_small_12fps.gif'))
    # c_image = canvas.create_image(0,0,anchor=Tk.NW, image=image)
    # frameCount=96
    # frames = [Tk.PhotoImage(file=join('img', 'loading_small_12fps.gif'), format=f'gif -index {i}') for i in
    #           range(frameCount)]
    # def update(ind):
    #     image = frames[ind]
    #     ind += 1
    #     if ind == frameCount:
    #         ind=20
    #     canvas.itemconfigure(c_image, image=image)
    #     try:
    #         splash.after(1000, update, ind)
    #     except:
    #         pass
    IMG_DIR = pkg_resources.resource_filename('simplyfire', 'img/')

    # method 1:
    global splash
    splash.title('SimplyFire')
    # splash = Tk.Tk()
    splash.wm_attributes('-toolwindow', True)

    # frameCount = 42
    # frames = [Tk.PhotoImage(file=join(IMG_DIR,'loading_12fps.gif'), format= f'gif -index {i}') for i in range(frameCount)]
    # label = Tk.Label(splash)
    # # label.configure(image=Tk.PhotoImage(file=join('img', 'logo.png')))
    # global app_start
    # app_start =False
    # def update(ind):
    #     global app_start
    #     frame = frames[ind]
    #     ind+= 1
    #     if ind==frameCount:
    #         ind =30
    #     label.configure(image=frame)
    #     if ind > 30:
    #         splash.after(200, update, ind)
    #     else:
    #         splash.after(12, update, ind)
    #     splash.update()
    # label.pack()

    frameCount = 28
    frames = [Tk.PhotoImage(file=join(IMG_DIR,'loading.gif'), format= f'gif -index {i}') for i in range(frameCount)]
    label = Tk.Label(splash)
    # label.configure(image=Tk.PhotoImage(file=join('img', 'logo.png')))
    global app_start
    app_start =False
    def update(ind):
        global app_start
        frame = frames[ind]
        ind+= 1
        if ind==frameCount:
            ind -=1
        label.configure(image=frame)
        splash.after(30, update, ind)
        splash.update()
    label.pack()
    splash.after(0, update, 0)
    # # method 2: (just a logo)
    # global splash
    # splash = Tk.Tk()
    # splash.title('SimpliFire')
    # splash.geometry('600x400')
    # splash.grid_columnconfigure(0, weight=1)
    # splash.grid_rowconfigure(0, weight=1)
    #
    # frameCount = 19
    # global frames
    # frames = [Tk.PhotoImage(file=join('img','loading_small_12fps.gif'), format= f'gif -index {i}') for i in range(frameCount)]
    #
    # label = Tk.Label(splash)
    # label.configure(image=frames[18])
    # label.pack(fill='both')
    # splash.update()

def load_app():
    from simplyfire import app

    # splash.after(0, splash.destroy)
    app.load(splash)



if __name__ == '__main__':

    # t = Thread(target=load_splash)
    # t.start()

    # IMG_DIR = pkg_resources.resource_filename('PyMini', 'img/')
    # splash.iconbitmap(join('img', 'logo.ico'))
    # # method 1:
    # frameCount = 96
    # frames = [Tk.PhotoImage(file=join('img','loading_small_12fps.gif'), format= f'gif -index {i}') for i in range(frameCount)]
    # label = Tk.Label(splash)
    # def update(ind):
    #     frame = frames[ind]
    #     ind+= 1
    #     if ind==frameCount:
    #         ind = 20
    #     label.configure(image=frame)
    #     splash.after(12, update, ind)
    # label.pack()
    # splash.after(0, update,0)

    # load_splash()
    t = Thread(target = load_splash)
    global splash
    splash = Tk.Tk()
    splash.after(0, t.start)
    t2 = Thread(target = load_app)
    splash.after(0, t2.start)
    # splash.after(750, load_app)
    splash.mainloop()


    # t.root.quit()



