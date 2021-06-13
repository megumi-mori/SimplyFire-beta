from tkinter import ttk
import tkinter as Tk

from config import config
from control_panel import font_bar

from menubar import menubar

from control_panel import detector
from utils.scrollable_option_frame import ScrollableOptionFrame
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



##################################################
#                 CONTROL PANEL                  #
##################################################

# set up frame
left = Tk.Frame(pw, background='blue')
left.grid(column=0, row=0, sticky='news')
left.grid_rowconfigure(0, weight=1)
left.grid_columnconfigure(0, weight=1)

# insert control panel in to left panel
cp = Tk.Frame(left, bg='purple')
cp.grid_columnconfigure(0, weight=1)
cp.grid_rowconfigure(0, weight=1)
cp.grid(column=0 ,row=0, sticky='news')

cp_notebook = ttk.Notebook(cp)
cp_notebook.grid(column=0, row=0, sticky='news')

# insert detector options tab into control panel
cp.detector_tab = ScrollableOptionFrame(cp)
detector.populate(cp.detector_tab)
cp_notebook.add(cp.detector_tab.get_frame(), text='Detector')

# insert style options tab into control panel



# set up font adjustment bar
fb = font_bar.load(left)
fb.grid(column=0, row=1, sticky='news')


##################################################
#                  DATA DISPLAY                  #
##################################################
# set up frame
right = Tk.Frame(pw, background = 'pink')
right.grid(column=1, row=0, sticky='news')



pw.add(left)
pw.add(right)

# adjust frame width
try:

    pw.paneconfig(left, width=config.cp_width)
    print('try')
except:
    root.update()
    print(root.winfo_width())
    pw.paneconfig(left, width=int(config.default_relative_cp_width * root.winfo_width()))


##################################################
#                    MENU BAR                    #
##################################################

# set up menubar
menubar = menubar.load_menubar(root)
root.config(menu=menubar)

# set up closing sequence
root.protocol('WM_DELETE_WINDOW', on_close)

def load():
    return root