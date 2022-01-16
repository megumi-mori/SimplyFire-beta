from PyMini.utils.scrollable_option_frame import ScrollableOptionFrame
def load(parent):
    frame = ScrollableOptionFrame(parent)
    frame.grid_columnconfigure(0, weight=1)

    frame.frame.insert_title(
        name='continuous_title',
        text='Continuous Mode'
    )

    return frame
    pass
