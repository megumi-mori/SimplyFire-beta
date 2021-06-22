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
        name='event_color_peak',
        label='Event peak color:',
        value=config.event_color_peak,
        default=config.default_event_color_peak,
        validate_type='color'
    )
    optionframe.get_widget('event_color_peak').bind(
        '<Return>',
        lambda e, k='event_color_peak': apply_style
    )
    optionframe.insert_label_entry(
        name='event_color_start',
        label='Event start color:',
        value=config.event_color_start,
        default=config.default_event_color_start,
        validate_type='color'
    )
    optionframe.get_widget('event_color_start').bind(
        '<Return>',
        lambda e, k='event_color_start': apply_style
    )
    optionframe.insert_label_entry(
        name='event_color_end',
        label='Event baseline color:',
        value=config.event_color_end,
        default=config.default_event_color_end,
        validate_type='color'
    )
    optionframe.get_widget('event_color_end').bind(
        '<Return>',
        lambda e, k='event_color_end': apply_style
    )
    optionframe.insert_label_entry(
        name='event_color_decay',
        label='Event decay (tau) color:',
        value=config.event_color_decay,
        default=config.event_color_decay,
        validate_type='color'
    )
    optionframe.get_widget('event_color_decay').bind(
        '<Return>',
        lambda e, k='event_color_decayr': apply_style
    )
    optionframe.insert_label_entry(
        name='event_color_highlight',
        label='Event highlight color:',
        value=config.event_color_highlight,
        default=config.default_event_color_highlight,
        validate_type='color'
    )
    optionframe.get_widget('event_color_highlight').bind(
        '<Return>',
        lambda e, k='event_color_highlight': apply_style
    )
    optionframe.insert_label_entry(
        name='trace_highlight_color',
        label='Trace highlight color:',
        value=config.trace_highlight_color,
        default=config.default_trace_highlight_color,
        validate_type='color'
    )
    optionframe.get_widget('trace_highlight_color').bind(
        '<Return>',
        lambda e, k='trace_highlight_color': apply_style
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