import tkinter as Tk
from utils.scrollable_option_frame import ScrollableOptionFrame
from config import config
def load(parent):
    frame = ScrollableOptionFrame(parent, scrollbar=False)
    frame.grid_columnconfigure(0, weight=1)

    frame.insert_title(
        name='sweep_title',
        text='Overlay Configurations'
    )
    frame.insert_label_checkbox(
        name='export_sweep',
        label='Export sweep numbers when exporting image?',
        value=config.export_sweep,
        default=config.default_export_sweep
    )

    frame.insert_title(
        name='sweep_select',
        text='Select Sweeps'
    )
    frame.grid_rowconfigure(3, weight=1)
    list_frame = ScrollableOptionFrame(frame, scrollbar=True)
    list_frame.grid(sticky='news')
    frame.insert_panel(list_frame, separator=False)
    list_frame.insert_button(
        text='Hide All',
        command=None
    )
    list_frame.insert_button(
        text='Show All',
        command=None
    )

    return frame
