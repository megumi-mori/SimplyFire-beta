"""
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

import tkinter as Tk
from SimplyFire import app
from SimplyFire.utils import scrollable_option_frame
def load():
    try:
        global window
        window.deiconify()
    except:
        create_window()

def create_window():
    global window
    window = Tk.Toplevel(app.root)
    window.geometry('600x600')
    # app.root.attributes('-disabled', True)
    window.lift()
    window.focus_set()
    window.protocol('WM_DELETE_WINDOW', _on_close)

    ##########################
    # Populate window
    ##########################

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    frame = scrollable_option_frame.ScrollableOptionFrame(window)
    frame.grid(row=0, column=0, sticky='news')
    optionframe = frame.frame

    optionframe.insert_title(text='Close application to bind keys')
    test_entry = optionframe.insert_label_entry(name="", label='test entry:', value='', default='')
    test_entry.bind('<KeyRelease>', show_key_name)


def show_key_name(e):
    print(e)


def _on_close():
    app.root.attributes('-disabled', False)
    window.withdraw()