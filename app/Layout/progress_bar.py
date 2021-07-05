import tkinter as Tk
from tkinter import ttk
from config import config

class ProgressBar(Tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # self.bar=Tk.Frame(self, bg='white', height=15)
        self.bar=ttk.Progressbar(self, orient=Tk.HORIZONTAL, mode='indeterminate')
        self.bar.grid(column=0, row=0, sticky='nws')

    def initiate(self):
        # self.bar.config(bg=config.default_progress_bar_color)
        pass

    def progress(self, percent):
        # w = self.parent.winfo_width()
        # self.bar.config(width=percent * w)
        # self.update()
        self.bar['value'] = percent
        pass

    def clear(self):
        self.bar['value'] = 0
        pass
        # # self.progress(0.01)
        # self.progress(0.01)
        # self.update()


def progress(percent):
    w = frame.winfo_width()

    bar.config(width=percent * w)

def initiate():
    bar.config(bg='blue')
def clear():
    bar.config(bg='white')
    bar.config(width=0)

