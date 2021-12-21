import tkinter as Tk
from tkinter import ttk
import app
from utils.widget import DataTable, VarText

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

    protocol_table = DataTable(protocol_frame)
    protocol_table.grid(column=0, row=0,sticky='news')

    ##########################
    # populate protocol list #
    ##########################

    protocol_table.define_columns(('protocol',), sort=False)
    protocol_table.table.configure(selectmode='none', show='tree headings')

    protocol_table.set_iid('protocol')

    protocol_table.add({'protocol':'menubar'})
    protocol_table.add({'protocol': 'mini analysis tab'})
    protocol_table.add({'protocol': 'evoked analysis tab'})
    protocol_table.add({'protocol': 'adjustment tab'})



    ###########
    #Menubar
    ###########
    protocol_table.insert(parent='menubar', index='end', iid='set to mini mode', values=('\tset to mini mode',))
    protocol_table.insert(parent='menubar', index='end', iid='set to evoked mode', values=('\tset to evoked mode',))
    protocol_table.add({'protocol': 'mini analysis mode'}, parent='menubar')
    protocol_table.add({'protocol': 'evoked analysis mode'}, parent='menubar')
    protocol_table.add({'protocol': 'continuous view mode'}, parent='menubar')
    protocol_table.add({'protocol': 'overlay view mode'}, parent='menubar')

    ########
    # Mini analysis tab
    ########
    protocol_table.add({'protocol': 'Find in window'}, parent='mini analysis tab')
    protocol_table.add({'protocol': 'Find all'}, parent='mini analysis tab')
    protocol_table.add({'protocol': 'Delete in window'}, parent='mini analysis tab')
    protocol_table.add({'protocol': 'Delete all'}, parent='mini analysis tab')

    #########
    #Evoked analysis tab
    #########
    protocol_table.add({'protocol': 'Min/Max'},  parent='evoked analysis tab')


    protocol_table.table.column("#0", stretch=False, width=20)
    protocol_table.table.column(0, stretch=True)


    middle_button_frame = Tk.Frame(protocol_frame)
    middle_button_frame.grid(column=1, row=0, sticky='news')

    protocol_list = VarText(protocol_frame, value="", width=20)
    protocol_list.grid(column=2, row=0, sticky='news')



    window.update()
    # protocol_table.fit_columns()

   # protocol_table = DataTable(protocol_frame)
    # protocol_table.grid(column=0, row=0, sticky='news')
    #
    # protocol_table.define_columns(['Protocol'], sort=False, iid_header=None, stretch=Tk.NO)
    #
    # file_frame = Tk.Frame(window)
    # file_frame.grid(row=0, column=2, sticky='news')
    # file_frame.grid_columnconfigure(0, weight=1)
    # file_frame.grid_rowconfigure(0, weight=1)
    # file_table = DataTable(file_frame)
    # file_table.grid(column=0, row=0, sticky='news')
    #
    # file_table.define_columns(['Directory', 'Filename'], sort=False, iid_header=None, stretch=Tk.NO)
    # window.update()
    # protocol_table.fit_columns()
    # file_table.fit_columns()


def _on_close(event=None):
    app.root.attributes('-disabled', False)
    window.withdraw()


