from utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from tkinter import filedialog
from utils import widget
from config import  config
import app
from tkinter import ttk
import os

def load(parent):
    ##################################################
    #                    Methods                     #
    ##################################################

    def _ask_dirname(e=None):
        d = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                           defaultextension='.yaml')
        if d:
            app.widgets['config_user_path'].config(state="normal")
            app.widgets['config_user_path'].set(d)
            app.widgets['config_user_path'].config(state='disabled')




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
    app.widgets['config_autoload'] = optionframe.insert_label_checkbox(
        name='config_autoload',
        label='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue=""
    )
    app.widgets['config_autosave'] = optionframe.insert_label_checkbox(
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
    print('config user path being loaded to settings {}'.format(config.config_user_path))
    dir_entry.configure(state='disabled', height=2)
    dir_entry.grid(column=0,row=1,sticky='news')
    app.widgets['config_user_path'] = dir_entry

    Tk.Button(
        master=dir_frame,
        text='Browse',
        command=_ask_dirname
    ).grid(column=1, row=1, sticky='news')

    optionframe.insert_button("Save",
                              command= lambda e=app.widgets['config_user_path'].get():
                            app.dump_user_setting(e))

    optionframe.insert_button("Save As...", command=save_config_as)

    optionframe.insert_button("Load", command=app.load_config)

    optionframe.insert_button(
        text='Default',
        command=optionframe.default
    )

    optionframe.insert_title(
        name='misc',
        text='Misc'
    )
    app.widgets['config_file_autodir'] = optionframe.insert_label_checkbox(
        name='config_file_autodir',
        label='Use trace file directory as default export directory (figures, data)',
        onvalue="1",
        offvalue=""
    )

    app.widgets['config_undo_stack'] = optionframe.insert_label_entry(
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





