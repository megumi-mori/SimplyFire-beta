from utils.scrollable_option_frame import OptionFrame, ScrollableOptionFrame
import app
from config import config
from tkinter import ttk, StringVar
import tkinter as Tk
from utils import widget
from Backend import interface
from DataVisualizer import trace_display, evoked_data_display
from Layout import sweep_tab
import pandas as pd

def load(parent):

    global widgets
    widgets = {}

    frame = ScrollableOptionFrame(parent)
    optionframe = frame.frame
    optionframe.insert_title(
        name='evoked',
        text='Evoked analysis mode',
        separator=True
    )
    widgets['evoked_target'] = optionframe.insert_label_optionmenu(
        name='evoked_target',
        label='Apply calculation to: ',
        options=['All sweeps', 'Visible sweeps', 'Highlighted sweeps'],
        separator=False
    ) #2
    widgets['evoked_channel'] = optionframe.insert_label_checkbox(
        name='evoked_channel',
        label='Calculate visible channel only',
        onvalue='1',
        offvalue="",
        separator=False
    )
    window_panel = optionframe.make_panel(separator=False)
    window_option_panel = OptionFrame(window_panel)
    window_option_panel.grid_columnconfigure(0, weight=1)
    window_option_panel.grid(column=0, row=0, sticky='news')
    widgets['evoked_window_mode'] = StringVar(window_option_panel, config.evoked_window_mode)

    window_option_panel.insert_widget(
        Tk.Label(master=window_option_panel, text='Calculate using data from (overlay only):')
    )

    all_button = ttk.Radiobutton(
        window_option_panel,
        text='Entire sweep',
        value='all',
        command=_select_evoked_window_mode,
        variable=widgets['evoked_window_mode']

    )
    window_option_panel.insert_widget(all_button)

    visible_button = ttk.Radiobutton(
        window_option_panel,
        text='Visible window',
        value='visible',
        command=_select_evoked_window_mode,
        variable=widgets['evoked_window_mode']

    )
    window_option_panel.insert_widget(visible_button)

    manual_button = ttk.Radiobutton(
        window_option_panel,
        text='Manually defined range:',
        value='manual',
        command=_select_evoked_window_mode,
        variable=widgets['evoked_window_mode']
    )
    window_option_panel.insert_widget(manual_button)

    panel = Tk.Frame(window_option_panel)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_columnconfigure(1, weight=1)

    widgets['evoked_range_left'] = widget.VarEntry(
        parent=panel,
        name='evoked_range_left',
        validate_type='float'
    )
    widgets['evoked_range_left'].grid(column=0, row=0, sticky='news')

    widgets['evoked_range_right'] = widget.VarEntry(
        parent=panel,
        name='evoked_range_right',
        validate_type='float'
    )
    widgets['evoked_range_right'].grid(column=1, row=0, sticky='news')

    window_option_panel.insert_widget(panel)



    min_max_title =optionframe.insert_title(
        name='min_max',
        text='Min/Max',
        separator=False
    ) #5
    optionframe.insert_button(
        text='Calculate Min/Max',
        command=calculate_min_max
    )

    # optionframe.insert_separator().master #7
    optionframe.insert_title(
        name='data',
        text='Data Display',
        separator=False
    )
    optionframe.insert_button(
        text='Reset\ndata',
        command=evoked_data_display.reset
    )
    optionframe.insert_button(
        text='Fit\ncolumns',
        command=evoked_data_display.dataframe.fit_columns
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

def calculate_min_max(e=None):
    target = widgets['evoked_target'].get()
    if app.widgets['trace_mode'].get() == 'continuous':
        target_sweeps = range(interface.al.recording.sweep_count)
    else:
        if target == 'All sweeps':
            target_sweeps = range(interface.al.recording.sweep_count)
        elif target == 'Visible sweeps':
            target_sweeps = [i for i, v in enumerate(sweep_tab.sweep_vars) if v.get()]  # check visible sweeps
        elif target == 'Highlighted sweeps':
            target_sweeps = [i for i in trace_display.highlighted_sweep]
    limit_channel = widgets['evoked_channel'].get()
    if limit_channel:
        channels = [interface.al.recording.channel]
    else:
        channels = range(interface.al.recording.channel_count)
    window = widgets['evoked_window_mode'].get()

    if window == 'all':
        xlim = None
    elif window == "visible":
        xlim = trace_display.ax.get_xlim()
    elif window == 'manual':
        xlim = (float(widgets['evoked_range_left'].get()), float(widgets['evoked_range_right'].get()))

    mins, mins_std = interface.al.calculate_min_sweeps(plot_mode=app.widgets['trace_mode'].get(), channels=channels, sweeps=target_sweeps, xlim=xlim)
    maxs, maxs_std = interface.al.calculate_max_sweeps(plot_mode=app.widgets['trace_mode'].get(), channels=channels, sweeps=target_sweeps,
                                                       xlim=xlim)
    if app.widgets['trace_mode'].get() == 'continuous':
        target_sweeps=[0]
    for i, c in enumerate(channels):
        for j, s in enumerate(target_sweeps):
            evoked_data_display.add({
                'channel': c,
                'sweep': s,
                'min': mins[i, j, 0],
                'min_unit': interface.al.recording.y_unit,
                'max': maxs[i, j, 0],
                'max_unit': interface.al.recording.y_unit
            })

    pass