from utils.scrollable_option_frame import OptionFrame, ScrollableOptionFrame
import app
from config import config
from tkinter import ttk, StringVar
import tkinter as Tk
from utils import widget

def load(parent):
    frame = ScrollableOptionFrame(parent)
    optionframe = frame.frame
    optionframe.insert_title(
        name='evoked',
        text='Evoked analysis mode',
        separator=True
    )
    app.widgets['evoked_target'] = optionframe.insert_label_optionmenu(
        name='evoked_target',
        label='Apply calculation to: ',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    )
    app.widgets['evoked_channel'] = optionframe.insert_label_checkbox(
        name='evoked_channel',
        label='Calculate visible channel only',
        onvalue='1',
        offvalue="",
        separator=False
    )
    window_option_panel = OptionFrame(optionframe)
    window_option_panel.grid_columnconfigure(0, weight=1)
    window_option_panel.config(bg='blue')
    optionframe.insert_panel(window_option_panel)
    app.widgets['evoked_window_mode'] = StringVar(window_option_panel, config.evoked_window_mode)

    window_option_panel.insert_widget(
        Tk.Label(master=window_option_panel, text='Calculate using data from:')
    )

    all_button = ttk.Radiobutton(
        window_option_panel,
        text='Entire sweep',
        value='all',
        command=_select_evoked_window_mode,
        variable=app.widgets['evoked_window_mode']

    )
    window_option_panel.insert_widget(all_button)

    visible_button = ttk.Radiobutton(
        window_option_panel,
        text='Visible window',
        value='visible',
        command=_select_evoked_window_mode,
        variable=app.widgets['evoked_window_mode']

    )
    window_option_panel.insert_widget(visible_button)

    manual_button = ttk.Radiobutton(
        window_option_panel,
        text='Manually defined range:',
        value='manual',
        command=_select_evoked_window_mode,
        variable=app.widgets['evoked_window_mode']
    )
    window_option_panel.insert_widget(manual_button)

    panel = Tk.Frame(window_option_panel)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_columnconfigure(1, weight=1)

    app.widgets['evoked_range_left'] = widget.VarEntry(
        parent=panel,
        name='evoked_range_left',
        validate_type='float'
    )
    app.widgets['evoked_range_left'].grid(column=0, row=0, sticky='news')

    app.widgets['evoked_range_right'] = widget.VarEntry(
        parent=panel,
        name='evoked_range_right',
        validate_type='float'
    )
    app.widgets['evoked_range_right'].grid(column=1, row=0, sticky='news')

    window_option_panel.insert_widget(panel)


    optionframe.insert_title(
        name='min_max',
        text='Min/Max',
        separator=False
    )

    return frame

def _select_evoked_window_mode(e=None):
    if app.widgets['evoked_window_mode'].get() == 'all':
        app.widgets['evoked_range_left'].config(state='disabled')
        app.widgets['evoked_range_right'].config(state='disabled')
        return
    if app.widgets['evoked_window_mode'].get() == 'visible':
        app.widgets['evoked_range_left'].config(state='disabled')
        app.widgets['evoked_range_right'].config(state='disabled')
        return
    if app.widgets['evoked_window_mode'].get() == 'manual':
        app.widgets['evoked_range_left'].config(state='normal')
        app.widgets['evoked_range_right'].config(state='normal')
    pass