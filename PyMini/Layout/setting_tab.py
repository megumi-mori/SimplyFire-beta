
import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk, font

from PyMini.utils import custom_widgets
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
from PyMini.Layout import batch_popup
from PyMini.config import config
from PyMini import app
from PyMini.DataVisualizer import trace_display, param_guide
from PyMini.Backend import interface

import os

def load(parent):
    global widgets
    widgets = {}
    ##################################################
    #                    Methods                     #
    ##################################################

    def _ask_dirname(e=None):
        global widgets
        d = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                           defaultextension='.yaml')
        if d:
            widgets['config_user_path'].config(state="normal")
            widgets['config_user_path'].set(d)
            widgets['config_user_path'].config(state='disabled')




    ##################################################
    #                    Populate                    #
    ##################################################
    global frame
    frame = ScrollableOptionFrame(parent)
    global optionframe
    optionframe = frame.frame
    ##################################################
    #                Visual Options                  #
    ##################################################
    global s
    s = ttk.Style()

    optionframe.insert_title(
        name='visual_settings',
        text='Application Font'
    )
    widgets['font_size'] = optionframe.insert_label_optionmenu(
        name='font_size',
        text="Font size",
        options=range(9,20,1),
        command=set_fontsize
    )

    ##################################################
    #               Parameter Options                #
    ##################################################
    optionframe.insert_title(
        name='config_settings',
        text='Config Auto-save/load'
    )
    widgets['config_autoload'] = optionframe.insert_label_checkbox(
        name='config_autoload',
        text='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue="",
        # value=config.config_autoload
    )
    widgets['config_autosave'] = optionframe.insert_label_checkbox(
        name='config_autosave',
        text='Automatically save configurations at the end of this session',
        onvalue='1',
        offvalue=""
    )

    # auto_load directory panel

    dir_panel = optionframe.make_panel(separator=True)
    dir_frame = ttk.Frame(dir_panel)
    dir_frame.grid(column=0, row=0, sticky='news')
    dir_frame.columnconfigure(0, weight=1)
    ttk.Label(master=dir_frame,
             text='Configuration file path:').grid(column=0, row=0, sticky='news')
    global dir_entry
    dir_entry = custom_widgets.VarText(
        parent=dir_frame,
        name='config_user_path',
        value=config.config_user_path,
        default=config.default_config_user_path
    )
    dir_entry.configure(state='disabled', height=2)
    dir_entry.grid(column=0,row=1,sticky='news')
    widgets['config_user_path'] = dir_entry

    Tk.Button(
        master=dir_frame,
        text='Browse',
        command=_ask_dirname
    ).grid(column=1, row=1, sticky='news')


    # optionframe.insert_button("Save",
    #                           command= lambda e=widgets['config_user_path'].get():
    #                         app.dump_user_setting(e))
    optionframe.insert_button(text='Save',
                              command=save)

    optionframe.insert_button(text="Save As...", command=save_config_as)

    optionframe.insert_button(text="Load", command=load_config)

    optionframe.insert_button(
        text='Default',
        command=default
    )

    optionframe.insert_title(
        name='misc',
        text='Misc'
    )
    # widgets['config_file_autodir'] = optionframe.insert_label_checkbox(
    #     name='config_file_autodir',
    #     text='Use trace file directory as default export directory (figures, data)',
    #     onvalue="1",
    #     offvalue=""
    # )

    widgets['config_undo_stack'] = optionframe.insert_label_entry(
        name='config_undo_stack',
        text='Number of steps to store in memory for undo (Experimental)',
    )

    optionframe.insert_title(
        text='Window size'
    )
    widgets['window_width'] = optionframe.insert_label_entry(
        name='window_width',
        text='Window width (px)',
        value=config.geometry.split('x')[0],
        default=config.default_geometry.split('x')[0]
    )
    widgets['window_width'].bind('<Return>', apply_geometry)
    widgets['window_height'] = optionframe.insert_label_entry(
        name='window_height',
        text='Window height (px)',
        value=config.geometry.split('x')[1],
        default=config.default_geometry.split('x')[1]
    )
    widgets['window_height'].bind('<Return>', apply_geometry)
    widgets['cp_width'] = optionframe.insert_label_entry(
        name='cp_width',
        text='Control panel width (px)',
    )
    widgets['cp_width'].bind('<Return>', apply_geometry)
    widgets['gp_height'] = optionframe.insert_label_entry(
        name='gp_height',
        text='Graph panel height (px)'
    )
    widgets['gp_height'].bind('<Return>', apply_geometry)
    app.root.bind('<Configure>', change_geometry_entries)
    app.cp.bind('<Configure>', change_pw_entries)
    app.gp.bind('<Configure>', change_gp_entries)



    optionframe.insert_button(
        text='Apply',
        command=apply_geometry
    )
    set_fontsize(widgets['font_size'].get())
    global menu_var
    menu_var = Tk.BooleanVar()
    app.menubar.settings_menu.add_checkbutton(label='Open settings tab',
                                             command=toggle_tab_display,
                                             variable=menu_var,
                                             onvalue=True,
                                             offvalue=False)

    return frame

def toggle_tab_display(event=None):
    global menu_var
    if menu_var.get():
        app.config_cp_tab(frame, state='normal')
    else:
        app.config_cp_tab(frame, state='hidden')

def load_config(e=None):
    interface.focus()
    app.load_config()

def apply_geometry(e=None):
    app.root.geometry(f'{widgets["window_width"].get()}x{widgets["window_height"].get()}')
    app.pw.paneconfig(app.cp, width=int(widgets['cp_width'].get()))
    app.pw_2.paneconfig(app.gp, height=int(widgets['gp_height'].get()))
def change_geometry_entries(e=None):
    geometry = app.root.geometry().split('+')
    geometry[0] = geometry[0].split('x')
    widgets['window_width'].set(geometry[0][0])
    widgets['window_height'].set(geometry[0][1])
def change_gp_entries(e=None):
    widgets['gp_height'].set(app.gp.winfo_height())
def change_pw_entries(e=None):
    widgets['cp_width'].set(app.cp.winfo_width())
def default(e=None):
    interface.focus()
    optionframe.default(widgets=widgets)
def save_config_as():
    interface.focus()
    d = filedialog.asksaveasfilename(filetypes=[('yaml file', '*.yaml')], defaultextension='.yaml').strip()

    if d:
        try:
            app.dump_user_setting(d)
        except:
            save_config_as()
    return d

def save(event=None):
    interface.focus()
    print(app.custom_widgets)
    app.dump_user_setting(widgets['config_user_path'].get())


def set_fontsize(fontsize=None):
    interface.focus()
    if fontsize is None:
        fontsize=widgets['font_size'].get()
    fontsize=int(float(fontsize))
    fonts = [
        "TkDefaultFont",
        "TkTextFont",
        "TkMenuFont",
        "TkHeadingFont"
    ]
    for f in fonts:
        def_font = font.nametofont(f)
        def_font.configure(size=fontsize)
        s.configure('Treeview', rowheight=int(fontsize * 2))

    Tk.Text.configure(dir_entry, font=Tk.font.Font(size=fontsize))
    Tk.Text.configure(app.log_display.log_text, font=Tk.font.Font(size=fontsize))
    try:
        trace_display.ax.xaxis.get_label().set_fontsize(fontsize)
        trace_display.ax.yaxis.get_label().set_fontsize(fontsize)
        trace_display.ax.tick_params(axis='y', which='major', labelsize=fontsize)
        trace_display.ax.tick_params(axis='x', which='major', labelsize=fontsize)
    except:
        pass

    try:
        param_guide.ax.xaxis.get_label().set_fontsize(fontsize)
        param_guide.ax.yaxis.get_label().set_fontsize(fontsize)
        param_guide.ax.tick_params(axis='y', which='major', labelsize=fontsize)
        param_guide.ax.tick_params(axis='x', which='major', labelsize=fontsize)
        Tk.Text.configure(param_guide.msg_label, font=Tk.font.Font(size=fontsize))
    except:
        pass

    try:
        Tk.Text.configure(batch_popup.path_entry, font=Tk.font.Font(size=fontsize))
        Tk.Text.configure(batch_popup.file_entry, font=Tk.font.Font(size=fontsize))
        Tk.Text.configure(batch_popup.batch_log, font=Tk.font.Font(size=fontsize))
    except:
        pass