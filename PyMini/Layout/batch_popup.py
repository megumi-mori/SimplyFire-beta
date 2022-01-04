import tkinter as Tk
import tkinter.filedialog
from tkinter import ttk, filedialog
from PyMini import app
from PyMini.Backend import interface
from PyMini.Layout import menubar, adjust_tab, detector_tab, evoked_tab
from PyMini.DataVisualizer import data_display, evoked_data_display, results_display
from PyMini.utils.widget import DataTable, VarText, VarLabel
import os
from PIL import Image, ImageTk
import yaml
from threading import Thread

def change_mode(mode):
    # 0 for mini 1 for evoked
    menubar.view_menu.invoke(mode)
    menubar.analysis_menu.invoke(mode)
    pass

def load():
    global stop
    stop = False
    try:
        global window
        window.deiconify()
        print('recalling window')
    except:
        global command_dict
        command_dict = {
            'Mini analysis mode (continuous)': lambda m=0: change_mode(m),
            'Evoked analysis mode (overlay)': lambda m=1: change_mode(m),

            'Find all': lambda p=False: detector_tab.find_all(p),
            'Find in window': lambda p=False: detector_tab.find_in_window(p),
            'Delete all': interface.delete_all_events,
            'Delete in window': detector_tab.delete_in_window,
            'Report stats (mini)': data_display.report,

            'Apply baseline adjustment': adjust_tab.adjust_baseline,
            'Apply trace averaging': adjust_tab.average_trace,
            'Apply filter': adjust_tab.filter,

            'Min/Max': evoked_tab.calculate_min_max,
            'Report stats (evoked)': evoked_data_display.report

        }
        create_window()
    global current_command
    current_command = None

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
    protocol_frame.grid_rowconfigure(1, weight=1)

    protocol_save_frame = ttk.Frame(protocol_frame)
    protocol_save_frame.grid(column=0, row=0, sticky='news')
    protocol_save_frame.grid_columnconfigure(0, weight=1)
    protocol_save_frame.grid_columnconfigure(1, weight=1)
    ttk.Button(protocol_save_frame, text='Import Protocol', command=ask_open_batch).grid(column=0, row=0, sticky='e')
    ttk.Button(protocol_save_frame, text='Export Protocol', command=ask_save_batch).grid(column=1, row=0, sticky='w')


    protocol_editor_frame = ttk.Frame(protocol_frame)
    protocol_editor_frame.grid(row=1, column=0, sticky='news')
    protocol_editor_frame.grid_columnconfigure(0, weight=1)
    protocol_editor_frame.grid_columnconfigure(2, weight=1)
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

    # Menubar
    # command_table.table.insert(parent='menubar', index='end', iid='open trace file', values=('\tOpen trace file',), tag='selectable')
    # command_table.table.insert(parent='menubar', index='end', iid='open event file', values=('\tOpen event file',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='save events file', values=('\tSave minis',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='mini mode', values=('\tMini analysis mode (continuous)',),
                                tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='evoked mode',
                                values=('\tEvoked analysis mode (overlay)',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='export events', values=('\tExport mini analysis data',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='export evoked', values=('\tExport evoked analysis data',), tag='selectable')
    command_table.table.insert(parent='menubar', index='end', iid='export results', values=('\tExport results table',), tag='selectable')

    # Mini analysis tab
    command_table.table.insert(parent='mini analysis tab', index='end', iid='delete in window',
                               values=('\tDelete in window',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='delete all',
                               values=('\tDelete all',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='find in window',
                          values=('\tFind in window',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='find all',
                          values=('\tFind all',), tag='selectable')
    command_table.table.insert(parent='mini analysis tab', index='end', iid='report mini',
                               values=('\tReport stats (mini)',), tag='selectable')


    # Evoked analysis tab
    command_table.table.insert(parent='evoked analysis tab', index='end', iid='min/max',
                          values=('\tMin/Max',), tag='selectable')
    command_table.table.insert(parent='evoked analysis tab', index='end', iid='report evoked',
                               values=('\tReport stats (evoked)',), tag='selectable')

    # Adjustment tab
    command_table.table.insert(parent='adjustment tab', index='end', iid='baseline adjustment',
                                values=('\tApply baseline adjustment',), tag='selectable')
    command_table.table.insert(parent='adjustment tab', index='end', iid='trace averaging',
                                values=('\tApply trace averaging',), tag='selectable')
    command_table.table.insert(parent='adjustment tab', index='end', iid='apply filter',
                                values=('\tApply filter',), tag='selectable')
    command_table.table.column("#0", stretch=False, width=40)
    command_table.table.column(0, stretch=True)

    # editor buttons
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

    # protocol list
    global protocol_table
    protocol_table = DataTable(protocol_editor_frame)
    protocol_table.table.configure(selectmode='none', show='tree headings')
    protocol_table.grid(column=2, row=0, sticky='news')
    protocol_table.define_columns(('Protocol',), sort=False)
    protocol_table.table.column(0, stretch=True)
    protocol_table.table.bind('<Button-1>', _on_click, add='+')

    protocol_navigation_frame = ttk.Frame(protocol_frame)
    protocol_navigation_frame.grid(column=0, row=2, sticky='news')
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
    file_frame.grid_rowconfigure(2, weight=1)

    # Import and export buttons
    file_save_frame = ttk.Frame(file_frame)
    file_save_frame.grid(column=1, row=0, sticky='news')
    file_save_frame.grid_columnconfigure(0, weight=1)
    file_save_frame.grid_columnconfigure(1, weight=1)
    ttk.Button(file_save_frame, text='Import list', command=ask_import_file).grid(column=0, row=0, sticky='ne')
    ttk.Button(file_save_frame, text='Export list', command=ask_export_file).grid(column=1, row=0, sticky='nw')

    # Path selection
    ttk.Label(master=file_frame,
              text='Base directory path:').grid(column=0, row=1, sticky='news')
    global path_entry
    path_entry = VarText(parent=file_frame,
        value="",
        default="")
    path_entry.grid(column=1, row=1, sticky='news')
    path_entry.configure(state='disabled', height=2)
    path_button_frame = ttk.Frame(file_frame)
    path_button_frame.grid(column=2, row=1, sticky='news')
    ttk.Button(master=path_button_frame, text='Browse', command=ask_path).grid(column=0, row=0, sticky='nw')
    ttk.Button(master=path_button_frame, text='Clear', command=path_entry.clear).grid(column=0, row=1, sticky='nw')

    # Filename selection
    ttk.Label(file_frame, text='File path list:').grid(column=0, row=2, sticky='nw')
    global file_entry
    file_entry = Tk.Text(master=file_frame)
    file_entry.grid(column=1, row=2, sticky='news')
    file_button_frame = ttk.Frame(file_frame)
    file_button_frame.grid(column=2, row=2, sticky='news')
    file_button_frame.grid_rowconfigure(0, weight=1)
    file_button_frame.grid_rowconfigure(2, weight=1)
    ttk.Button(file_button_frame, text='Add', command=ask_add_files).grid(column=0, row=0, sticky='s')
    ttk.Button(file_button_frame, text='Clear', command=lambda i=1.0, j=Tk.END: file_entry.delete(i,j)).grid(column=0, row=1)

    # Navigation buttons

    ttk.Button(file_frame, text='Next', command=lambda e=2:notebook.select(e)).grid(column=2, row=3, sticky='e')
    ttk.Button(file_frame, text='Previous', command=lambda e=0: notebook.select(e)).grid(column=0, row=3, sticky='w')

    ######################
    # Batch Processor #
    ###################

    batch_frame = ttk.Frame(window)
    notebook.add(batch_frame, text='Process')
    batch_frame.grid_columnconfigure(0, weight=1)
    batch_frame.grid_rowconfigure(1, weight=1)

    control_frame = ttk.Frame(batch_frame)
    control_frame.grid(column=0, row=2, sticky='news')
    control_frame.grid_columnconfigure(0, weight=1)
    control_frame.grid_columnconfigure(1, weight=1)
    global start_button
    start_button = ttk.Button(control_frame, text='START', command=process_start)
    start_button.grid(column=1, row=0, sticky='ne')
    ttk.Button(control_frame, text='Previous', command=lambda e=1: notebook.select(e)).grid(column=0, row=0, sticky='w')
    global stop_button
    stop_button = ttk.Button(control_frame, text='STOP', command=process_interrupt)
    stop_button.grid(column=2, row=0, sticky='ne')
    stop_button.grid_forget()
    # stop_button.config(state='disabled')

    global batch_log
    batch_log = VarText(parent=batch_frame, value="Press Start to begin...", default="Press Start to begin...", lock=False)
    batch_log.grid(column=0, row=1, sticky='news')

    global progress_message
    progress_message = VarLabel(batch_frame, value="Processing 0/0 files. At 0/0 steps", default="Processing 0/0 files. At 0/0 steps")
    progress_message.grid(column=0, row=2)

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
    if filenames is not None:
        filenames = "\n".join(filenames)
        filenames = filenames + '\n'
        file_entry.insert(Tk.END, filenames)
    window.lift()

def ask_import_file(event=None):
    fname = filedialog.askopenfilename(title='Open', filetypes=[('yaml files', '*.yaml'), ('All files', '*.*')])
    window.lift()
    if fname is None:
        return None
    with open(fname) as f:
        data = yaml.safe_load(f)
    global path_entry
    global file_entry
    path_entry.set(data['path_entry'])
    file_entry.delete(1.0, Tk.END)
    file_entry.insert(1.0, data['file_entry'])
    pass

def ask_export_file(event=None):
    fname = filedialog.asksaveasfilename(title='Save As...', filetypes=[('yaml files', '*.yaml'), ('All files','*.*')], defaultextension='.yaml')
    window.lift()

    if fname is None:
        return
    global path_entry
    global file_entry
    with open(fname, 'w') as f:
        f.write(yaml.safe_dump({
            'path_entry': path_entry.get(),
            'file_entry': file_entry.get(1.0, Tk.END)
        }))
    pass
def ask_open_batch(event=None):
    fname = filedialog.askopenfilename(title='Open', filetypes=[('protocol files', "*.prt"), ('All files', '*.*')])
    window.lift()
    if not fname:
        return
    with open(fname, 'r') as f:
        lines = f.readlines()
        for l in lines:
            protocol_table.table.insert('', 'end', values=(l.strip(),), tag='selectable')

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
    window.lift()
    if fname is None:
        return
    global protocol_fname
    protocol_fname = fname
    save_batch()

def process_interrupt(event=None):
    global stop
    stop = True
    global current_command
    interface.interrupt(process=current_command)


def process_start(event=None):
    global start_button
    start_button.grid_forget()
    global stop_button
    stop_button.grid(column=2, row=0, sticky='ne')
    global stop
    stop = False

    t = Thread(target=process_batch())
    t.start()

def process_batch(event=None):
    global window
    window.protocol("WM_DELETE_WINDOW", disable_event)
    app.root.attributes('-disabled', True)

    global protocol_table
    commands = [protocol_table.table.item(i, 'values')[0] for i in protocol_table.table.get_children()]
    total_steps = len(commands)
    global file_entry
    files = file_entry.get(1.0, Tk.END).split('\n')
    files = [f for f in files if f != ""]
    total_files = len(files)
    global path_entry
    basedir = path_entry.get()
    global stop
    global progress_message
    global batch_log
    global current_command
    batch_log.delete(1.0, Tk.END)

    for j, f in enumerate(files):
        if stop:
            break
        progress_message.config(text=f'Processing {j + 1}/{total_files} files. At {0}/{total_steps} steps')
        try:
            if f:
                interface.open_trace(f)
                batch_log.insert(f'Opening file: {f}\n')

                for i,c in enumerate(commands):
                    batch_log.insert(f'\t{c}\n')
                    progress_message.config(text=f'Processing {j+1}/{total_files} files. At {i+1}/{total_steps} steps')
                    current_command = c
                    if c == 'Save minis':
                        fname = f.split('.')[0]+'.event'
                        interface.save_events(fname, mode='x')
                        pass
                    elif c == 'Export mini analysis data':
                        fname =f.split('.')[0]+'_mini.csv'
                        data_display.dataframe.export(fname, mode='x')
                    elif c == 'Export evoked analysis data':
                        fname = f.split('.')[0] + '_evoked.csv'
                        evoked_data_display.dataframe.export(fname, mode='x')
                    elif c == 'Export results table':
                        fname = 'results.csv'
                        results_display.dataframe.export(fname, mode='x')

                    else:
                        command_dict[c]()
        except:
            batch_log.insert(f'could not open {f}')
    if stop:
        batch_log.insert('Batch stopped by user\n')
    batch_log.insert('End of batch\n')
    stop = False
    app.root.attributes('-disabled', False)
    window.protocol("WM_DELETE_WINDOW", window.withdraw)
    global stop_button
    stop_button.grid_forget()
    global start_button
    start_button.grid(column=1, row=0, sticky='ne')

    progress_message.config(text=f'Processing 0/0 files. At 0/0 steps')

    pass

def disable_event():
    pass
