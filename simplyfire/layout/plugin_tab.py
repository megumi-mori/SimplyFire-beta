"""
UI to select plugins to activate

SimplyFire - Customizable analysis of electrophysiology data
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
from simplyfire import app
from tkinter import ttk, messagebox
import tkinter as Tk
from simplyfire.utils.scrollable_option_frame import ScrollableOptionFrame
from packaging.version import parse

changed = False
def load():
    global plugin_vars
    plugin_vars = {}
    global active_plugins
    active_plugins = []
    global window
    window = Tk.Toplevel(app.root)

    window.withdraw()
    window.geometry('400x600')
    app.menubar.plugin_menu.add_command(label='Manage plug-ins', command=window.deiconify)
    window.protocol('WM_DELETE_WINDOW', _on_close)

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)
    optionframe = ScrollableOptionFrame(window)
    optionframe.grid(column=0, row=0, sticky='news')

    global frame
    frame = optionframe.frame
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=0)

    label = Tk.Label(master=frame, text='name', relief='groove')
    label.grid(column=0, row=0, sticky='news')
    label = Tk.Label(master=frame, text='description', relief='groove')
    label.grid(column=1, row=0, sticky='news')
    label = Tk.Label(master=frame, text='on/off', relief='groove')
    label.grid(column=2, row=0, sticky='news')

    button_frame = Tk.Frame(window)
    button_frame.grid(column=0, row=1, sticky='news')
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    ttk.Button(button_frame, text='Apply', command=apply).grid(column=0, row=0, sticky='nse')
    ttk.Button(button_frame, text='Cancel', command=cancel).grid(column=1, row=0, sticky='nsw')

    _populate_plugins()


    active_plugins = [p for p in app.config.get_value('active_plugins', [])]

def apply():
    # check for requirements
    manifests = app.plugin_manager.manifests
    needed_plugins = []
    for plugin_name in plugin_vars.keys():
        if plugin_vars[plugin_name].get(): # activated plugin
            manifest = manifests[plugin_name]
            for r in manifest.get('requirements', []):
                # check if requirement is installed
                if not plugin_vars[r].get() and r not in needed_plugins:
                    needed_plugins.append(r)
    if len(needed_plugins) > 0:
        msg = 'Some required plugins are not activated.\n'
        msg += 'Turn on the following plugins?\n'
        msg+= ','.join(needed_plugins)
        answer = messagebox.askyesno('Warning', msg)
        window.lift()
        if answer:
            for r in needed_plugins:
                plugin_vars[r].set(True)
    messagebox.showwarning('Warning', 'Please reopen the software to apply changes')
    global active_plugins
    active_plugins = [plugin_name for plugin_name in plugin_vars.keys() if plugin_vars[plugin_name].get()]
    global changed
    changed=False
    window.withdraw()

def cancel():
    window.withdraw()
    for plugin_name, var in plugin_vars.items():
        if plugin_name in active_plugins:
            var.set(True)
        else:
            var.set(False)
    global changed
    changed = False

def _on_close():
    if changed:
        answer = messagebox.askyesno('Warning', 'Unsaved changes to the plugin list will be lost. Continue?')
        if not answer:
            window.lift()
            return
    cancel()
    # add commands to cancel the changes made on the window

def _populate_plugins():
    app.plugin_manager.load_manifests()
    i = 1
    # make plugin control GUI
    manifests = app.plugin_manager.manifests
    for plugin_name in manifests.keys():
        # load the plugin control GUI
        label = Tk.Label(master=frame, text=plugin_name, relief='groove')
        label.grid(column=0, row=i, sticky='news')

        description = manifests[plugin_name]['description']
        # add warning
        requirements = manifests[plugin_name].get('requirements', None)
        first = True
        if requirements:
            for r in requirements:
                if r not in manifests.keys():
                    if first:
                        description += '\nWarning: Missing requirements - '
                    description += f' {r},'

        if parse(manifests[plugin_name]['minimumCoreVersion']) > parse(app.config.get_value('version')):
            description += f'\nWarning: Minimum core requirement not met!'

        label = Tk.Text(master=frame, height=4)
        label.insert(Tk.INSERT,description)
        label.config(state='disabled')
        label.grid(column=1, row=i, sticky='news')

        var = Tk.BooleanVar(frame)
        plugin_vars[plugin_name] = var
        var.set(False)
        checkbutton = ttk.Checkbutton(frame, var=var, onvalue=True, offvalue=False, command=log_change)
        checkbutton.grid(column=2, row=i, sticky='news')
        i += 1

def get_plugins():
    return [plugin_name for plugin_name in plugin_vars.keys() if plugin_vars[plugin_name].get()]

def log_change(event=None):
    global changed
    changed = True





