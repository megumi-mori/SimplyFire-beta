from config import config
from utils.scrollable_option_frame import ScrollableOptionFrame
import pymini


def load(parent):

    def apply_all_style():
        pymini.plot_area.apply_all_style()
        pass

    def apply_style(style):
        pymini.plot_area.apply_style(style)
        pass

    def default_style_parameters():
        optionframe.default([
            'line_color',
            'line_width',
            'event_color',
            'highlight_color',
            'baseline_color',
            'decay_color',
            'trace_highlight_color'
        ])
    def _change_display_mode(e):
        print(e)


    optionframe = ScrollableOptionFrame(parent)
    ##################################################
    #           Populate style option tab            #
    ##################################################

    ##################################################
    #               Parameter options                #
    ##################################################

    optionframe.insert_title(
        name='plot_style',
        text='Graph Style'
    )
    optionframe.insert_label_entry(
        name='line_width',
        label='Trace line width:',
        value=config.line_width,
        default=config.default_line_width,
        validate_type='color'
    )
    optionframe.get_widget('line_width').bind(
        '<Return>',
        lambda e, k='line_width': apply_style(k)
    )
    optionframe.insert_label_entry(
        name='line_color',
        label='Trace line color:',
        value=config.line_color,
        default=config.default_line_color,
        validate_type='color'
    )
    optionframe.get_widget('line_color').bind(
        '<Return>',
        lambda e, k='line_color': apply_style(k)
    )
    optionframe.insert_label_entry(
        name='event_color',
        label='Event peak color:',
        value=config.event_color,
        default=config.default_event_color,
        validate_type='color'
    )
    optionframe.get_widget('event_color').bind(
        '<Return>',
        lambda e, k='event_color': apply_style
    )
    optionframe.insert_label_entry(
        name='baseline_color',
        label='Event baseline color:',
        value=config.baseline_color,
        default=config.default_baseline_color,
        validate_type='color'
    )
    optionframe.get_widget('baseline_color').bind(
        '<Return>',
        lambda e, k='baseline_color': apply_style
    )
    optionframe.insert_label_entry(
        name='decay_color',
        label='Event decay (tau) color:',
        value=config.decay_color,
        default=config.default_decay_color,
        validate_type='color'
    )
    optionframe.get_widget('decay_color').bind(
        '<Return>',
        lambda e, k='decay_color': apply_style
    )
    optionframe.insert_label_entry(
        name='highlight_color',
        label='Event highlight color:',
        value=config.highlight_color,
        default=config.default_highlight_color,
        validate_type='color'
    )
    optionframe.get_widget('highlight_color').bind(
        '<Return>',
        lambda e, k='highlight_color': apply_style
    )
    optionframe.insert_label_entry(
        name='trace_highlight_color',
        label='Trace highlight color:',
        value=config.trace_highlight_color,
        default=config.default_highlight_color,
        validate_type='color'
    )
    optionframe.get_widget('highlight_color').bind(
        '<Return>',
        lambda e, k='highlight_color': apply_style
    )
    optionframe.insert_button(
        text='Apply',
        command=apply_all_style
    )
    optionframe.insert_button(
        text='Default parameters',
        command=default_style_parameters
    )
    ##################################################
    #                 Marker display                 #
    ##################################################

    optionframe.insert_title(
        name='event_markers',
        text='Event Markers'
    )
    optionframe.insert_label_checkbox(
        name='show_peak',
        label='Peak',
        value=config.show_peak,
        default=config.default_show_peak,
        onvalue="1",
        offvalue=""
    )
    optionframe.insert_label_checkbox(
        name='show_decay_constant',
        label='Decay Constant',
        value=config.show_decay_constant,
        default=config.default_show_decay_constant,
        onvalue="1",
        offvalue=""
    )
    optionframe.insert_label_checkbox(
        name='show_start',
        label='Event Start',
        value=config.show_start,
        default=config.default_show_start,
        onvalue="1",
        offvalue=""
    )
    optionframe.insert_label_checkbox(
        name='show_end',
        label='Event End',
        value=config.show_end,
        default=config.default_show_end,
        onvalue="1",
        offvalue=""
    )

    # ##################################################
    # #                  Display Mode                  #
    # ##################################################
    # optionframe.insert_title(
    #     name='plot_mode',
    #     text="Display Mode"
    # )
    # optionframe.insert_label_optionmenu(
    #     name='plot_mode',
    #     label='Select display mode',
    #     value=config.plot_mode,
    #     default=config.default_plot_mode,
    #     options=['Continuous', 'Overlay'],
    #     command=_change_display_mode
    # )




    return optionframe