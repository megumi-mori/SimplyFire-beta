from PyMini import app
from PyMini.Modules.base_control_module import BaseControlModule
from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
import tkinter as Tk
from tkinter import ttk
class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
            name='sweeps',
        menu_label='Sweep Selector',
        tab_label='Sweep',
        parent=app.root,
        scrollbar=False,
        filename=__file__,
        has_table=False)

        self.sweep_vars = [] # list of Tk.BooleanVars
        self.sweep_labels = [] # list of Tk.Labels
        self.sweep_buttons = [] # list of checkbuttons
        self.panels = [] # list of frames

        self._load_layout()
        self._load_binding()

        pass

    def _load_layout(self):
        self.insert_title(
            text='Sweep Selector'
        )

        self.insert_button(
            text='Hide All',
            # command=hide_all
        )
        self.insert_button(
            text='Show All',
            # command=show_all
        )
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=100)
        self.list_frame = ScrollableOptionFrame(self)  # , scrollbar=True)
        self.list_frame.grid(sticky='news')
        self.insert_panel(self.list_frame, separator=False)
    def populate_sweeps(self, event=None):
        frame = self.list_frame.get_frame() #get the internal frame in list_frame

        names = app.trace_display.sweeps.keys()
        for i, sweepname in enumerate(names):
            if i < len(self.sweep_vars):
                self.sweep_labels[i].config(text=sweepname)
                self.sweep_vars[i].set(True)
            else:
                f = Tk.Frame(frame)
                f.grid_columnconfigure(0, weight=1)
                f.grid_rowconfigure(0, weight=1)
                f.grid(column=0, row=i, sticky='news')
                label = Tk.Label(f, text=sweepname, justify=Tk.LEFT)
                label.grid(column=0, row=i, sticky='news')
                self.sweep_labels.append(label)
                var = Tk.BooleanVar(f, True)
                button = ttk.Checkbutton(master=f,
                                         variable=var,
                                         command=lambda x=i, v=var.get:
                                         self.toggle_sweep(x, v()))
                self.sweep_buttons.append(button)
                button.grid(column=1, row=i, sticky='es')
                self.sweep_vars.append(var)
                self.panels.append(f)
        j = len(self.sweep_vars)
        while len(self.sweep_vars) > len(names):
            temp = self.panels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_buttons.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_labels.pop()
            temp.forget()
            temp.destroy()
            del temp

            temp = self.sweep_vars.pop()
            temp.forget()
            temp.destroy()
            del temp
            j -= 1
        # if replace:
        #     while len(sweep_vars) > num:
        #         temp = panels.pop()
        #         temp.forget()
        #         temp.destroy()
        #         del temp
        #         # frames are getting removed from the parent frame - memory leak is not caused by this
        #         temp = checkbuttons.pop()
        #         temp.forget()
        #         temp.destroy()
        #         del temp
        #         temp = sweep_labels.pop()
        #         temp.forget()
        #         temp.destroy()
        #         del temp
        #         temp = sweep_vars.pop()
        #         del temp
        pass
    def _load_binding(self):
        app.root.bind('<<OpenedRecording>>', self.populate_sweeps)
        app.root.bind('<<ChangeTraceMode>>', self.populate_sweeps)
        pass
    def toggle_sweep(self, index=None, value=None):
        print(f"toggle sweep: {index} {value}")