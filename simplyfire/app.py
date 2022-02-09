"""
simplyfire - Customizable analysis of electrophysiology data
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
from tkinter import ttk, messagebox
import tkinter as Tk
import yaml
from PIL import Image
import os
from simplyfire.utils import custom_widgets
from simplyfire.backend import interpreter, interface
from simplyfire.config import config
# from PyMini.Layout import detector_tab, style_tab, setting_tab, navigation_tab, \
#     sweep_tab, graph_panel, continuous_tab, adjust_tab, evoked_tab, batch_popup, menubar,\
#     compare_tab
from simplyfire.layout import menubar, graph_panel, setting_tab, batch_popup, log_display, results_display, trace_display, results_display, log_display
# from PyMini.DataVisualizer import data_display, log_display, evoked_data_display, results_display, trace_display, param_guide
import importlib
# debugging
import time




event_filename = None
widgets = {}

##################################################
#                    Methods                     #
##################################################

def _on_close():
    """
    The function is called when the program is closing (pressing X)
    Uses the config module to write out user-defined parameters
    :return: None
    """
    global widgets
    # if widgets['config_autosave'].get():
    # try:
    dump_user_setting()
    # except:
    #     Tk.messagebox.showinfo(title='Error', message='Error while writing out user preferences.\n Please select a new filename.')
    #     f = setting_tab.save_config_as()
    #     if f:
    #         widgets['config_user_path'].set(f)

    dump_config_var(key='key_', filename=config.config_keymap_path, title='Keymap')
    dump_system_setting()
    root.destroy()
    app_root.destroy()

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


# def change_label(key, value, tab=None):
#     try:
#         tabs[tab].change_label(key, value)
#         return True
#     except:
#         for t in tabs:
#             try:
#                 tabs[t].change_label(key, value)
#                 return True
#             except:
#                 pass
#     return False

def load(splash):
    # debugging:
    global t0
    t0 = time.time()
    global app_root
    app_root = splash
    # tracemalloc.start()
    config.load()
    global root
    global loaded
    loaded = False
    root = Tk.Toplevel()
    root.withdraw()
    root.title('simplyfire v{}'.format(config.version))
    IMG_DIR = config.IMG_DIR
    root.iconbitmap(os.path.join(IMG_DIR, 'logo_bw.ico'))
    if config.zoomed:
        root.state('zoomed')
    global menu
    menu = Tk.Menu(root)
    root.config(menu=menu)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frame = Tk.Frame(root, bg='red')
    frame.grid(column=0, row=0, sticky='news')

    # root.bind(config.key_reset_focus, lambda e: data_display.table.focus_set())


    global arrow_img
    arrow_img = Image.open(os.path.join(IMG_DIR, 'arrow.png'))

    global widgets
    global pw
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
    global gp
    gp = graph_panel.load(root)
    root.update_idletasks()
    pw_2.add(gp)
    pw_2.paneconfig(gp, height=config.gp_height)

    global data_notebook
    data_notebook = ttk.Notebook(pw_2)
    data_notebook.bind('<ButtonRelease>', interface.focus, add='+')



    pw_2.add(data_notebook)
    dp_notebook.add(pw_2, text='trace')

    log_frame = log_display.load(root)
    dp_notebook.add(log_frame, text='log')

    results_frame = results_display.load(root)
    dp_notebook.add(results_frame, text='results', sticky='news')


    ##################################################
    #                 CONTROL PANEL                  #
    ##################################################

    # set up frame
    global cp
    cp = Tk.Frame(pw, background='blue')
    cp.grid(column=0, row=0, sticky='news')
    cp.grid_rowconfigure(0, weight=1)
    cp.grid_columnconfigure(0, weight=1)

    global cp_notebook
    cp_notebook = ttk.Notebook(cp)
    cp_notebook.grid(column=0, row=0, sticky='news')
    cp_notebook.bind('<<NotebookTabChanged>>', synch_tab_focus, add='+')
    cp_notebook.bind('<ButtonRelease>', interface.focus, add='+')

    #############################################################
    # Insert custom tabs here to include in the control panel
    #############################################################
        # cp_tab_details = {
    #     'mini': {'module': detector_tab, 'text': 'Analysis', 'partner': ['evoked'], 'name':'detector_rab'},
    #     'evoked': {'module': evoked_tab, 'text': 'Analysis', 'partner': ['mini'], 'name':'evoked_tab'},
    #     'continuous': {'module': continuous_tab, 'text': 'View', 'partner': ['overlay', 'compare'], 'name':'continuous_tab'},
    #     'overlay': {'module': sweep_tab, 'text': 'View', 'partner': ['continuous', 'compare'], 'name':'sweep_tab'},
    #     'compare':{'module': compare_tab, 'text': 'View', 'partner': ['continuous', 'overlay'], 'name':'compare_tab'},
    #     'adjust': {'module': adjust_tab, 'text': 'Adjust', 'partner': [], 'name':'adjust_tab'},
    #     'navigation': {'module': navigation_tab, 'text': 'Navi', 'partner': [], 'name':'navigation_tab'},
    #     'style':{'module': style_tab, 'text': 'Style', 'partner': [], 'name':'style_tab'},
    #     'setting':{'module': setting_tab, 'text': 'Setting', 'partner': [], 'name':'setting_tab'}
    # }
    #
    # for i, t in enumerate(cp_tab_details):
    #     cp_tab_details[t]['tab'] = cp_tab_details[t]['module'].load(cp)
    #     cp_notebook.add(cp_tab_details[t]['tab'], text=cp_tab_details[t]['text'])
    #     cp_tab_details[t]['index'] = i
    #     globals()[cp_tab_details[t]['name']] = cp_tab_details[t]['module']


    # root.bind('<Configure>', print)

    # test = StyleTab(left, __import__(__name__), interface)
    # cp_notebook.add(test, text='test')

    for k, v in graph_panel.widgets.items():
        widgets[k] = v

    # get reference to widgets
    # for module in [detector_tab, evoked_tab, adjust_tab, navigation_tab, style_tab, setting_tab, graph_panel]:
    #     for k, v in module.widgets.items():
    #         widgets[k] = v
    # setting_tab.set_fontsize(widgets['font_size'].get())
    # # set focus rules
    for key in widgets:
        if type(widgets[key]) == custom_widgets.VarEntry:
            widgets[key].bind('<Return>', lambda e: interface.focus(), add='+')
        if type(widgets[key]) == custom_widgets.VarCheckbutton:
            widgets[key].bind('<ButtonRelease>', lambda e: interface.focus(), add='+')
        if type(widgets[key]) == custom_widgets.VarOptionmenu:
            widgets[key].bind('<ButtonRelease>', lambda e: interface.focus(), add='+')
        if type(widgets[key]) == custom_widgets.VarCheckbutton:
            widgets[key].bind('<ButtonRelease>', lambda e: interface.focus(), add='+')

    # set up font adjustment bar
    # fb = font_bar.load(left, config.font_size)
    # widgets['font_size'] = font_bar.font_scale
    # fb.grid(column=0, row=1, sticky='news')

    # set up progress bar
    global pb
    # pb = progress_bar.ProgressBar(left)
    pb = ttk.Progressbar(cp, length=100,
                         mode='determinate',
                         orient=Tk.HORIZONTAL)
    pb.grid(column=0, row=2, stick='news')

    # finis up the pw setting:

    pw.grid(column=0, row=0, sticky='news')
    pw.add(cp)
    pw.add(right)

    # adjust frame width
    root.update()
    pw.paneconfig(cp, width=int(config.cp_width))

    ##################################################
    #                    MENU BAR                    #
    ##################################################

    # set up menubar
    menubar.load(menu)

    globals()['menubar'] = menubar

    for k, v in menubar.widgets.items():
        widgets[k] = v

    setting_tab.load(root)
    for k, v in setting_tab.widgets.items():
        widgets[k] = v

    batch_popup.load()
    menubar.batch_menu.add_command(label='Batch Processing', command=batch_popup.show)

    global control_panel_dict
    control_panel_dict = {}

    global data_notebook_dict
    data_notebook_dict = {}

    global modules
    modules = {}

    with open(os.path.join(config.CONFIG_DIR, 'modules.yaml')) as f:
        module_list = yaml.safe_load(f)['modules']
        for module_name in module_list:
            load_module(module_name)


            # except Exception as e:
            #     print(e)
            #     pass
        # # only show one tab at a time
        # global data_tab_details
        # data_tab_details = {
        #     'mini': {'module': data_display, 'text': 'Mini Data'},
        #     'evoked': {'module': evoked_data_display, 'text': 'Evoked Data'}
        # }
        # for i, t in enumerate(data_tab_details):
        #     data_tab_details[t]['tab'] = data_tab_details[t]['module'].load(root)
        #     data_notebook.add(data_tab_details[t]['tab'], text=data_tab_details[t]['text'])
        #     data_tab_details[t]['index'] = i
    # set up closing sequence

    root.protocol('WM_DELETE_WINDOW', _on_close)

    # set up event bindings
    interpreter.initialize()

    for modulename in config.start_module:
        try:
            modules[modulename].menu_var.set(True)
        except: # module removed from module-list
            pass
    for module_name, module in modules.items():
        module.update_module_display()

    cp_notebook.add(setting_tab.frame, text='Setting', state='hidden')
    root.update()
    ## root2 = root
    loaded = True
    root.event_generate('<<LoadCompleted>>')

    root.focus_force()
    interface.focus()
    splash.withdraw()

    root.deiconify()
    # # finalize the data viewer - table
    root.geometry(config.geometry)
    if config.user_config_load_error is not None:
        messagebox.showwarning('Warning', f'Error while loading user settings: {config.user_config_load_error}\nReverting to default configurations.')
    return None



def load_module(module_name):
    global modules
    if modules.get(module_name, None):
        return
    # load modules
    module_path = os.path.join(config.MODULES_DIR, module_name)
    try:
        module = importlib.import_module(f'simplyfire.modules.{module_name}.{module_name}')
    except ModuleNotFoundError:
        log_display.log(f'Load error. Module {module_name} does not have file {module_name}.py', '@Load')
        return

    with open(os.path.join(module_path, 'config.yaml'), 'r') as config_file:
        module_config = yaml.safe_load(config_file)
    if module_config.get('dependencies', None):
        # has dependencies
        for req_module_name in module_config['dependencies']:
            load_module(req_module_name)
    try:
        parent_module = getattr(module, 'Module', None)()
    except TypeError as e:
        log_display.log(f'Load error. Module {module_name}: {e}', '@Load')
        return
    modules[module_name] = parent_module
def get_tab_focus():
    focus = {}
    focus['control_panel'] = cp_notebook.select()
    focus['data_panel'] = data_notebook.select()
    return focus

def get_module(module_name, component=None):
    module = modules.get(module_name, None)
    if not module:
        return None
    if component:
        return module.get(component, None)
    else:
        return module

def synch_tab_focus(event=None):
    try:
        module = root.children.get(cp_notebook.select().split('.')[-1]).module
        module.select()
    except:
        pass

def advance_progress_bar(value, mode='determinate'):
    if mode == 'determinate':
        pb['value'] += value
    else:
        pb['value'] = (pb['value'] + value) % 100
    pb.update()
def set_progress_bar(value):
    global pb
    pb['value'] = value
    pb.update()

def clear_progress_bar():
    global pb
    pb['value'] = 0
    pb.update()

def dump_user_setting(filename=None):
    global widgets
    ignore = ['config_', '_log', 'temp_']
    print('Writing out configuration variables....')
    if filename is None:
        filename = os.path.join(widgets['config_user_dir'].var.get().strip(), 'user_config.yaml')
        # filename = os.path.join(pkg_resources.resource_filename('PyMini', 'config'), 'test_user_config.yaml')
    with open(filename, 'w') as f:
        print('writing dump user config {}'.format(filename))
        f.write("#################################################################\n")
        f.write("# PyMini user configurations\n")
        f.write("#################################################################\n")
        f.write("\n")
        # pymini.pb.initiate()
        d = {}
        for key in widgets.keys():
            try:
                for ig in ignore:
                    if ig in key:
                        break
                else:
                    d[key] = widgets[key].get()
            except:
                d[key] = widgets[key].get()
        global cp
        if loaded:
            d['zoomed'] = root.state() == 'zoomed'
            if not root.state() == 'zoomed':
                d['cp_width'] = cp.winfo_width()
                d['gp_height'] = gp.winfo_height()
                d['geometry'] = root.geometry().split('+')[0]

        # d['compare_color_list'] = config.compare_color_list
        # d['compare_color_list'][:len(compare_tab.trace_list)] = [c['color_entry'].get() for c in compare_tab.trace_list]
        d['start_module'] = [name for name, module in modules.items() if module.menu_var.get()]
        for modulename, module in modules.items():
            d[modulename] = dict([(key, var.get()) for key, var in module.widgets.items() if 'key_' not in key])
            for key in [k for k in module.defaults.keys() if 'key_' in k]:
                setattr(config, key, module.defaults[key])

        f.write(yaml.safe_dump(d))
        # pymini.pb.clear()

        # f.write(yaml.safe_dump(user_vars))
    print('Completed')

def dump_system_setting():
    print('Saving config options....')
    with open(config.config_system_path, 'w') as f:
        print('dumping system config {}'.format(config.config_system_path))
        f.write("#################################################################\n")
        f.write("# PyMini system configurations\n")
        f.write("#################################################################\n")
        f.write("\n")

        # f.write(yaml.safe_dump(dict([(key, widgets[key].get()) for key in widgets if 'config' in key])))
        # f.write(yaml.safe_dump(dict([(n, getattr(config, n)) for n in config.user_vars if 'config' in n])))
        f.write(yaml.safe_dump(dict([(key, value.get()) for key, value in widgets.items() if 'config' in key])))

    print('Completed')

def dump_config_var(key, filename, title=None):
    print('Saving "{}" config values...'.format(key))
    print(filename)
    with open(filename, 'w') as f:
        f.write("#################################################################\n")
        f.write("# PyMini {} configurations\n".format(title))
        f.write("#################################################################\n")
        f.write("\n")
        f.write(yaml.safe_dump(dict([(n, getattr(config, n)) for n in config.user_vars if key in n])))
    print('Completed')

def load_config(filename=None):
    if not filename:
        return None
    with open(filename) as f:
        loaded_configs = yaml.safe_load(f)
    for key in widgets.keys():
        try:
            value = loaded_configs.get(key, None)
            if value:
                widgets[key].set(value)
        except:
            pass
    for modulename in modules:
        for key in modules[modulename].widgets.keys():
            try:
                value = loaded_configs[modulename].get(key, None)
                if value:
                    modules[modulename].widgets[key].set(value)
            except:
                pass

def print_time_lapse(msg=""):
    global t0
    try:
        print(f"{msg}: {time.time() - t0}")
    except:
        print(msg)
        pass
    t0 = time.time()