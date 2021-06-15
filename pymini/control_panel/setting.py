from utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from tkinter import filedialog
from utils import widget
from config import  config
import pymini
from tkinter import ttk

def load(parent):

    frame = ScrollableOptionFrame(parent)
    ##################################################
    #               Parameter Options                #
    ##################################################

    dir_panel = frame.make_panel(separator=False)
    ttk.Label(master=dir_panel,
             text='Configuration file directory:').grid(column=0, row=0)

    dir_entry = widget.LinkedEntry(
        parent=dir_panel,
        name="config_dir",
        value=config.config_dir,
        default=config.default_config_dir,
        validate_type="dir"
    )
    dir_entry.widget.configure(state='disabled')
    dir_entry.grid(column=0,row=1,sticky='news')
    frame.widgets['config_dir'] = dir_entry

    dir_button = Tk.Button(
        master=dir_panel,
        text='Browse',
        command=ask_dirname
    )
    dir_button.grid(column=1, row=1, sticky='news')

    ttk.Label(master=dir_panel,
              text='Configuration file name:').grid(column=0, row=2)

    file_entry = widget.LinkedEntry(
        parent=dir_panel,
        name='config_fname',
        value=config.config_fname,
        default=config.default_config_fname,
        validate_type="fname"
    )

    frame.insert_checkbox(
        name='auto_load_config',
        label='Load user-config at start-up',
        value=0,
        default=0,
    )
    return frame
    pass

def ask_dirname(e=None):
    dir = filedialog.askdirectory(mustexist=True)
    pymini.cp.settings_tab.widgets['config_dir'].widget.config(state="normal")
    pymini.cp.settings_tab.widgets['config_dir'].set(dir)
    pymini.cp.settings_tab.widgets['config_dir'].widget.config(state='disabled')

