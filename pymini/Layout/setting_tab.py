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
        config.dump_user_config(optionframe.widgets['config_path'].get())
        pass

    def _ask_dirname(e=None):
        d = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                           defaultextension='.yaml')
        if d:
            optionframe.widgets['config_path'].widget.config(state="normal")
            optionframe.widgets['config_path'].set(d)
            optionframe.widgets['config_path'].widget.config(state='disabled')

    def _save_config_as():
        d = filedialog.asksaveasfilename(filetypes=[('yaml file', '*.yaml')], defaultextension='.yaml')
        if d:
            config.dump_user_config(d)


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
    pymini.widgets['config_autoload'] = optionframe.insert_label_checkbox(
        name='config_autoload',
        label='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue=""
    )
    pymini.widgets['config_autosave'] = optionframe.insert_label_checkbox(
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

    optionframe.insert_button("Save current \nconfig now",
                        command= lambda e=pymini.widgets['config_user_path'].get():
                            config.dump_user_config(e))

    optionframe.insert_button("Save current \nconfig As...", command=_save_config_as)

    optionframe.insert_button("Load config \nfrom file...", command=config.load_config)

    optionframe.insert_button(
        text='Reset to default \nparameters',
        command=optionframe.default
    )

    optionframe.insert_title(
        name='misc',
        text='Misc'
    )
    pymini.widgets['config_file_autodir'] = optionframe.insert_label_checkbox(
        name='config_file_autodir',
        label='Use trace file directory as default export directory (figures, data)',
        onvalue="1",
        offvalue=""
    )


    return frame







