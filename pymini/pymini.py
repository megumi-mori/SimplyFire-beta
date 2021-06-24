from tkinter import ttk
import tkinter as Tk

from config import config

from Layout import font_bar, menubar, detector_tab, style_tab, progress_bar, setting_tab, navigation_tab, sweep_tab, table_panel, graph_panel

from utils import widget



##################################################
#                    Methods                     #
##################################################
def test():
    data_table.add_event({
            't':0.001,
    })
    data_table.add_event({
        't':0.25,
    })
    data_table.add_event({
        't':0.02
    })
def _on_close():
    """
    The function is called when the program is closing (pressing X)
    Uses the config module to write out user-defined parameters
    :return: None
    """
    print('closing')
    plot.focus()
    if widgets['config_autosave'].get():
        config.dump_user_config(widgets['config_user_path'].get(), ignore=['config'])
    config.dump_system_config()
    root.destroy()



def get_value(key, tab=None):
    try:
        v = widgets[key].get()
        return v
    except:
        pass

def get_widget(key, tab=None):
    try:
        return widgets[key]
    except:
        pass


def set_value(key, value, tab=None):
    widgets[key].set(value)
    try:
        widgets[key].set(value)
        return
    except:
        raise
        None


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

widgets = {}

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

plot = tabs['graph_panel'].plot

tabs['table_panel'] = table_panel.load(pw_2, root)
pw_2.add(tabs['table_panel'])

# data_table = tabs['table_panel'].table

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

# insert detector_tab options tab into control panel
#need to check user defined mode
tabs['detector_tab'] = detector_tab.load(cp)
cp_notebook.add(tabs['detector_tab'], text='Detector')

#insert sweep tab
tabs['sweep_tab'] = sweep_tab.load(cp)

# insert navigation_tab tab into control panel
tabs['navigation_tab'] = navigation_tab.load(cp, root)
cp_notebook.add(tabs['navigation_tab'], text='Navigation')

# insert style_tab options tab into control panel
tabs['style_tab'] = style_tab.load(cp)
cp_notebook.add(tabs['style_tab'], text='Style')

# insert setting option tab into control panel
tabs['settings_tab'] = setting_tab.load(cp)
cp_notebook.add(tabs['settings_tab'], text='Setting')

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
plot.focus()

data_table.show_columns()
root.update()
# data_table.fit_columns()





##################################################
#                    MENU BAR                    #
##################################################

# set up menubar
menubar = menubar.load_menubar(root)
root.config(menu=menubar)

# set up closing sequence
root.protocol('WM_DELETE_WINDOW', _on_close)

test()

def load():
    return root



