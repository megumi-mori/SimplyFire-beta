from tkinter import Frame
class BaseModule():
    name = 'base_module'

    def __init__(self, root, interface):
        self.root = root
        self.interface = interface

    def log(self, msg, header=True):
        if header:
            self.root.log_display.log(f'@ {name}: {msg}')
        else:
            self.root.log_display.log(f'    {msg}')

    def undo(self, func):
        def inner(*args, **kwargs):
            self.log('Undo', True)
            func(*args, **kwargs)
        return inner




