
import tkinter as Tk
from tkinter import filedialog
from tkinter import ttk

from PyMini.utils import widget
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
from PyMini.config import config
import app

import os

def load(parent):
    global widgets
    widgets = {}
    ##################################################
    #                    Methods                     #
    ##################################################

    def _ask_dirname(e=None):
        global widgets
        widgets = {}
        d = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                           defaultextension='.yaml')
        if d:
            widgets['config_user_path'].config(state="normal")
            widgets['config_user_path'].set(d)
            widgets['config_user_path'].config(state='disabled')




    ##################################################
    #                    Populate                    #
    ##################################################

    frame = ScrollableOptionFrame(parent)

    optionframe = frame.frame
    ##################################################
    #               Parameter Options                #
    ##################################################
    optionframe.insert_title(
        name='config_settings',
        text='Config Auto-save/load'
    )
    widgets['config_autoload'] = optionframe.insert_label_checkbox(
        name='config_autoload',
        label='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue=""
    )
    widgets['config_autosave'] = optionframe.insert_label_checkbox(
        name='config_autosave',
        label='Automatically save configurations at the end of this session',
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

    dir_entry = widget.VarText(
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
    optionframe.insert_button('Save',
                              command=save)

    optionframe.insert_button("Save As...", command=save_config_as)

    optionframe.insert_button("Load", command=app.load_config)

    optionframe.insert_button(
        text='Default',
        command=lambda w=widgets:optionframe.default(widgets=w)
    )

    optionframe.insert_title(
        name='misc',
        text='Misc'
    )
    widgets['config_file_autodir'] = optionframe.insert_label_checkbox(
        name='config_file_autodir',
        label='Use trace file directory as default export directory (figures, data)',
        onvalue="1",
        offvalue=""
    )

    widgets['config_undo_stack'] = optionframe.insert_label_entry(
        name='config_undo_stack',
        label='Number of steps to store in memory for undo (Experimental)',
    )

    return frame

def save_config_as():
    d = filedialog.asksaveasfilename(filetypes=[('yaml file', '*.yaml')], defaultextension='.yaml')

    if d:
        try:
            app.dump_user_setting(d)
        except:
            save_config_as()
    return d

def save(event=None):
    print(app.widgets)
    app.dump_user_setting(widgets['config_user_path'].get())



