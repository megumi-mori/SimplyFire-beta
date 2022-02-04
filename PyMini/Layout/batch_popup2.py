from tkinter import ttk
import tkinter as Tk
from PyMini import app
class BatchPopup(Tk.Toplevel):
    def __init__(self):
        super().__init__(app.root)
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self._load_layout()

    def ask_open_batch(self):
        pass

    def ask_save_batch(self):
        pass

    def show(self):
        self.deiconify()

    def interrupt(self):
        pass

    def resume(self):
        pass

    def _load_layout(self):
        ############
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(column=0, row=0, sticky='news')

        ########### protocol page
        self.protocol_frame = ttk.Frame(self)
        self.notebook.add(self.protocol_frame, text='Commands')
        self.protocol_frame.grid_columnconfigure(0, weight=1)
        self.protocol_frame.grid_rowconfigure(0, weight=1)

        frame = ttk.Frame(self.protocol_frame)
        frame.grid(column=0, row=0, sticky='news')
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        ttk.Button(frame, text='Import Protocol', command=self.ask_open_batch).grid(column=0, row=0, sticky='e')
        ttk.Button(frame, text='Export Protocol', command=self.ask_save_batch).grid(column=1, row=0, sticky='w')


    def _on_close(self):
        self.interrupt()
        if self.paused:
            self.resume()
        app.root.attributes('-disabled', False)
        self.withdraw()
