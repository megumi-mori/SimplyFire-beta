from tkinter import ttk, filedialog
import tkinter as Tk

from config import config
from control_panel import font_bar

from menubar import menubar

from control_panel import detector, style, progress_bar, setting

from data_panel import graph_panel, table_panel
from utils.scrollable_option_frame import ScrollableOptionFrame


##################################################
#                Closing Sequence                #
##################################################
def _on_close():
    """
    The function is called when the program is closing (pressing X)
    Uses the config module to write out user-defined parameters
    :return: None
    """
    print('closing')
    tabs = [cp.detector_tab, cp.style_tab]
    # if cp.detector_tab.get_value('save_detector_preferences') == '1':
    #     tabs.append(cp.detector_tab)
    # if cp.style_tab.get_value('save_style_preferences') == '1':
    #     tabs.append(cp.style_tab)
    if cp.settings_tab.get_value('config_autosave') == '1':
        config.dump_user_config(cp.settings_tab.get_value('config_path'))
    config.dump_system_config()
    root.destroy()

def _update_config(filepath):
    pass

def open_trace():
    f = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf")])
    plot_area.open_trace(f)



root = Tk.Tk()
root.title('PyMini v{}'.format(config.version))
root.geometry('{}x{}'.format(config.geometry[0], config.geometry[1]))

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

pw = Tk.PanedWindow(
    root,
    orient=Tk.HORIZONTAL,
    showhandle=True,
    sashrelief=Tk.SUNKEN,
    handlesize=config.default_pw_handlesize
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
cp.detector_tab = detector.load(cp)
cp_notebook.add(cp.detector_tab, text='Detector')

# insert style options tab into control panel
cp.style_tab = style.load(cp)
cp_notebook.add(cp.style_tab, text='Plot')

# insert settings option tab into control panel
cp.settings_tab = setting.load(cp)
cp_notebook.add(cp.settings_tab, text='Settings')

# set up font adjustment bar
fb = font_bar.load(left)
fb.grid(column=0, row=1, sticky='news')

# set up progress bar
pb = progress_bar.ProgressBar(left)
pb.grid(column=0, row=2, stick='news')



##################################################
#                   DATA PANEL                   #
##################################################
# set up frame
right = Tk.Frame(pw, background = 'pink')
right.grid(column=0, row=0, sticky='news')
right.columnconfigure(0, weight=1)
right.rowconfigure(0, weight=1)

pw_2 = Tk.PanedWindow(
    right,
    orient=Tk.VERTICAL,
    showhandle=True,
    sashrelief=Tk.SUNKEN,
    handlesize=config.default_pw_handlesize
)


gp = graph_panel.load(pw_2)
gp.grid(column=0, row=0, sticky='news')
pw_2.add(gp)

plot_area = gp.plot

tp = table_panel.load(pw_2)
pw_2.add(tp)

pw_2.grid(column=0, row=0, sticky='news')
pw_2.paneconfig(gp, height=config.gp_height)


# finis up the pw setting:

pw.grid(column=0, row=0, sticky='news')
pw.add(left)
pw.add(right)

# adjust frame width
root.update()
pw.paneconfig(left, width=int(config.cp_width))






##################################################
#                    MENU BAR                    #
##################################################

# set up menubar
menubar = menubar.load_menubar(root)
root.config(menu=menubar)

# set up closing sequence
root.protocol('WM_DELETE_WINDOW', _on_close)

def load():
    return root