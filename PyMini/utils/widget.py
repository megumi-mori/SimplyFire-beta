import tkinter as Tk
from tkinter import ttk, font
from PyMini.config import config
from PyMini.utils import validation
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import yaml
from PyMini import app
import textwrap




class VarWidget():
    def __init__(
            self,
            parent=None,
            name="",
            value=None,
            default=None,
            interface=None
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
        self.undo_value = self.get()
        self.interface = interface

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
            interface=None,
            width=None,
            **kwargs
    ):
        self.validate_type=validate_type
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default,
            interface=interface
        )
        if width is None:
            width = config.entry_width
        Tk.Entry.__init__(
            self,
            master=parent,
            textvariable=self.var,
            width=width,
            justify=Tk.RIGHT,
        )

        self.prev = self.get()
        self.validate_type = validate_type
        self.validate(event=None, validation_type=validate_type, undo=False)
        self.bind('<FocusOut>', lambda e, v=validate_type: self.validate(e, v), add='+')
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

    def validate(self, event, validation_type, undo=True):
        value = self.get()
        if validation.validate(validation_type, self.var.get()):
            self.undo_value = self.prev
            # if value != self.prev and undo:
            #     interface.add_undo([lambda v=self.prev:self.undo(v)])
            self.prev = value
            return True
        elif validation_type == 'int':
            try:
                new_value = str(int(float(value)))
                # self.set(new_value)
                # if new_value != self.prev and undo:
                #     interface.add_undo([lambda v=self.prev:self.undo(v)])
                self.prev = new_value
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
        return validation.convert(self.validate_type, self.var.get())
        # return self.var.get()
    def undo(self, value):
        self.set(value)
        self.focus_set()
        self.prev = value

class LabelVarEntry(Tk.Frame):
    def __init__(self,
                 parent,
                 name=None,
                 label="",
                 ** kwargs
                 ):
        Tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # make label (left side of frame)
        text = textwrap.wrap(label, width=config.default_label_length)
        text='\n'.join(text)
        self.label = ttk.Label(self, text=text)
        self.label.grid(column=0, row=0, sticky='news')

        self.widget = VarEntry(parent=self, name=name, **kwargs)
        self.widget.grid(row=0, column=1, sticky='ews')

def create_label_var_widget(widget, parent, label="", **kwargs):
    frame=Tk.Frame(parent)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # make label
    text = textwrap.wrap(label, width=config.default_label_length)
    text = '\n'.join(text)

    frame.label = ttk.Label(frame, text=text)
    frame.label.grid(column=0, row=0, sticky='news')

    frame.widget = widget(parent=frame, **kwargs)
    frame.widget.grid(row=0, column=1, sticky='ews')

    return frame




class VarOptionmenu(VarWidget, ttk.OptionMenu):
    def __init__(
            self,
            parent,
            name=None,
            value=None,
            default="",
            options=None,
            command=None,
            interface=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default,
            interface=interface
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
            command=self.command,
            **kwargs
        )

    def command_undo(self, e=None):
        if self.undo_value == self.get():
            print('nothing to do')
            return None
        try:
            self.set_undo()
            self.command(e)
        except Exception as ex:
            print(ex)
            pass
        #     interface.add_undo([
        #         lambda v=self.undo_value: self.var.set(v),
        #         self.command,
        #         self.set_undo,
        #     ])
        # except:
        #     interface.add_undo([
        #         lambda v=self.undo_value: self.var.set(v),
        #         self.set_undo
        #     ])
        # self.undo_value = self.get()

    def set_undo(self):
        self.undo_value = self.get()

    def clear_options(self):
        self['menu'].delete(0, 'end')

    def add_command(self, label="", command=None, **kwargs):
        self['menu'].add_command(label=label, command=command, **kwargs)

    def set(self, val):
        if val != self.get():
            self.undo_value = self.get()
            self.var.set(val)
        if self.command is not None:
            self.command()


class VarCheckbutton(VarWidget, ttk.Checkbutton):
    def __init__(
            self,
            parent,
            name=None,
            value=None,
            default=None,
            command=None,
            interface=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            name=name,
            parent=parent,
            value=value,
            default=default,
            interface=interface
        )
        ttk.Checkbutton.__init__(
            self,
            master=parent,
            variable=self.var,
            command=command,
            **kwargs
        )
    #     self.var.trace_add('write', self.toggle)
    #
    # def toggle(self, var=None, val=None, e=None):
    #     interface.add_undo([
    #         self.invoke,
    #         self.interface.undo_stack.pop
    #     ])

class VarText(VarWidget, Tk.Text):
    def __init__(
            self,
            parent,
            name="",
            value="",
            default="",
            lock=False,
            interface=None,
            **kwargs
    ):
        VarWidget.__init__(
            self,
            parent=parent,
            name=name,
            value=value,
            default=default,
            interface=interface
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
        disable = False
        if self['state'] == 'disabled':
            disable = True
            self.config(state='normal')
        self.delete(1.0, Tk.END)
        # self.insert(1.0, value)
        self.var.set(value)
        Tk.Text.insert(self, 1.0, value)
        if disable:
            self.config(state='disabled')

    def clear(self):
        disable = False
        if self['state'] == 'disabled':
            disable=True
            self.config(state='normal')
        self.delete(1.0, Tk.END)
        self.var.set("")
        if disable:
            self.config(state='disabled')

    def insert(self, text):
        disable = False
        if self['state'] == 'disabled':
            disable = True
            self.config(state='normal')
        Tk.Text.insert(self, Tk.END, text)
        self.var.set(self.var.get()+text)
        if disable:
            self.config(state='disabled')

    # def get(self):
    #     return Tk.Text.get(self, 1.0, Tk.END)

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
    def __init__(self, parent, bindings=None):
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

        if bindings is None:
            bindings = ('copy', 'select all', 'deselect', 'delete')
        if 'copy' in bindings:
            for key in config.key_copy:
                self.table.bind(key, self.copy, add="+")
        if 'select all' in bindings:
            for key in config.key_select_all:
                self.table.bind(key, self.select_all, add="+")
        if 'deselect' in bindings:
            for key in config.key_deselect:
                self.table.bind(key, self.unselect, add="+")
        if 'delete' in bindings:
            for key in config.key_delete:
                self.table.bind(key, self.delete_selected, add="+")

        self.menu = Tk.Menu(self.table, tearoff=0)

        self.table.bind("<Button-3>", self.popup, add="+")
    def remove_binding(self, type=''):
        if type == 'delete':
            for key in config.key_delete:
                self.table.bind(key)
            print('remove binding')
    def popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def add_menu_command(self, **kwargs):
        """
        adds a command to right-click menu
        use **kwargs for tkinter.Menu.add_command kwargs
        """
        self.menu.add_command(**kwargs)
    #     self.table.bind('<Button-3>', self.get_element)
    #
    # def get_element(self, e):
    #     print(self.table.identify_region(e.x, e.y))

    def copy(self, event=None):
        selected = self.table.selection()
        text = ""
        for c in self.displaycolumns:
            text = f'{text}{c}\t'
        text = text[:-1] + '\n'
        if len(selected) > 0:
            for i in selected:
                data = self.table.set(i)
                for c in self.displaycolumns:
                    text = text + '{}\t'.format(data[c])
                text = text[:-1] + '\n'
        try:
            app.root.clipboard_clear()
            app.root.clipboard_append(text)
        except:
            pass
    def copy_all(self, event=None):
        items = self.table.get_children()
        text = ""
        for c in self.columns:
            text = text + '{}\t'.format(c)
        text = text + '\n'
        for i in items:
            data = self.table.set(i)
            for c in self.columns:
                text = text + '{}\t'.format(data[c])
            text = text + '\n'
        try:
            app.root.clipboard_clear()
            app.root.clipboard_append(text)
        except:
            pass

    def select_all(self, event=None):
        self.table.selection_set(self.table.get_children())

    def define_columns(self, columns, sort=True, iid_header=None, stretch=False):
        # columns should be in tuple to avoid mutation
        self.table.config(displaycolumns=())
        self.table.config(columns=columns, show='headings')
        self.table.config(displaycolumns=columns)
        self.sort=sort
        self.iid_header = iid_header
        self.columns = columns
        self.displaycolumns=columns

        if sort:
            for i, col in enumerate(columns):
                self.table.heading(i, text=col, command=lambda _col = col: self._sort(_col, False))
                self.table.column(i, stretch=stretch)
        else:
            for i, col in enumerate(columns):
                self.table.heading(i, text=col)
                self.table.column(i, stretch=stretch)

    def add_columns(self, columns):
        all_columns = [i for i in self.columns]
        for c in columns:
            if c not in all_columns:
                all_columns.append(c)
        self.define_columns(all_columns, self.sort, self.iid_header)

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

    def add(self, datadict, parent='', index='end'): # data in the form of a dict
        new_columns = [key for key in datadict if key not in self.columns]
        if new_columns:
            self.add_columns(new_columns)
        self.table.insert(parent, index, iid=datadict.get(self.iid_header, None),
                          values=[datadict.get(i, None) for i in self.columns])

    def append(self, dataframe):
        if dataframe is None:
            print('nothing in dataframe')
            return None
        total = dataframe.shape[0]
        try:
            dataframe=dataframe[[k for k in self.columns]]
            for i, (idx, row) in enumerate(dataframe.iterrows()):
                try:
                    self.table.insert('', 'end', iid=row[self.iid_header],
                                      values=[row[k] for k in self.columns])
                    app.pb['value'] = i/total*100
                    app.pb.update()
                except Exception as e:
                    print(f'datatable append{e}')
                    pass
        except Exception as e:
            print(f'widget dataframe append error {e}')
            pass
    def set(self, dataframe):
        self.clear()
        self.append(dataframe)

    def fit_columns(self, event=None):
        if len(self.columns)>0:
            w = int(self.table.winfo_width()/len(self.columns))
            for i in self.displaycolumns:
                self.table.column(i, width=w)

    def show_columns(self, columns):
        self.displaycolumns=columns
        self.table.config(displaycolumns=columns)


    def clear(self):
        self.table.selection_remove(*self.table.selection())
        self.table.delete(*self.table.get_children())

    def hide(self):
        items = self.table.get_children()
        self.table.detach(*items)

    def unhide(self):
        items = self.table.get_children()


    ##### selection control #####
    def unselect(self, event=None):
        self.table.selection_remove(*self.table.selection())

    def select(self, iid):
        self.table.selection_set(str(iid))
        self.table.see(str(iid))

    def delete(self, iid):
        try:
            self.table.selection_remove(*[str(i) for i in iid])
        except:
            pass
        self.table.delete(*[str(i) for i in iid])

    def delete_selected(self, e=None):
        selection = self.table.selection()
        self.table.selection_remove(*selection)
        self.table.delete(*selection)
        return selection

    def export(self, filename, mode='w', suffix_num=0, handle_error=True):
        if suffix_num > 0:
            new_filename = f'{filename.split(".")[0]}({suffix_num}).{filename.split(".")[1]}'
        try:
            with open(new_filename, mode) as f:
                items = self.table.get_children()
                f.write(','.join(self.displaycolumns))
                f.write('\n')
                for i in items:
                    data = self.table.set(i)
                    f.write(','.join([data[c] for c in self.displaycolumns]))
                    f.write('\n')
        except (FileExistsError):
            if handle_error:
                self.export(filename, mode, suffix_num+1)



