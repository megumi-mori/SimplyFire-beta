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

from SimplyFire.utils.custom_widgets import DataTable
import tkinter as Tk
from tkinter import ttk

default_columns = ['filename', 'analysis','channel']

def load(parent):

    frame = Tk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    global dataframe
    dataframe = DataTable(frame)
    dataframe.grid(row=0, column=0, sticky='news')

    global table
    table = dataframe.table

    dataframe.define_columns(tuple(default_columns), sort=False)

    button_frame=Tk.Frame(frame)
    button_frame.grid(row=1, column=0, sticky='news')

    ttk.Button(button_frame, text='clear data (keep columns)', command=dataframe.clear).grid(column=0, row=0)
    ttk.Button(button_frame, text='Reset columns', command=erase).grid(column=1, row=0)
    ttk.Button(button_frame, text='Fit columns', command=dataframe.fit_columns).grid(column=2, row=0)

    dataframe.menu.add_command(label='Copy selection (Ctrl+c)', command=dataframe.copy)
    dataframe.menu.add_command(label='Select all (Ctrl+a)', command=dataframe.select_all)
    dataframe.menu.add_command(label='Delete (Del)', command = delete_selected)
    dataframe.menu.add_separator()
    dataframe.menu.add_command(label='Clear data', command=dataframe.clear)
    dataframe.menu.add_command(label='Reset columns', command=erase)
    dataframe.menu.add_command(label='Fit columns', command=dataframe.fit_columns)
    return frame

def erase(event=None):
    dataframe.clear()
    dataframe.define_columns(tuple(default_columns), sort=False)

def delete_selected(e=None):
    dataframe.delete_selected()
    # if len(dataframe.table.get_children()) == 0:
    #     dataframe.menu.entryconfig(0, state=Tk.DISABLED)

def report(data):
    dataframe.add(data)