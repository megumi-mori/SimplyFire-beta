from threading import Thread
from tkinter import ttk
import tkinter as Tk
from simplyfire import app
popup_window = None
def do_nothing():
    pass
thread_function = do_nothing
interrupt_function = do_nothing
show_popup=True

def start_thread(target_func, interrupt_func=None, popup=True):
    if interrupt_func:
        assert (callable(interrupt_func)),  "interrupt_func must be callable"
    global thread_function
    thread_function = target_func
    global interrupt_function
    interrupt_function = interrupt_func
    global show_popup
    show_popup = popup
    t = Thread(target=_run_target_func)
    t.start()
    if popup and interrupt_func:
        return _show_interrupt_popup(interrupt_func)

def _run_target_func():
    # destroy the popup window at the end of the target process
    global thread_function
    global show_popup
    global interrupt_function
    thread_function()
    if show_popup:
        _destroy_interrupt_popup(interrupt_function)

def _show_interrupt_popup(interrupt_func):
    assert (callable(interrupt_func)), "interrupt_func must be callable"
    global popup_window
    popup_window = Tk.Toplevel(app.root)
    app.root.attributes('-disabled', True)

    def disable():
        pass

    popup_window.protocol('WM_DELETE_WINDOW', disable)
    label = ttk.Label(master=popup_window, text='Processing. Press STOP to interrupt')
    label.pack()
    button = ttk.Button(master=popup_window, text='STOP',
                        command=lambda t=interrupt_func: _destroy_interrupt_popup(t))
    button.pack()
    return popup_window


def _destroy_interrupt_popup(interrupt_func=None):
    if interrupt_func:
        interrupt_func()
    app.root.attributes('-disabled', False)
    if popup_window:
        popup_window.destroy()