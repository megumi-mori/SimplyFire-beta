import tkinter as Tk
from tkinter import ttk
from utils import widget
import pymini
import datetime



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
    global log_entry
    log_entry = widget.VarEntry(parent=insert_frame, name='custom_log', value='', default='')
    log_entry.grid(column=1, row=0, sticky='news')
    log_entry.configure(justify=Tk.LEFT)
    log_entry.bind('<Return>', user_update)

    test_button = Tk.Button(insert_frame, text='test')
    test_button.bind('<ButtonPress-1>', user_update)
    test_button.grid(column=2, row=0, sticky='news')

    button_frame = Tk.Frame(frame)
    button_frame.grid(column=0, row=2, sticky='news')

    copy_button = Tk.Button(button_frame, text='Copy', command=copy)
    copy_button.grid(column=0, row=0, stick='nws')

    log_text.insert(Tk.END, '{}\n'.format(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S')))



    return frame

def copy():
    pymini.root.clipboard_clear()
    pymini.root.clipboard_append(log_text.get())
    print(log_text.get())
    pymini.root.update()

def user_update(e=None):
    log_text.insert(Tk.END, '{} @user: {}\n'.format(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'), log_entry.get()))
    log_entry.set("")
    log_text.see(Tk.END)

def system_update(msg):
    log_text.insert(Tk.END, '{} @system:  {}\n'.format(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'), msg))
    log_text.see(Tk.END)

def open_update(filename):
    log_text.insert(Tk.END, '{} @open: {}\n'.format(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'), filename))
    log_text.see(Tk.END)

def search_update(msg):
    log_text.insert(Tk.END, '{} @search: {}\n'.format(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'), msg))
    log_text.see(Tk.END)




