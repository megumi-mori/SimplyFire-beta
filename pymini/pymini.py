from tkinter import ttk
import tkinter as Tk

from config import config
from control_panel import control_panel, font_bar
print('pymini loaded')

def on_close():
    print('closing')
    root.destroy()

root = Tk.Tk()
root.title('PyMini v{}'.format(config.version))
try:
    root.geometry('{}x{}'.format(config.user_geometry[0], config.user_geometry[1]))
except:
    root.geometry('{}x{}'.format(config.default_geometry[0], config.default_geometry[1]))
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

pw = Tk.PanedWindow(
    root,
    orient=Tk.HORIZONTAL,
    showhandle=True,
    sashrelief=Tk.SUNKEN,
)

pw.grid(column=0, row=0, sticky='news')


# set up control panel frame
left = Tk.Frame(background='blue')
left.grid(column=0, row=0, sticky='news')
left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

    ## load control panel
cp, cp_tabs = control_panel.load(left)
cp.grid(column=0, row=0, sticky='news')

fb = font_bar.load(left)
fb.grid(column=0, row=1, sticky='news')

# set up data frame
right = Tk.Frame(pw, background = 'pink')
right.grid(column=1, row=0, sticky='news')

pw.add(left)
try:

    pw.paneconfig(left, width=config.user_cp_width)
    print('try')
except:
    root.update()
    print(root.winfo_width())
    pw.paneconfig(left, width=int(config.default_relative_cp_width * root.winfo_width()))
pw.add(right)

root.protocol('WM_DELETE_WINDOW', on_close)
def load():
    return root





