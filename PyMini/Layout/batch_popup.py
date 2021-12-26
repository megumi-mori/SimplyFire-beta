import tkinter as Tk
import tkinter.filedialog
from tkinter import ttk, filedialog
import app
from utils.widget import DataTable, VarText
import os
from PIL import Image, ImageTk

def load():
    try:
        window.deiconify()
        print('recalling window')
    except:
        create_window()

def create_window():
    global window
    window = Tk.Toplevel(app.root)
    window.geometry('600x600')
    # app.root.attributes('-disabled', True)
    window.lift()
    window.focus_set()
    window.protocol('WM_DELETE_WINDOW', _on_close)

    ####################################
    # Populate batch processing window #
    ####################################

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(window)
    notebook.grid(column=0, row=0, sticky='news')

    ####################################
    # Protocol Window #
    ####################################

    protocol_frame = ttk.Frame(window)
    notebook.add(protocol_frame, text='Commands')
    protocol_frame.grid_columnconfigure(0, weight=1)
    protocol_frame.grid_rowconfigure(0, weight=1)

    protocol_editor_frame = ttk.Frame(protocol_frame)
    protocol_editor_frame.grid(row=0, column=0, sticky='news')
    protocol_editor_frame.grid_columnconfigure(0, weight=1)
    protocol_editor_frame.grid_rowconfigure(0, weight=1)

    global command_table
    command_table = DataTable(protocol_editor_frame, bindings=('deselect'))
    command_table.grid(column=0, row=0,sticky='news')

    ##########################
    # populate protocol list #
    ##########################

    command_table.define_columns(('Commands',), sort=False)
    command_table.table.configure(selectmode='none', show='tree headings')
    command_table.table.bind('<Button-1>', _on_click)

    command_table.set_iid('Commands')

    command_table.add({'Commands':'menubar'})
    command_table.table.item('menubar', open=True)
    command_table.add({'Commands': 'mini analysis tab'})
    command_table.table.item('mini analysis tab', open=True)
    command_table.add({'Commands': 'evoked analysis tab'})
    command_table.table.item('evoked analysis tab', open=True)
    command_table.add({'Commands': 'adjustment tab'})
    command_table.table.item('adjustment tab', open=True)



    ###########
    #Menubar
    ###########
    command_table.table.insert(parent='menubar', index='end', iid='open trace file', values=('\tOpen trace file',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='open event file', values=('\tOpen event file',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='save events file', values=('\tSave event file',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='mini mode', values=('\tAnalyze mini',),
                                tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='evoked mode',
                                values=('\tAnalyze evoked',), tag='selectable')

    ########
    # Mini analysis tab
    ########
    command_table.table.insert(parent='mini analysis tab', index='end', iid='find in window',
                          values=('\tFind in window',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='find all',
                          values=('\tFind all',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='delete in window',
                          values=('\tDelete in window',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='delete all',
                          values=('\tDelete all',), tag='selectable')

    #########
    #Evoked analysis tab
    #########
    command_table.table.insert(parent='evoked analysis tab', index='end', iid='min/max',
                          values=('\tMin/Max',), tag='selectable')


    ########
    # Adjustment tab
    ########
    command_table.table.insert(parent='adjustment tab', index='end', iid='baseline adjustment',
                                values=('\tApply baseline adjustment',), tag='selectable')
    command_table.table.insert(parent='adjustment tab', index='end', iid='trace averaging',
                                values=('\tApply trace averaging',), tag='selectable')
    command_table.table.insert(parent='adjustment tab', index='end', iid='apply filter',
                                values=('\tApply filter',), tag='selectable')
    command_table.table.column("#0", stretch=False, width=40)
    command_table.table.column(0, stretch=True)


    middle_button_frame = Tk.Frame(protocol_editor_frame)
    middle_button_frame.grid(column=1, row=0, sticky='news')
    middle_button_frame.grid_rowconfigure(0, weight=1)
    middle_button_frame.grid_rowconfigure(3, weight=1)
    middle_button_frame.grid_rowconfigure(6, weight=1)

    add_button = ttk.Button(middle_button_frame, command=_add_command)
    add_button.image = ImageTk.PhotoImage(app.arrow_img.rotate(270), master=app.root)
    add_button.config(image=add_button.image)
    add_button.grid(column=0, row=1, sticky='news')

    remove_button = ttk.Button(middle_button_frame, command=_delete_command)
    remove_button.image = ImageTk.PhotoImage(app.arrow_img.rotate(90), master=app.root)
    remove_button.config(image=remove_button.image)
    remove_button.grid(column=0, row=2, sticky='news')

    up_button = ttk.Button(middle_button_frame, command=_move_up_command)
    up_button.image = ImageTk.PhotoImage(app.arrow_img, master=app.root)
    up_button.config(image=up_button.image)
    up_button.grid(column=0, row=4, sticky='news')

    down_button = ttk.Button(middle_button_frame, command=_move_down_command)
    down_button.image = ImageTk.PhotoImage(app.arrow_img.rotate(180), master=app.root)
    down_button.config(image=down_button.image)
    down_button.grid(column=0, row=5, sticky='news')

    global protocol_table
    protocol_table = DataTable(protocol_editor_frame)
    protocol_table.table.configure(selectmode='none', show='tree headings')
    protocol_table.grid(column=2, row=0, sticky='news')
    protocol_table.define_columns(('Protocol',), sort=False)
    protocol_table.table.column(0, stretch=True)
    protocol_table.table.bind('<Button-1>', _on_click, add='+')

    protocol_navigation_frame = ttk.Frame(protocol_frame)
    protocol_navigation_frame.grid(column=0, row=1, sticky='news')
    protocol_navigation_frame.grid_rowconfigure(0, weight=1)
    protocol_navigation_frame.grid_columnconfigure(0, weight=1)

    next_button = ttk.Button(protocol_navigation_frame, text='Next', command=lambda e=1:notebook.select(e))
    next_button.grid(column=0, row=0, sticky='e')

    ########################
    # Populate File Window #
    ########################

    file_frame = ttk.Frame(window)
    notebook.add(file_frame, text='File List')
    file_frame.grid_columnconfigure(1, weight=1)
    file_frame.grid_rowconfigure(1, weight=1)
    list_frame = ttk.Frame(file_frame)
    list_frame.grid(row=1, column=0, sticky='news')
    list_frame.grid_rowconfigure(1, weight=1)
    list_frame.grid_columnconfigure(1, weight=1)




    ##################
    # Path selection #
    ##################
    ttk.Label(master=list_frame,
              text='Base directory path:').grid(column=0, row=0, sticky='news')
    global path_entry
    path_entry = VarText(parent=list_frame,
        value="",
        default="")
    path_entry.grid(column=1, row=0, sticky='news')
    path_entry.configure(state='disabled', height=2)
    path_button_frame = ttk.Frame(list_frame)
    path_button_frame.grid(column=2, row=0, sticky='news')
    ttk.Button(master=path_button_frame, text='Browse', command=ask_path).grid(column=0, row=0, sticky='nw')
    ttk.Button(master=path_button_frame, text='Clear', command=path_entry.clear).grid(column=0, row=1, sticky='nw')

    ######################
    # Filename selection #
    ######################
    ttk.Label(list_frame, text='File path list:').grid(column=0, row=1, sticky='nw')
    global file_entry
    file_entry = VarText(parent=list_frame,
                              value="",
                              default="")
    file_entry.grid(column=1, row=1, sticky='news')
    file_button_frame = ttk.Frame(list_frame)
    file_button_frame.grid(column=2, row=1, sticky='news')
    file_button_frame.grid_rowconfigure(0, weight=1)
    file_button_frame.grid_rowconfigure(2, weight=1)

    ttk.Button(file_button_frame, text='Add', command=ask_add_files).grid(column=0, row=0, sticky='s')
    ttk.Button(file_button_frame, text='Clear').grid(column=0, row=1)
    # next_button = ttk.Button(protocol_navigation_frame, text='Next', command=lambda e=1:notebook.select(e))
    # next_button.grid(column=0, row=0, sticky='e')

    import_export_frame = ttk.Frame(list_frame)
    import_export_frame.grid(column=1, row=2, sticky='news')
    ttk.Button(import_export_frame, text='Import list', command=ask_import_file).grid(column=0, row=0, sticky='n')
    ttk.Button(import_export_frame, text='Export list').grid(column=1, row=0, sticky='n')






    ##########
    # Menu bar
    ##########
    menubar = Tk.Menu(window)
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)
    window.config(menu=menubar)

    global protocol_fname
    protocol_fname = None

    file_menu.add_command(label="Open protocol \t Ctrl+o", command=ask_open_batch)
    file_menu.add_command(label="Save protocol as \t Ctrl+Shift+s", command=ask_save_batch)
    file_menu.add_command(label="Save protocol as \t Ctrl+s", command=save_batch)
    window.bind('<Control-o>', ask_open_batch)
    window.bind('<Control-s>', save_batch)
    window.bind('<Control-Shift-s>', ask_save_batch)

    window.update()


def _on_close(event=None):
    app.root.attributes('-disabled', False)
    window.withdraw()

def _on_click(event=None):
    tree = event.widget
    global protocol_table
    global command_table
    if tree == command_table.table:
        protocol_table.table.selection_remove(*protocol_table.table.selection())
    else:
        command_table.table.selection_remove(*command_table.table.selection())
    item_name = tree.identify_row(event.y)
    if item_name:
        tags = tree.item(item_name, 'tags')
        if tags and (tags[0] == 'selectable'):
            sel = tree.selection()
            if item_name in sel:
                tree.selection_remove(item_name)
            else:
                tree.selection_set(item_name)


def _add_command(event=None):
    global protocol_table
    global command_table

    sel = command_table.table.selection()
    try:
        protocol_table.table.insert('', 'end', values=(command_table.table.item(*sel, 'values')[0][1:],), tag='selectable')
        command_table.table.selection_remove(*command_table.table.selection())
    except:
        pass

def _delete_command(event=None):
    global protocol_table

    sel = protocol_table.table.selection()
    try:
        protocol_table.table.delete(*sel)
    except:
        pass
    pass
def _move_up_command(event=None):
    global protocol_table
    sel = protocol_table.table.selection()
    try:
        protocol_table.table.move(sel, '', protocol_table.table.index(sel)-1)
    except:
        pass

def _move_down_command(event=None):
    global command_table
    sel = protocol_table.table.selection()
    try:
        protocol_table.table.move(sel, '', protocol_table.table.index(sel)+1)
    except:
        pass
    pass

def ask_path(event=None):
    pathname=tkinter.filedialog.askdirectory(mustexist=True)
    window.lift()
    global path_entry
    path_entry.set(pathname)

    pass

def ask_add_files(event=None):
    if os.path.exists(path_entry.get()):
        filenames = tkinter.filedialog.askopenfilenames(
            initialdir=path_entry.get(),
            filetypes=[('abf files', '*.abf'), ('event files', '*.event'), ("All files", '*.*')])
    else:
        filenames=tkinter.filedialog.askopenfilenames(filetypes=[('abf files','*.abf'), ('event files', '*.event'), ("All files", '*.*')])
    global file_entry
    filenames = "\n".join(filenames)+'\n'
    file_entry.insert(Tk.END, filenames)
    window.lift()

def ask_import_file(event=None):
    pass

def ask_export_file(event=None):
    pass
def ask_open_batch(event=None):
    fname = filedialog.askopenfilename(title='Open', filetypes=[('protocol files', "*.prt"), ('All files', '*.*')])
    with open(fname, 'r') as f:
        lines = f.readlines()
        for l in lines:
            protocol_table.table.insert('', 'end', values=(l.strip(),), tag='selectable')
    window.lift()

def save_batch(event=None):
    global protocol_fname
    if protocol_fname is not None:
        global protocol_table
        commands = protocol_table.table.get_children()
        with open(protocol_fname, 'w') as f:
            for c in commands:
                f.write(protocol_table.table.item(c, 'values')[0])
                f.write('\n')
        window.lift()
    else:
        ask_save_batch()
def ask_save_batch(event=None):
    fname = filedialog.asksaveasfilename(title='Save As...', filetypes=[('protocol files', "*.prt"), ('All files', '*.*0')], defaultextension='.prt')
    if fname is not None:
        global protocol_fname
        protocol_fname = fname
        save_batch()
    else:
        return None