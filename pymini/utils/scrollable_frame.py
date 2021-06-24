# import tkinter as Tk
# from tkinter import ttk
# class ScrollableFrame():
#     # Scrollable Frame made using tutorial from: https://blog.teclado.com/tkinter-scrollable-frames/
#     def __init__(self, parent):
#         self.container = Tk.Frame(parent, bg='red')
#         self.canvas = Tk.Canvas(self.container, bg='orange')
#         self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
#         self.frame = Tk.Frame(self.canvas, bg='green')
#
#         self.frame.bind(
#             "<Configure>",
#             lambda e: self.canvas.configure(
#                 scrollregion=self.canvas.bbox('all')
#             )
#         )
#
#         self.canvas.create_window((0, 0), window=self.frame, anchor='nw', tag='option')
#
#         self.canvas.configure(yscrollcommand=self.scrollbar.set)
#
#
#         self.container.grid(column=0, row=0, sticky='news')
#         self.container.grid_columnconfigure(0, weight=1)
#         self.container.grid_rowconfigure(0, weight=1)
#
#         self.canvas.grid(column=0, row=0, sticky='news')
#         self.canvas.grid_columnconfigure(0, weight=1)
#         self.canvas.grid_rowconfigure(0, weight=1)
#
#         self.scrollbar.grid(column=2, row=0, sticky='ns')
#
#         self.canvas.bind('<Configure>', self.adjust_width)
#
#         # bind mousewheel
#         # Windows only for now:
#         self.frame.bind('<Enter>', self._bind_mousewheel)
#         self.frame.bind('<Leave>', self._unbind_mousewheel)
#
#     def adjust_width(self, e):
#         self.canvas.itemconfigure('option', width=e.width-4)
#         pass
#
#     def get_frame(self):
#         return self.container
#
#     def get_canvas(self):
#         return self.canvas
#
#     def _bind_mousewheel(self, event):
#         self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
#
#     def _unbind_mousewheel(self, event):
#         self.canvas.unbind_all('<MouseWheel')
#
#     def _on_mousewheel(self, event):
#         self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
#
#
