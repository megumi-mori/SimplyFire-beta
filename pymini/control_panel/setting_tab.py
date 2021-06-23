from utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from tkinter import filedialog
from utils import widget
from config import  config
import pymini
from tkinter import ttk
import os

def load(parent):
    ##################################################
    #                    Methods                     #
    ##################################################
    def _save_config():
        """
        Linked to the settings_tab "Save current config now" button
        Calls the config module's dump_user_config function with the current config path
        :return:
        """
        config.dump_user_config(frame.widgets['config_path'].get())
        pass

    def _ask_dirname(e=None):
        dir = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                           defaultextension='.yaml')
        if dir:
            frame.widgets['config_path'].widget.config(state="normal")
            frame.widgets['config_path'].set(dir)
            frame.widgets['config_path'].widget.config(state='disabled')

    def _save_config_as():
        dir = filedialog.asksaveasfilename(filetypes=[('yaml file', '*yaml')], defaultextension='.yaml')
        if dir:
            config.dump_user_config(dir)


    ##################################################
    #                    Populate                    #
    ##################################################

    frame = ScrollableOptionFrame(parent)
    ##################################################
    #               Parameter Options                #
    ##################################################
    frame.insert_title(
        name='config_settings',
        text='Config Auto-save/load'
    )
    pymini.widgets['config_autoload'] = frame.insert_label_checkbox(
        name='config_autoload',
        label='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue=""
    )
    pymini.widgets['config_autosave'] = frame.insert_label_checkbox(
        name='config_autosave',
        label='Automatically save configurations at the end of this session',
        onvalue='1',
        offvalue=""
    )

    # auto_load directory panel

    dir_panel = frame.make_panel(separator=True)
    dir_frame = ttk.Frame(dir_panel)
    dir_frame.grid(column=0, row=0, sticky='news')
    dir_frame.columnconfigure(0, weight=1)
    ttk.Label(master=dir_frame,
             text='Configuration file path:').grid(column=0, row=0, sticky='news')

    dir_entry = widget.VarText(
        parent=dir_frame,
        name='config_user_path',
        value=config.convert_to_path(config.config_user_path),
        default=config.convert_to_path(config.default_config_user_path)
    )
    dir_entry.configure(state='disabled', height=2)
    dir_entry.grid(column=0,row=1,sticky='news')
    pymini.widgets['config_user_path'] = dir_entry

    Tk.Button(
        master=dir_frame,
        text='Browse',
        command=_ask_dirname
    ).grid(column=1, row=1, sticky='news')

    frame.insert_button("Save current config now",
                        command= lambda e=pymini.widgets['config_user_path'].get():
                            config.dump_user_config(e))

    frame.insert_button("Save current config As...", command=_save_config_as)

    frame.insert_button("Load config from file...", command=config.load_config)

    frame.insert_button(
        text='Reset to default parameters',
        command=frame.default
    )

    frame.insert_title(
        name='misc',
        text='Misc'
    )
    pymini.widgets['config_file_autodir'] = frame.insert_label_checkbox(
        name='config_file_autodir',
        label='Use trace file directory as default export directory (figures, data)',
        onvalue="1",
        offvalue=""
    )


    return frame







