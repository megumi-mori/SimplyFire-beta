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
        path = frame.widgets['config_path'].get()
        config.dump_user_config(path)
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
    frame.insert_label_checkbox(
        name='config_autoload',
        label='Automatically load configurations at the beginning of the next session',
        value=config.config_autoload,
        default=0
    )
    frame.insert_label_checkbox(
        name='config_autosave',
        label='Automatically save configurations at the end of this session',
        value=config.config_autosave,
        default=0
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
        name='config_path',
        value=config.convert_to_path(config.config_path),
        default=config.convert_to_path(config.system_default_config_path)
    )
    dir_entry.configure(state='disabled', height=2)
    dir_entry.grid(column=0,row=1,sticky='news')
    frame.widgets['config_path'] = dir_entry

    Tk.Button(
        master=dir_frame,
        text='Browse',
        command=_ask_dirname
    ).grid(column=1, row=1, sticky='news')

    frame.insert_button("Save current config now", command= _save_config)

    frame.insert_button("Save current config As...", command=_save_config_as)

    frame.insert_button("Load config from file...", command=config.load_config)

    frame.insert_button(
        text='Reset to default parameters',
        command=frame.default
    )

    return frame







