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
import tkinter as Tk
from tkinter import filedialog, messagebox
from tkinter import ttk, font

from simplyfire.utils import custom_widgets
from simplyfire.utils.scrollable_option_frame import ScrollableOptionFrame
from simplyfire import app

import os


def load(parent):
    global widgets
    widgets = {}
    ##################################################
    #                    Methods                     #
    ##################################################


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
    widgets['system_autoload'] = optionframe.insert_label_checkbox(
        name='system_autoload',
        text='Automatically load configurations at the beginning of the next session',
        onvalue='1',
        offvalue="",
        value=app.config.get_value('system_autoload'),
        default=app.config.get_default_value('system_autoload')
    )
    widgets['system_autosave'] = optionframe.insert_label_checkbox(
        name='system_autosave',
        text='Automatically save configurations at the end of this session',
        onvalue='1',
        offvalue="",
        value=app.config.get_value('system_autosave'),
        default=app.config.get_default_value('system_autosave')
    )
    widgets['log_autosave'] = optionframe.insert_label_checkbox(
        name='log_autosave',
        text='Save log at the end of this session',
        onvalue='1',
        offvalue='',
        value=app.config.get_value('log_autosave'),
        default=app.config.get_default_value('log_autosave', '1')
    )

    # auto_load directory panel

    dir_panel = optionframe.make_panel(separator=True)
    dir_frame = ttk.Frame(dir_panel)
    dir_frame.grid(column=0, row=0, sticky='news')
    dir_frame.columnconfigure(0, weight=1)
    ttk.Label(master=dir_frame,
             text='Data directory:').grid(column=0, row=0, sticky='news')
    global dir_entry
    dir_entry = custom_widgets.VarText(
        parent=dir_frame,
        name='system_data_dir',
        value=app.config.get_value('system_data_dir'),
        default=app.config.get_default_value('system_data_dir')
    )
    dir_entry.configure(state='disabled', height=2)
    dir_entry.grid(column=0,row=1,sticky='news')
    widgets['system_data_dir'] = dir_entry

    Tk.Button(
        master=dir_frame,
        text='Browse',
        command=_ask_dirname
    ).grid(column=1, row=1, sticky='news')


    # optionframe.insert_button("Save",
    #                           command= lambda e=widgets['config_user_dir'].get():
    #                         app.dump_user_setting(e))
    # optionframe.insert_button(text='Save',
    #                           command=save)

    optionframe.insert_button(text="Save", command=save_config)
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


    widgets['system_undo_stack'] = optionframe.insert_label_entry(
        name='system_undo_stack',
        text='Number of steps to store in memory for undo (Experimental)',
        value=app.config.get_value('system_undo_stack'),
        default=app.config.get_default_value('system_undo_stack')
    )

    optionframe.insert_title(
        text='Window size'
    )
    widgets['window_width'] = optionframe.insert_label_entry(
        name='window_width',
        text='Window width (px)',
        value=app.config.get_value('geometry').split('x')[0],
        default=app.config.get_default_value('geometry').split('x')[0]
    )
    widgets['window_width'].bind('<Return>', apply_geometry)
    widgets['window_height'] = optionframe.insert_label_entry(
        name='window_height',
        text='Window height (px)',
        value=app.config.get_value('geometry').split('x')[1],
        default=app.config.get_default_value('geometry').split('x')[1]
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

    global menu_var
    menu_var = Tk.BooleanVar()
    def toggle_tab_display(event=None):
        if menu_var.get():
            app.cp_notebook.tab(frame, state='normal')
            try:
                app.cp_notebook.index(app.cp_notebook.select())
            except:
                app.cp_notebook.select(frame)
        else:
            app.cp_notebook.tab(frame, state='hidden')
    app.menubar.settings_menu.add_checkbutton(label='Settings tab',
                                             command=toggle_tab_display,
                                             variable=menu_var,
                                             onvalue=True,
                                             offvalue=False)

    for w in widgets:
        value = app.config.get_value(w, None)
        if value:
            widgets[w].set(value)
    set_fontsize(widgets['font_size'].get())
    return frame

def load_config(e=None, filename=None):
    app.interface.focus()
    if filename is None:
        filename = filedialog.askopenfilename()
    app.load_config(filename=filename)
    app.root.event_generate('<<LoadedConfig>>')

def apply_geometry(e=None):
    app.root.geometry(f'{widgets["window_width"].get()}x{widgets["window_height"].get()}')
    app.pw.paneconfig(app.cp, width=int(widgets['cp_width'].get()))
    app.pw_2.paneconfig(app.gp, height=int(widgets['gp_height'].get()))
def change_geometry_entries(e=None):
    try:
        geometry = app.root.geometry().split('+')
        geometry[0] = geometry[0].split('x')
        widgets['window_width'].set(geometry[0][0])
        widgets['window_height'].set(geometry[0][1])
    except:
        pass
def change_gp_entries(e=None):
    widgets['gp_height'].set(app.gp.winfo_height())
def change_pw_entries(e=None):
    widgets['cp_width'].set(app.cp.winfo_width())
def default(e=None):
    app.interface.focus()
    optionframe.default(widgets=widgets)

def save_config():
    app.interface.focus()
    app.dump_system_setting()
    app.dump_user_setting()
    app.dump_plugin_setting()

def save_config_as():
    app.interface.focus()
    d = filedialog.asksaveasfilename(filetypes=[('yaml file', '*.yaml')], defaultextension='.yaml').strip()

    if d:
        try:
            app.dump_user_setting(d)
        except:
            save_config_as()
    return d

def set_fontsize(fontsize=None):
    app.interface.focus()
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
        app.trace_display.ax.xaxis.get_label().set_fontsize(fontsize)
        app.trace_display.ax.yaxis.get_label().set_fontsize(fontsize)
        app.trace_display.ax.tick_params(axis='y', which='major', labelsize=fontsize)
        app.trace_display.ax.tick_params(axis='x', which='major', labelsize=fontsize)
    except:
        pass

    try:
        Tk.Text.configure(app.batch_popup.path_entry, font=Tk.font.Font(size=fontsize))
        Tk.Text.configure(app.batch_popup.file_entry, font=Tk.font.Font(size=fontsize))
        Tk.Text.configure(app.batch_popup.batch_log, font=Tk.font.Font(size=fontsize))
    except:
        pass

def _ask_dirname(e=None):
    global widgets
    # d = filedialog.asksaveasfilename(title='Select a directory', filetypes=[('yaml file', '*.yaml')],
                                       # defaultextension='.yaml')
    d = filedialog.askdirectory(title='Select a directory')
    if d:
        widgets['system_data_dir'].config(state="normal")
        widgets['system_data_dir'].set(d)
        widgets['system_data_dir'].config(state='disabled')
        if os.path.exists(os.path.join(d, 'user_config.yaml')):
            answer = messagebox.askyesnocancel(title='Load config?', message='A configuration file already exists in this directory.\nLoad configuration?\n(The file will be overwritten when the program closes.)')
            if answer is None:
                return
            if answer:
                load_config(filename = os.path.join(d, 'user_config.yaml'))
            if not answer:
                pass
        else:
            app.dump_user_setting()
            app.dump_system_setting()
            app.dump_plugin_setting()
