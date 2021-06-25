import tkinter as Tk
from utils import widget
import pymini


def load(parent):
    frame = Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    log_text = widget.VarText(
        parent=frame,
        name='application_log',
        value='',
        default=''
    )
    pymini.widgets['application_log'] = log_text

    log_text.configure(state='disabled')
    log_text.grid(column=0, row=0, sticky='news')

    insert_frame = Tk.Frame(frame)
    insert_frame.grid_rowconfigure(0, weight=1)
    insert_frame.grid_columnconfigure(1, weight=1)

    insert_frame.grid(column=0, row=1, sticky='news')

    Tk.Label(insert_frame, text='Insert log:').grid(column=0, row=0, sticky='news')
    pymini.widgets['custom_log'] = widget.VarEntry(parent=insert_frame, name='custom_log', value='', default='')
    pymini.widgets['custom_log'].grid(column=1, row=0, sticky='news')
    pymini.widgets['custom_log'].configure(justify=Tk.LEFT)
    pymini.widgets['custom_log'].bind('<Return>', update)

    test_button = Tk.Button(insert_frame, text='test')
    test_button.bind('<ButtonPress-1>', update)
    test_button.grid(column=2, row=0, sticky='news')


    return frame

def update(e=None):
    print(pymini.widgets['custom_log'].get())
    pymini.widgets['application_log'].insert(Tk.END, '@user: ')
    pymini.widgets['application_log'].insert(Tk.END, '{}\n'.format(pymini.widgets['custom_log'].get()))


