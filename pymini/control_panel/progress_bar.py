import tkinter as Tk
from config import config

class ProgressBar(Tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.bar=Tk.Frame(self, bg='white', height=15)
        self.bar.grid(column=0, row=0, sticky='nws')

    def initiate(self):
        self.bar.config(bg=config.default_progress_bar_color)

    def progress(self, percent):
        w = self.parent.winfo_width()
        self.bar.config(width=percent * w)
        self.update()

    def clear(self):
        self.bar.config(bg='grey')
        self.bar.config(width=0)

def progress(percent):
    w = frame.winfo_width()

    bar.config(width=percent * w)

def initiate():
    bar.config(bg='blue')
def clear():
    bar.config(bg='white')
    bar.config(width=0)

