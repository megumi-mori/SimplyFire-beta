import tkinter as Tk
from tkinter import ttk, font
from config import config
from utils import validation
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import yaml


class VarWidget():
    def __init__(
            self,
            parent=None,
            name="",
            value=None,
            default=None
    ):
        self.name = name
        self.var = Tk.StringVar()
        if value is not None:
            try:
                self.var.set(value)
            except:
                pass
            if default is not None:
                self.default=default
            else:
                self.default = config.default_vars['default_{}'.format(name)]
            return

        try:
            self.var.set(config.user_vars[name])
            self.default = config.default_vars['default_{}'.format(name)]
        except:
            try:
                self.var.set(config.system_vars[name])
                self.default = config.default_vars['system_default_{}'.format(name)]
            except:
                self.var.set('')
                self.default = ''

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def get_default(self):
        return self.default

    def set_to_default(self):
        self.set(self.default)

    def get_widget(self):
        return self

class VarEntry(VarWidget, Tk.Entry):
    def __init__(
            self,
            parent,
            name=None,
            value=None,
            default=None,
            validate_type=None,
            **kwargs
    ):
        self.prev = value
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default
        )
        Tk.Entry.__init__(
            self,
            master=parent,
            textvariable=self.var,
            width=config.entry_width,
            justify=Tk.RIGHT,
        )
        self.validate_type=validate_type
        self.prev = self.default
        self.validate_type = validate_type
        self.validate(event=None, validation_type=validate_type)
        self.bind('<FocusOut>', lambda e, v=validate_type: self.validate(e, v))
        self.bind('<Return>', lambda e, v=validate_type: self.validate(e, v), add="+")

    def revert(self):
        if validation.validate(self.validate_type, self.prev):
            self.set(self.prev)
        else:
            self.set_to_default()
            self.prev = self.default

    def set(self, value=""):
        # cannot use Tk.StringVar.set() due to validatecommand conflict
        self.delete(0, len(self.var.get()))
        self.insert(0, value)

    def validate(self, event, validation_type, c=None):
        value = self.get()
        if validation.validate(validation_type, self.var.get()):
            self.prev = value
            return True
        elif validation_type == 'int':
            try:
                new_value = str(int(float(value)))
                self.set(new_value)
                return True
            except:
                self.revert()
                return False
        else:
            self.revert()
            return False

    def get(self):
        # if validation.is_na(self.var.get()):
        #     return None
        return self.var.get()


class VarOptionmenu(VarWidget, ttk.OptionMenu):
    def __init__(
            self,
            parent,
            name=None,
            value=None,
            default="",
            options=None,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default
        )
        if options is None:
            options = []
        if value is None:
            value = default
        self.command = command
        ttk.OptionMenu.__init__(
            self,
            parent,
            self.var,
            value,
            *options,
            command=command,
            **kwargs
        )

    def replace_options(self, options=None):
        if options is None:
            options = []
        self['menu'].delete(0, 'end')
        for i in options:
            self['menu'].add_command(
                label=i,
                command=self.command
            )

    def clear_options(self):
        self['menu'].delete(0, 'end')

    def add_option(self, *args, **kwargs):
        self['menu'].add_command(*args, **kwargs)

class VarCheckbutton(VarWidget, ttk.Checkbutton):
    def __init__(
            self,
            parent,
            name=None,
            value=None,
            default=None,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            name=name,
            parent=parent,
            value=value,
            default=default

        )
        ttk.Checkbutton.__init__(
            self,
            master=parent,
            variable=self.var,
            command=command,
            **kwargs
        )

class VarText(VarWidget, Tk.Text):
    def __init__(
            self,
            parent,
            name="",
            value=None,
            default=None,
            lock=False,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default
        )
        Tk.Text.__init__(
            self,
            master=parent,
            **kwargs
        )
        # print(self.get())
        self.lock = lock
        if lock:
            Tk.Text.configure(self, state='disabled')
        self.set(value)


    def set(self, value):
        if self.lock:
            return None
        disable = False
        if self['state'] == 'disabled':
            disable = True
            self.config(state='normal')
        self.delete(1.0, Tk.END)
        self.insert(1.0, value)
        self.var.set(value)
        if disable:
            self.config(state='disabled')

    def clear(self):
        if self.lock:
            return None
        disable = False
        if self['state'] == 'disabled':
            disable=True
            self.config(state='normal')
        self.delete(1.0, Tk.END)
        self.var.set("")
        if disable:
            self.config(state='disabled')

    def insert(self, *args, **kwargs):
        disable = False
        if self['state'] == 'disabled':
            disable = True
            self.config(state='normal')
        Tk.Text.insert(self, *args, **kwargs)
        self.var.set(Tk.Text.get(self,1.0, Tk.END))
        if disable:
            self.config(state='disabled')


class VarScale(VarWidget, ttk.Scale):
    def __init__(
            self,
            parent,
            value="",
            default="",
            from_=100,
            to=100,
            orient=Tk.VERTICAL,
            command=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        ttk.Scale.__init__(
            self,
            master=parent,
            variable=self.var,
            from_=from_,
            to=to,
            orient=orient,
            command=command,
            **kwargs
        )

class VarLabel(VarWidget, ttk.Label):
    def __init__(
            self,
            parent,
            value="",
            default="",
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            value=value,
            default=default
        )
        ttk.Label.__init__(
            self,
            master=parent,
            text=value
        )

    def set(self, value):
        self.config(text = value)

class NavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent):
        self.toolitems = [t for t in self.toolitems if t[0] in ('Pan', 'Zoom', 'Save')]
        NavigationToolbar2Tk.__init__(self, canvas, parent)

        # self.add_toolitem(name='test', position=-1, image='img/arrow.png')

        # self.test_button = self._custom_button('test', command=self.test)

    def _custom_button(self, text, command, **kwargs):
        button = Tk.Button(master=self, text=text, padx=2, pady=2, command=command, **kwargs)
        button.pack(side = Tk.LEFT, fill='y')
        return button

    def test(self, e=None):
        if self.mode == 'test':
            self.mode = None
        else:
            self.mode = 'test'

        self._update_buttons_checked() ################ this is what you need to update the checked buttons in toolbar
        print(self.mode)
        # self.test_button.config(relief='sunken')

        self.canvas.widgetlock(self)



class PseudoFrame():
    """
    this class is used to store information similarly to ScrollableOptionFrame
    """
    def __init__(self):
        self.data = {}

    def get_value(self, key):
        return self.data[key]

    def set_value(self, key, value):
        self.data[key] = value

    def safe_dump_vars(self):
        return yaml.safe_dump(self.data)

class DataTable(Tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self)
        self.table.grid(column=0, row=0, sticky='news')

        vsb = ttk.Scrollbar(self, orient=Tk.VERTICAL, command=self.table.yview)
        vsb.grid(column=1, row=0, sticky='ns')
        self.table.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient=Tk.HORIZONTAL, command=self.table.xview)
        hsb.grid(column=0, row=1, sticky='ew')
        self.table.configure(xscrollcommand=hsb.set)

    #     self.table.bind('<Button-3>', self.get_element)
    #
    # def get_element(self, e):
    #     print(self.table.identify_region(e.x, e.y))


    def define_columns(self, columns):
        # columns should be in tuple to avoid mutation
        self.table.config(displaycolumns=())
        self.table.config(columns=columns, show='headings')
        self.table.config(displaycolumns=columns)
        self.iid_header = columns[0]
        self.columns = columns
        self.displaycolumns=columns
        for i, col in enumerate(columns):
            self.table.heading(i, text=col, command=lambda _col = col: self._sort(_col, False))
            self.table.column(i, stretch=Tk.NO)

    def add_columns(self, columns):
        all_columns = [i for i in self.columns]
        for c in columns:
            if c not in all_columns:
                all_columns.append(c)
        self.define_columns(all_columns)

    def set_iid(self, iid):
        self.iid_header = iid

    def _sort(self, col, reverse):
        try:
            l = [(float(self.table.set(k, col)), k) for k in self.table.get_children('')]
        except:
            l = [(self.table.set(k, col), k) for k in self.table.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.table.move(k, "", index)
        self.table.heading(col, command = lambda _col=col: self._sort(_col, not reverse))
        try:
            self.table.see(self.table.selection()[0])
        except:
            pass

    def add(self, datadict): # data in the form of a dict
        new_columns = [key for key in datadict if key not in self.columns]
        if new_columns:
            self.add_columns(new_columns)
        self.table.insert('', 'end', iid=datadict.get(self.iid_header, None),
                          values=[datadict.get(i, None) for i in self.columns])

    def append(self, dataframe):
        for i in dataframe.index:
            try:
                self.table.insert('', 'end', iid=i,
                                  values=[dataframe.loc[i][k] for k in self.columns])
            except:
                pass
    def set(self, dataframe):
        self.clear()
        self.append(dataframe)

    def fit_columns(self):
        w = int(self.table.winfo_width()/len(self.columns))
        for i in self.displaycolumns:
            self.table.column(i, width=w)

    def show_columns(self, columns):
        self.displaycolumns=columns
        self.table.config(displaycolumns=columns)


    def clear(self):
        self.table.selection_remove(*self.table.selection())
        self.table.delete(*self.table.get_children())
    ##### selection control #####

    def unselect(self):
        self.table.selection_remove(*self.table.selection())

    def select(self, iid):
        self.table.see(str(iid))
        self.table.selection_set(str(iid))

    def delete(self, iid):
        try:
            self.table.selection_remove(*[str(i) for i in iid])
        except:
            pass
        self.table.delete(*[str(i) for i in iid])




