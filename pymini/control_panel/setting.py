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
    frame.insert_checkbox(
        name='config_autoload',
        label='Automatically save and load user configurations?',
        value=config.config_autoload,
        default=0
    )
    print('dir_panel')

    dir_panel = frame.make_panel(separator=True)
    dir_frame = ttk.Frame(dir_panel)
    dir_frame.grid(column=0, row=0, sticky='news')
    dir_frame.columnconfigure(0, weight=1)
    ttk.Label(master=dir_frame,
             text='Configuration file directory:').grid(column=0, row=0, sticky='news')

    # dir_entry = widget.LinkedEntry(
    #     parent=dir_panel,
    #     name="config_dir",
    #     value=config.convert_to_path(config.config_path),
    #     default=config.convert_to_path(config.default_config_path),
    #     validate_type="dir"
    # )
    dir_entry = Tk.Text(dir_frame)
    dir_entry.insert(1.0, config.convert_to_path(config.config_path))
    dir_entry.configure(state='disabled', height = 1)
    dir_entry.grid(column=0,row=1,sticky='news')
    frame.widgets['config_dir'] = dir_entry

    dir_button = Tk.Button(
        master=dir_frame,
        text='Browse',
        command=ask_dirname
    )
    dir_button.grid(column=1, row=1, sticky='news')

    ttk.Label(master=dir_frame,
              text='Configuration file name:').grid(column=0, row=2, sticky='news')

    file_entry = widget.LinkedEntry(
        parent=dir_frame,
        name='config_fname',
        value=config.config_fname,
        default=config.default_config_fname,
        validate_type="fname"
    )
    file_entry.widget.grid(column=0, row=3, sticky='news')

    frame.insert_button("Save Config As...")
    frame.insert_button("Load Config", command=config.load_config)

    return frame
    pass

def ask_dirname(e=None):
    dir = filedialog.askdirectory(mustexist=True)
    pymini.cp.settings_tab.widgets['config_dir'].widget.config(state="normal")
    pymini.cp.settings_tab.widgets['config_dir'].set(dir)
    pymini.cp.settings_tab.widgets['config_dir'].widget.config(state='disabled')

