import tkinter as Tk
from tkinter import ttk
from utils import widget
import pymini


def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    global log_text

    log_frame = Tk.Frame(frame)
    log_frame.grid_columnconfigure(0, weight=1)
    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid(column=0, row=0, sticky='news')

    log_text = widget.VarText(
        parent=log_frame,
        name='application_log',
        value='',
        default='',
        lock=True
    )

    log_text.configure(state='disabled')
    log_text.grid(column=0, row=0, sticky='news')

    vsb = ttk.Scrollbar(log_frame, orient=Tk.VERTICAL, command=log_text.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    log_text.configure(yscrollcommand=vsb.set)

    insert_frame = Tk.Frame(frame)
    insert_frame.grid_rowconfigure(0, weight=1)
    insert_frame.grid_columnconfigure(1, weight=1)

    insert_frame.grid(column=0, row=1, sticky='news')

    Tk.Label(insert_frame, text='Insert log:').grid(column=0, row=0, sticky='news')
    pymini.widgets['custom_log'] = widget.VarEntry(parent=insert_frame, name='custom_log', value='', default='')
    pymini.widgets['custom_log'].grid(column=1, row=0, sticky='news')
    pymini.widgets['custom_log'].configure(justify=Tk.LEFT)
    pymini.widgets['custom_log'].bind('<Return>', user_update)

    test_button = Tk.Button(insert_frame, text='test')
    test_button.bind('<ButtonPress-1>', user_update)
    test_button.grid(column=2, row=0, sticky='news')

    button_frame = Tk.Frame(frame)
    button_frame.grid(column=0, row=2, sticky='news')

    copy_button = Tk.Button(button_frame, text='Copy', command=copy)
    copy_button.grid(column=0, row=0, stick='nws')


    return frame

def copy():
    pymini.root.clipboard_clear()
    pymini.root.clipboard_append(log_text.get())
    print(log_text.get())
    pymini.root.update()

def user_update(e=None):
    log_text.insert(Tk.END, '@user: ')
    log_text.insert(Tk.END, '{}\n'.format(pymini.widgets['custom_log'].get()))
    pymini.widgets['custom_log'].set("")

system_update = lambda msg: log_text.insert(Tk.END, '@system:  {}\n'.format(msg))
open_update = lambda fname: log_text.insert(Tk.END, '@open: {}\n'.format(fname))


