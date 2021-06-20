from tkinter import ttk, filedialog
import tkinter as Tk

from config import config
from control_panel import font_bar

from menubar import menubar

from control_panel import detector, style, progress_bar, setting, navigation, sweep

from data_panel import graph_panel, table_panel

from utils import widget



##################################################
#                    Methods                     #
##################################################

def _on_close():
    """
    The function is called when the program is closing (pressing X)
    Uses the config module to write out user-defined parameters
    :return: None
    """
    print('closing')
    plot_area.focus()
    # if cp.detector_tab.get_value('save_detector_preferences') == '1':
    #     tabs.append(cp.detector_tab)
    # if cp.style_tab.get_value('save_style_preferences') == '1':
    #     tabs.append(cp.style_tab)
    if cp.settings_tab.get_value('config_autosave') == '1':
        config.dump_user_config(cp.settings_tab.get_value('config_path'), tabs)
    config.dump_system_config()
    root.destroy()

def open_trace():
    f = filedialog.askopenfilename(title='Open', filetypes=[('abf files', "*.abf")])
    if f:
        plot_area.open_trace(f)

def get_value(key, tab=None):
    try:
        return tabs[tab].get_value(key)
    except:
        for t in tabs:
            try:
                return tabs[t].get_value(key)
            except:
                pass
    return None

def get_widget(key, tab=None):
    try:
        return tabs[tab].get_widget(key)
    except:
        for t in tabs:
            try:
                return tabs[t].get_widget(key)
            except:
                pass
    return None

def set_value(key, value, tab=None):
    try:
        tabs[tab].set_value(key, value)
        print(tabs[tab].get_value(key))
        return True
    except:
        for t in tabs:
            try:
                tabs[t].set_value(key, value)
                return True
            except Exception as e:
                print(e)
                pass
    return False

def change_label(key, value, tab=None):
    try:
        tabs[tab].change_label(key, value)
        return True
    except:
        for t in tabs:
            try:
                tabs[t].change_label(key, value)
                return True
            except:
                pass
    return False

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
tabs = {}

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


tabs['graph_panel'] = graph_panel.load(pw_2)
tabs['graph_panel'].grid(column=0, row=0, sticky='news')
pw_2.add(tabs['graph_panel'])

plot_area = tabs['graph_panel'].plot

table_panel = table_panel.load(pw_2)
pw_2.add(table_panel)

pw_2.grid(column=0, row=0, sticky='news')
pw_2.paneconfig(tabs['graph_panel'], height=config.gp_height)

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
#need to check user defined mode
tabs['detector'] = detector.load(cp)
cp_notebook.add(tabs['detector'], text='Detector')

#insert sweep tab
tabs['sweep'] = sweep.load(cp)

# insert navigation tab into control panel
tabs['navigation'] = navigation.load(cp)
cp_notebook.add(tabs['navigation'], text='Navigation')

# insert style options tab into control panel
tabs['style'] = style.load(cp)
cp_notebook.add(tabs['style'], text='Style')

# insert settings option tab into control panel
cp.settings_tab = setting.load(cp)
cp_notebook.add(cp.settings_tab, text='Settings')

# set up font adjustment bar
fb = font_bar.load(left)
fb.grid(column=0, row=1, sticky='news')

# set up progress bar
pb = progress_bar.ProgressBar(left)
pb.grid(column=0, row=2, stick='news')

# finis up the pw setting:

pw.grid(column=0, row=0, sticky='news')
pw.add(left)
pw.add(right)

# adjust frame width
# root.update()
pw.paneconfig(left, width=int(config.cp_width))

# focus on plot
plot_area.focus()

table_panel.show_columns()




##################################################
#                    MENU BAR                    #
##################################################

# set up menubar
tabs['menu'] = widget.PseudoFrame()
menubar = menubar.load_menubar(root)
root.config(menu=menubar)

# set up closing sequence
root.protocol('WM_DELETE_WINDOW', _on_close)

def load():
    return root



