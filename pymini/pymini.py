from tkinter import ttk
import tkinter as Tk

from config import config

from Layout import font_bar, menubar, detector_tab, style_tab, progress_bar, setting_tab, navigation_tab, sweep_tab, graph_panel
from DataVisualizer import data_display, log_display

from utils import widget

event_filename = None

##################################################
#                    Methods                     #
##################################################
def test():
    data_display.table.insert("", 'end', values=[{'t':0.0001}.get(i, None) for i in data_display.header2config], iid='0.0001')
    data_display.add({'amp':'123'})
    # data_table.add_event({
    #     't':0.25,
    # })
    # data_table.add_event({
    #     't':0.02
    # })
def _on_close():
    """
    The function is called when the program is closing (pressing X)
    Uses the config module to write out user-defined parameters
    :return: None
    """
    print('closing')
    # plot.focus()
    if widgets['config_autosave'].get():
        config.dump_user_config(ignore=['config_', '_log'])
    config.dump_system_config()
    root.destroy()

def get_value(key, tab=None):
    try:
        v = widgets[key].get()
        return v
    except Exception as e:
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

def load():

    global root
    root = Tk.Tk()
    root.title('PyMini v{}'.format(config.version))
    root.geometry('{}x{}'.format(config.geometry[0], config.geometry[1]))

    # root.bind('<KeyPress>', key)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.bind(config.key_reset_focus, lambda e: data_display.table.focus_set())

    global widgets
    widgets = {}

    pw = Tk.PanedWindow(
        root,
        orient=Tk.HORIZONTAL,
        showhandle=True,
        sashrelief=Tk.SUNKEN,
        handlesize=config.default_pw_handlesize
    )

    pw.grid(column=0, row=0, sticky='news')


    ##################################################
    #                   DATA PANEL                   #
    ##################################################

    # set up frame
    right = Tk.Frame(pw, background = 'pink')
    right.grid(column=0, row=0, sticky='news')
    right.columnconfigure(0, weight=1)
    right.rowconfigure(0, weight=1)

    dp_notebook = ttk.Notebook(right)
    dp_notebook.grid(column=0, row=0, sticky='news')

    global pw_2
    pw_2 = Tk.PanedWindow(
        right,
        orient=Tk.VERTICAL,
        showhandle=True,
        sashrelief=Tk.SUNKEN,
        handlesize=config.default_pw_handlesize
    )


    # must set up a graph object that can 'refresh' and 'plot' etc
    panel = graph_panel.load(pw_2)
    panel.grid(column=0, row=0, sticky='news')
    pw_2.add(panel)
    pw_2.paneconfig(panel, height=config.gp_height)

    panel = data_display.load(pw_2)
    pw_2.add(panel)
    pw_2.grid(column=0, row=0, sticky='news')

    dp_notebook.add(pw_2, text='data')

    log_frame = log_display.load(right)
    log_frame.grid(column=0, row=0, sticky='news')

    dp_notebook.add(log_frame, text='log')


    ##################################################
    #                 CONTROL PANEL                  #
    ##################################################

    # set up frame
    left = Tk.Frame(pw, background='blue')
    left.grid(column=0, row=0, sticky='news')
    left.grid_rowconfigure(0, weight=1)
    left.grid_columnconfigure(0, weight=1)

    # insert control panel in to left panel
    # cp = Tk.Frame(left, bg='purple')
    # cp.grid_columnconfigure(0, weight=1)
    # cp.grid_rowconfigure(0, weight=1)
    # cp.grid(column=0 ,row=0, sticky='news')

    global cp_notebook
    cp_notebook = ttk.Notebook(left)
    cp_notebook.grid(column=0, row=0, sticky='news')

    # insert detector_tab options tab into control panel
    #need to check user defined mode
    global tabs
    tabs = {}
    tabs['detector_tab'] = detector_tab.load(left)
    cp_notebook.add(tabs['detector_tab'], text='Mini')

    #insert sweep tab
    tabs['sweep_tab'] = sweep_tab.load(left)
    cp_notebook.add(tabs['sweep_tab'], text='Sweeps')

    # insert navigation_tab tab into control panel
    tabs['navigation_tab'] = navigation_tab.load(left, root)
    cp_notebook.add(tabs['navigation_tab'], text='Navi')

    # insert style_tab options tab into control panel
    tabs['style_tab'] = style_tab.load(left)
    cp_notebook.add(tabs['style_tab'], text='Style')

    # insert setting option tab into control panel
    tabs['settings_tab'] = setting_tab.load(left)
    cp_notebook.add(tabs['settings_tab'], text='Setting')

    # set focus rules
    for key in widgets:
        if type(widgets[key]) == widget.VarEntry:
            widgets[key].bind('<Return>', lambda e: data_display.table.focus_set(), add='+')
        if type(widgets[key]) == widget.VarCheckbutton:
            widgets[key].bind('<ButtonRelease>', lambda e: data_display.table.focus_set(), add='+')
        if type(widgets[key]) == widget.VarOptionmenu:
            widgets[key].bind('<ButtonRelease>', lambda e: data_display.table.focus_set(), add='+')


    # set up font adjustment bar
    fb = font_bar.load(left)
    fb.grid(column=0, row=1, sticky='news')

    # set up progress bar
    global pb
    # pb = progress_bar.ProgressBar(left)
    pb = ttk.Progressbar(left, length=100,
                         mode='determinate',
                         orient=Tk.HORIZONTAL)
    pb.grid(column=0, row=2, stick='news')

    # finis up the pw setting:

    pw.grid(column=0, row=0, sticky='news')
    pw.add(left)
    pw.add(right)

    # adjust frame width
    # root.update()
    pw.paneconfig(left, width=int(config.cp_width))


    ##################################################
    #                    MENU BAR                    #
    ##################################################

    # set up menubar
    menu = menubar.load_menubar(root)
    root.config(menu=menu)

    # set up closing sequence
    root.protocol('WM_DELETE_WINDOW', _on_close)

    # finalize the data viewer - table
    data_display.show_columns()
    root.update()
    data_display.fit_columns()

    return root



