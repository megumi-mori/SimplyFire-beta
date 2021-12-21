import tkinter as Tk
from tkinter import ttk
import app
from utils.widget import DataTable, VarText
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
    app.root.attributes('-disabled', True)
    window.focus_set()
    window.protocol('WM_DELETE_WINDOW', _on_close)

    ####################################
    # Populate batch processing window #
    ####################################

    window.grid_columnconfigure(0, weight=1)
    window.grid_rowconfigure(0, weight=1)

    notebook = ttk.Notebook(window)
    notebook.grid(column=0, row=0, sticky='news')

    protocol_frame = Tk.Frame(window, bg='red')
    notebook.add(protocol_frame, text='Protocol')
    protocol_frame.grid_columnconfigure(0, weight=1)
    protocol_frame.grid_columnconfigure(2, weight=1)
    protocol_frame.grid_rowconfigure(0, weight=1)

    global command_table
    command_table = DataTable(protocol_frame, bindings=('deselect'))
    command_table.grid(column=0, row=0,sticky='news')

    ##########################
    # populate protocol list #
    ##########################

    command_table.define_columns(('protocol',), sort=False)
    command_table.table.configure(selectmode='none', show='tree headings')
    command_table.table.bind('<Button-1>', _on_click)

    command_table.set_iid('protocol')

    command_table.add({'protocol':'menubar'})
    command_table.table.item('menubar', open=True)
    command_table.add({'protocol': 'mini analysis tab'})
    command_table.table.item('mini analysis tab', open=True)
    command_table.add({'protocol': 'evoked analysis tab'})
    command_table.table.item('evoked analysis tab', open=True)
    command_table.add({'protocol': 'adjustment tab'})
    command_table.table.item('adjustment tab', open=True)



    ###########
    #Menubar
    ###########
    command_table.table.insert(parent='menubar', index='end', iid='mini mode', values=('\tSet to mini mode',),
                                tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='evoked mode',
                                values=('\tSet to evoked mode',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='continuous mode',
                                values=('\tSet to continuous mode',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='overlay mode',
                          values=('\tSet to overlay mode',), tag='selectable')

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
    command_table.table.column("#0", stretch=False, width=20)
    command_table.table.column(0, stretch=True)


    middle_button_frame = Tk.Frame(protocol_frame)
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
    protocol_table = DataTable(protocol_frame)
    protocol_table.table.configure(selectmode='none', show='tree headings')
    protocol_table.grid(column=2, row=0, sticky='news')
    protocol_table.define_columns(('batch protocol list',), sort=False)
    protocol_table.table.column(0, stretch=True)
    protocol_table.table.bind('<Button-1>', _on_click, add='+')

    ##########
    # Menu bar
    ##########
    menubar = Tk.Menu(window)
    file_menu = Tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)
    window.config(menu=menubar)
    file_menu.add_command(label="Open batch protocol \t Ctrl+o", command=ask_open_batch)
    file_menu.add_commad(label="Save batch protocol as \t Ctrl+s", command=ask_save_batch)
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
    protocol_table.table.insert('', 'end', values = command_table.table.item(*sel, 'values'), tag='selectable')

    command_table.table.selection_remove(*command_table.table.selection())

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

def ask_open_batch(event=None):
    pass

def ask_save_batch(event=None):
    pass