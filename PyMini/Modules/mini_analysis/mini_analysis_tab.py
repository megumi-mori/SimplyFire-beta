import matplotlib.backend_bases
from tkinter import messagebox
from PyMini.Modules.base_tab_module import BaseControlModule
from PyMini import app
from . import analysis
import pandas as pd
class ModuleControl(BaseControlModule):
    def __init__(self):
        super(ModuleControl, self).__init__(
            name= 'mini_analysis',
            menu_label='Mini Analysis',
            tab_label='Mini',
            parent=app.root,
            scrollbar=True,
            filename=__file__,
            has_table=True
        )

        self.changes = {}
        self.changed = False
        self.parameters = {}

        self.module_table = None
        self.mini_df = pd.DataFrame()

        self.markers = {'peak':None, 'decay':None, 'start':None}
        self.event_pick = False
        # plotting parameters:
        self.peak_color = 'green'
        self.decay_color = 'blue'
        self.start_color = 'red'
        self.highlight_color = 'red'

        self.peak_size = 5
        self.decay_size = 5
        self.start_size = 5
        self.highlight_size = 5

        self.insert_title(
            text="Mini Analysis"
        )
        self.find_all_button = self.insert_button(
            text='Find all',
            command=self.find_all
        )
        self.insert_button(
            text='Delete all',
            command=lambda undo=True:self.delete_all(undo)
        )
        self.insert_button(
            text='Find in\nwindow',
            command=self.find_range
        )
        self.insert_button(
            text='Delete in\nwindow',
            command=lambda undo=True:self.delete_in_window(undo)
        )
        self.insert_button(
            text='Report stats'
        )

        self.insert_title(
            text='Core parameters'
        )
        self.insert_label_optionmenu(
            name='detector_core_direction',
            label='Direction',
            options=['positive', 'negative']
        )

        self.core_params = {
            'manual_radius': {'id': 'detector_core_search_radius',
                              'label': 'Search radius in % of visible x-axis (Manual)', 'validation': 'float',
                              'conversion': float},
            'auto_radius': {'id': 'detector_core_auto_radius',
                            'label': 'Search window in ms (Auto)', 'validation': 'float', 'conversion': float},
            'delta_x_ms': {'id': 'detector_core_deltax_ms',
                           'label': 'Points before peak to estimate baseline (ms)',
                           'validation': 'float/zero',
                           'conversion': float},
            'lag_ms': {'id': 'detector_core_lag_ms',
                       'label': 'Window of data points averaged to find start of mini (ms):',
                       'validation': 'float', 'conversion': float}
        }
        for k, d in self.core_params.items():
            self.insert_label_entry(
                name=d['id'],
                label=d['label'],
                validate_type=d['validation']
            )
            self.widgets[d['id']].bind('<Return>', self._apply_parameters, add='+')
            self.widgets[d['id']].bind('<FocusOut>', self._apply_parameters, add='+')
            self.parameters[d['id']] = self.widgets[d['id']].get()
            self.changes[d['id']] = self.widgets[d['id']].get()
        self.insert_label_checkbox(
            name='detector_core_extrapolate_hw',
            label='Use decay to extrapolate halfwidth',
            onvalue='1',
            offvalue=""
        )
        self.insert_title(
            text='Decay fitting options'
        )
        self.insert_label_optionmenu(
            name='detector_core_decay_algorithm',
            label='Decay calculation method:',
            options=['Curve fit', '% amplitude'],
            command=self.populate_decay_algorithms
        )
        self.decay_params = {
            'decay_p_amp': {
                'id': 'detector_core_decay_p_amp',
                'label': 'Percent peak to mark as decay constant (%)',
                'validation': 'float',
                'conversion': float,
                'algorithm': ['% amplitude']
            },
            'decay_ss_min': {
                'id': 'detector_core_decay_ss_min',
                'label': 'Minimum decay constant (ms)',
                'validation': 'float',
                'conversion': float,
                'algorithm': ['Sum of squares']
            },
            'decay_ss_max': {
                'id': 'detector_core_decay_ss_max',
                'label': 'Max decay constant (ms)',
                'validation': 'float',
                'conversion': float,
                'algorithm': ['Sum of squares']
            },
            'decay_ss_interval': {
                'id': 'detector_core_decay_ss_interval',
                'label': 'Decay constant estimation step (ms)',
                'validation': 'float/auto',
                'conversion': float,
                'algorithm': ['Sum of squares']
            },
            'decay_best_guess': {
                'id': 'detector_core_decay_best_guess',
                'label': 'Starting seed for exponential decay fit (ms)',
                'validation': 'float',
                'conversion': float,
                'algorithm': ['Curve fit']
            },
            'decay_max_interval': {
                'id': 'detector_core_decay_max_interval',
                'label': 'Maximum x-interval considered for decay (ms)',
                'validation': 'float',
                'conversion': float,
                'algorithm': ['Curve fit', 'Sum of squares', '% amplitude']
            }
        }
        for k, d in self.decay_params.items():
            entry = self.insert_label_entry(
                name=d['id'],
                label=d['label'],
                validate_type=d['validation']
            )
            entry.master.master.grid_remove()
            entry.bind('<Return>', self._apply_parameters, add='+')
            entry.bind('<FocusOut>', self._apply_parameters, add='+')
            self.parameters[d['id']] = entry.get()
            self.changes[d['id']] = entry.get()
        self.populate_decay_algorithms(self.widgets['detector_core_decay_algorithm'].get())

        self.insert_title(
            text='Compound mini options'
        )
        self.insert_label_checkbox(
            name='detector_core_compound',
            label='Analyze compound minis',
            onvalue='1',
            offvalue='',
            command=self.populate_compound_params
        )
        self.compound_params = {
            # 'extrapolation_length': {'id': 'detector_core_extrapolation_length',
            #                   'label': 'Number of points after previous peak to extrapolate decay', 'validation': 'int',
            #                   'conversion': int},
            'p_valley': {'id': 'detector_core_p_valley',
                         'label': 'Minimum valley size in % of peak amplitude', 'validation': 'float',
                         'conversion': float},
            'max_compound_interval': {'id': 'detector_core_max_compound_interval',
                                      'label': 'Maximum interval between two peaks to use compound mini analysis (ms)',
                                      'validation': 'float', 'conversion': float},
            'min_peak2peak_ms': {'id': 'detector_core_min_peak2peak',
                                 'label': 'Ignore minis closer than (ms):', 'validation': 'float'},

        }
        for k, d in self.compound_params.items():
            entry = self.insert_label_entry(
                name=d['id'],
                label=d['label'],
                validate_type=d['validation']
            )
            entry.bind('<Return>', self._apply_parameters, add='+')
            entry.bind('<FocusOut>', self._apply_parameters, add='+')
            self.parameters[d['id']] = entry.get()
            self.changes[d['id']] = entry.get()
        self.populate_compound_params()

        self.insert_button(
            text='Apply',
            command=self._apply_parameters
        )

        self.insert_button(
            text='Default',
            command=self.default_core_params
        )

        ############## filtering parameters ###############

        self.insert_title(
            text='Filtering parameters'
        )
        self.filter_params = {
            'min_amp': {'id': 'detector_filter_min_amp',
                        'label': 'Minimum amplitude (absolute value) (y-axis unit):',
                        'validation': 'float/None', 'conversion': float},
            'max_amp': {'id': 'detector_filter_max_amp',
                        'label': 'Maximum amplitude (absolute value) (y-axis unit):',
                        'validation': 'float/None', 'conversion': float},
            'min_decay': {'id': 'detector_filter_min_decay',
                          'label': 'Minimum decay constant (tau) (ms)', 'validation': 'float/None',
                          'conversion': float},
            'max_decay': {'id': 'detector_filter_max_decay', 'label': 'Maximum decay constant (tau) (ms)',
                          'validation': 'float/None', 'conversion': float},
            'min_hw': {'id': 'detector_filter_min_hw', 'label': 'Minimum halfwidth (ms)', 'validation': 'float/None',
                       'conversion': float},
            'max_hw': {'id': 'detector_filter_max_hw', 'label': 'Maximum halfwidth (ms)', 'validation': 'float/None',
                       'conversion': float},
            'min_rise': {'id': 'detector_filter_min_rise', 'label': 'Minimum rise constant (ms)',
                         'validation': 'float/None', 'conversion': float},
            'max_rise': {'id': 'detector_filter_max_rise', 'label': 'Maximum rise constant (ms)',
                         'validation': 'float/None', 'conversion': float},
            'min_drr': {'id': 'detector_filter_min_dr', 'label': 'Minimum decay:rise ratio', 'validation': 'float/None',
                        'conversion': float},
            'max_drr': {'id': 'detector_filter_max_dr', 'label': 'Maximum decay:rise ratio', 'validation': 'float/None',
                        'conversion': float},
            'min_s2n': {'id': 'detector_filter_min_s2n', 'label': 'Minimum amp:std ratio', 'validation': 'float/None',
                        'conversion': float},
            'max_s2n': {'id': 'detector_filter_max_s2n', 'label': 'Maximum amp:std ratio', 'validation': 'float/None',
                        'conversion': float}
        }
        for k, d in self.filter_params.items():
            entry = self.insert_label_entry(
                name=d['id'],
                label=d['label'],
                validate_type=d['validation']
            )
            entry.bind('<Return>', self._apply_parameters, add='+')
            entry.bind('<FocusOut>', self._apply_parameters, add='+')
            self.parameters[d['id']] = entry.get()
            self.changes[d['id']] = entry.get()

        self.insert_button(
            text='Confirm',
            command=self._apply_parameters
        )

        self.insert_button(
            text='Default',
            command=lambda filter = 'detector_filter': self.set_to_default(filter)
        )
        self.insert_button(
            text='Apply filter\n(all)',
            command=self.apply_filter_all,
        )
        self.insert_button(
            text='Apply filter\n(window)',
            command=self.apply_filter_window
        )

        self.data_display_options = [
            ('data_display_time', 'Peak time'),
            ('data_display_amplitude', 'Amplitude'),
            ('data_display_decay', 'Decay constant'),
            # ('data_display_decay_func', 'Decay function'),
            ('data_display_rise', 'Rise duration'),
            ('data_display_halfwidth', 'Halfwidth'),
            ('data_display_baseline', 'Baseline'),
            # ('data_display_start', 'Start time'),
            # ('data_display_end', 'End time'),
            ('data_display_channel', 'Channel'),
            ('data_display_std', 'Stdev'),
            ('data_display_direction', 'Direction'),
            ('data_display_compound', 'Compound')
        ]

        for option in self.data_display_options:
            self.insert_label_checkbox(
                name=option[0],
                label=option[1],
                command=self._apply_column_options,
                onvalue='1',
                offvalue=""
            )
        self.mini_header2config = {
            't':'data_display_time',
            'amp': 'data_display_amplitude',
            'amp_unit': 'data_display_amplitude',
            'decay_const': 'data_display_decay',
            'decay_unit': 'data_display_decay',
            # ('decay_func', 'data_display_decay_func'),
            # ('decay_t', 'data_display_decay_time'),
            'rise_const': 'data_display_rise',
            'rise_unit': 'data_display_rise',
            'halfwidth': 'data_display_halfwidth',
            'halfwidth_unit':'data_display_halfwidth',
            'baseline':'data_display_baseline',
            'baseline_unit': 'data_display_baseline',
            'channel': 'data_display_channel',
            'stdev': 'data_display_std',
            'stdev_unit': 'data_display_std',
            'direction': 'data_display_direction',
            'compound': 'data_display_compound'
        }

        self.insert_button(
            text='Show All',
            command=self._columns_show_all
        )
        self.insert_button(
            text='Hide All',
            command=self._columns_hide_all
        )
        # event bindings:
        app.root.bind('<<LoadComplete>>', self._apply_column_options)
        app.root.bind('<<OpenRecording>>', lambda save=False:self.delete_clear(save))
        app.root.bind('<<DrawRect>>', self.select_from_rect)

        app.trace_display.canvas.mpl_connect('button_release_event', self.canvas_mouse_release)
        app.trace_display.canvas.mpl_connect('pick_event', self.select_from_event_pick)

    def _apply_column_options(self, e=None):
        app.get_data_table(self.name).show_columns(
            [k for k,v in self.mini_header2config.items() if self.widgets[v].get()]
        )
    def _apply_parameters(self, e=None):
        app.interface.focus()
        for i in self.parameters:
            if self.parameters[i] != self.widgets[i].get():
                self.changes[i] = self.widgets[i].get()
                self.changed = True

    def _columns_show_all(self, e=None):
        for option in self.data_display_options:
            self.widgets[option[0]].set('1')
        self._apply_column_options()
    def _columns_hide_all(self, e=None):
        for option in self.data_display_options:
            self.widgets[option[0]].set('')
        self._apply_column_options()

    def apply_filter_all(self, e=None):
        pass

    def apply_filter_window(self, e=None):
        pass

    def canvas_mouse_release(self, event: matplotlib.backend_bases.Event=None):
        if self.event_pick:
            self.event_pick = False
            return None
        if event.button != 1:
            return None
        if app.trace_display.canvas.toolbar.mode != "":
            return None
        if len(app.interface.recordings) == 0:
            return None
        if self.has_focus():
            if app.menubar.widgets['trace_mode'].get() != 'continuous':
                messagebox.showerror(title='Error', message='Please switch to continuous mode to analyze minis.')
                return None
            self.module_table.unselect()
            self.find_manual(event)
            pass

    def default_core_params(self, e=None):
        self.set_to_default('detector_core')
        self.populate_decay_algorithms()
        self.populate_compound_params()

    def delete_clear(self, undo=True):
        # deal with undo later
        # use this to clear the entire mini dataframe (all channels)
        self.mini_df = self.mini_df.iloc[0:0]
        self.module_table.clear()
        self.update_event_markers()

    def delete_all(self, undo=True):
        # deal with undo later
        # use this to clear the mini data for the current channel
        try:
            self.mini_df = self.mini_df[self.mini_df['channel']!=app.interface.channel]
        except:
            # no data yet
            pass
        self.module_table.clear()
        self.update_event_markers()
    def delete_in_window(self, undo=True):
        # deal with undo later
        xlim = app.trace_display.ax.get_xlim()
        selection = self.mini_df[(self.mini_df['t'] > xlim[0]) &
                            (self.mini_df['t'] < xlim[1]) &
                            (self.mini_df['channel'] == app.interface.channel)].t.values
        self.delete_selection(selection)


    def delete_selection(self, selection):
        # pass list of strings (corresponding to 't' column) to delete
        self.mini_df = self.mini_df[(~self.mini_df['t'].isin(selection))|(self.mini_df['channel']!=app.interface.channel)]
        self.module_table.delete(selection)
        self.update_event_markers()

    def extract_column(self, colname: str, t: list=None) -> list:
        # extract data for a specific column from the mini dataframe
        if len(app.interface.recordings) == 0:
            return None
        if len(self.mini_df.index) == 0:
            return None
        if t:
            try:
                return list(self.mini_df[self.mini_df['t'].isin(t)][colname])
            except:
                return list(self.mini_df[self.mini_df.t.isin(t)][colname])
        else:
            df = self.mini_df[self.mini_df['channel'] == app.interface.channel][colname]
            return list(df)

    def find_manual(self, event: matplotlib.backend_bases.Event=None):
        self.module_table.unselect()
        if event.xdata is None:
            return None
        mini = analysis.find_mini_manual(event.xdata, self.get_params(), self.mini_df)
        if mini['success']:
            self.mini_df = self.mini_df.append(mini,
                                     ignore_index=True,
                                     sort=False)
            self.mini_df = self.mini_df.sort_values(by='t')
            self.module_table.add({key:value for key,value in mini.items() if key in self.mini_header2config})
            self.update_event_markers()

    def find_all(self, event=None):
        self.module_table.unselect()
        df = analysis.find_mini_in_range(self.get_params(), self.mini_df)
        self.mini_df = pd.concat([self.mini_df, df])
        if df.shape[0] > 0:
            # if int(app.widgets['config_undo_stack'].get()) > 0:
            #     add_undo([
            #         lambda iid=df['t'].values, u=False: delete_event(iid, undo=u),
            #         lambda msg='Undo mini search': detector_tab.log(msg)
            #     ])
            self.update_event_markers()
            self.module_table.append(df)

        # if detector_tab.changed:
        #     log_display.search_update('Auto')
        #     log_display.param_update(detector_tab.changes)
        #     detector_tab.changes = {}
        #     detector_tab.changed = False
        app.pb['value'] = 0
        app.pb.update()
    def find_range(self, event=None):
        self.module_table.unselect()
        df = analysis.find_mini_in_range(self.get_params(), self.mini_df,
                                         xlim=app.trace_display.ax.get_xlim(),
                                         ylim=app.trace_display.ax.get_ylim())
        self.mini_df = pd.concat([self.mini_df, df])
        if df.shape[0] > 0:
            # if int(app.widgets['config_undo_stack'].get()) > 0:
            #     add_undo([
            #         lambda iid=df['t'].values, u=False: delete_event(iid, undo=u),
            #         lambda msg='Undo mini search': detector_tab.log(msg)
            #     ])
            self.update_event_markers()
            self.module_table.append(df)

    def get_params(self):
        params = {}
        params['direction'] = {'negative': -1, 'positive': 1}[
            self.widgets['detector_core_direction'].get()]  # convert direction to int value
        params['compound'] = self.widgets['detector_core_compound'].get() == '1'
        params['decay_algorithm'] = self.widgets['detector_core_decay_algorithm'].get()

        for k, d in self.core_params.items():
            try:
                params[k] = d['conversion'](self.widgets[d['id']].get())
            except:
                if self.widgets[d['id']].get() == 'None':
                    params[k] = None
                else:
                    params[k] = self.widgets[d['id']].get()
        for k, d in self.filter_params.items():
            try:
                params[k] = d['conversion'](self.widgets[d['id']].get())
            except:
                if self.widgets[d['id']].get() == 'None' or self.widgets[d['id']].get() == '':
                    params[k] = None
                else:
                    params[k] = self.widgets[d['id']].get()
        for k, d in self.decay_params.items():
            try:
                params[k] = d['conversion'](self.widgets[d['id']].get())
            except:
                if self.widgets[d['id']].get() == 'None':
                    params[k] = None
                else:
                    params[k] = self.widgets[d['id']].get()
        if params['compound']:
            for k, d in self.compound_params.items():
                params[k] = self.widgets[d['id']].get()
        return params



    def populate_decay_algorithms(self, e=None):
        algorithm = self.widgets['detector_core_decay_algorithm'].get()
        for k, d in self.decay_params.items():
            if algorithm in d['algorithm']:
                self.show_label_widget(self.widgets[d['id']])
            else:
                self.hide_label_widget(self.widgets[d['id']])
        self.record_change('decay algorithm', algorithm)



    def populate_compound_params(self, e=None):
        state = self.widgets['detector_core_compound'].get()
        if state:
            for k,d in self.compound_params.items():
                self.show_label_widget(self.widgets[d['id']])
        else:
            for k,d in self.compound_params.items():
                self.hide_label_widget(self.widgets[d['id']])

    def plot_peak(self, xs, ys):
        try:
            self.markers['peak'].remove()
        except:
            pass
        try:
            self.markers['peak'] = app.trace_display.ax.scatter(xs, ys, marker='o', color=self.peak_color,
                                                            s=self.peak_size**2, picker=True, animated=False)
        except:
            pass

    def plot_decay(self, xs, ys):
        try:
            self.markers['decay'].remove()
        except:
            pass
        try:
            self.markers['decay'], = app.trace_display.ax.plot(xs, ys, marker='x', color=self.decay_color,
                                                          markersize=self.decay_size, linestyle='None',
                                                          animated=False)
        except:
            pass

    def plot_highlight(self, xs, ys):
        try:
            self.markers['highlight'].remove()
        except:
            pass
        try:
            self.markers['highlight'], = app.trace_display.ax.plot(xs, ys, marker='o', c=self.highlight_color,
                                                                   markersize=self.highlight_size, linestyle='None',
                                                                   animated=False)
        except:
            pass
    def plot_start(self, xs, ys):
        try:
            self.markers['start'].remove()
        except:
            pass
        try:
            self.markers['start'], = app.trace_display.ax.plot(xs, ys, marker='x', color=self.start_color,
                                                          markersize=self.start_size, linestyle='None',
                                                          animated=False)
        except:
            pass
    def record_change(self, pname, pvalue):
        self.changed =  True
        self.changes[pname] = pvalue

    def select_from_event_pick(self, event=None):
        if not self.has_focus():
            return None
        self.event_pick = True # use this to avoid invoking other mouse-related events
        xdata, ydata = event.artist.get_offsets()[event.ind][0]
        if app.interpreter.multi_select:
            self.module_table.table.selection_toggle(str(round(xdata, app.interface.recordings[0].x_sigdig)))
        else:
            self.module_table.table.selection_set(str(round(xdata, app.interface.recordings[0].x_sigdig)))

    def select_from_table(self, selection):
        if not self.is_enabled():
            return None
        # pass a list of str for 't' column (index for table)
        selection = [float(i) for i in selection] # convert to float
        if selection:
            xs = self.extract_column('peak_coord_x', selection)
            ys = self.extract_column('peak_coord_y', selection)
            if len(selection) == 1:
                app.trace_display.center_plot_on(xs, ys)
            elif len(selection) > 1:
                app.trace_display.center_plot_area(min(xs), max(xs), min(ys), max(ys))
        else:
            xs = None
            ys = None
        self.plot_highlight(xs, ys) # get peak coordinates
        app.trace_display.draw_ani()

    def select_from_rect(self, event=None):
        if not self.has_focus():
            return None

        xlim = (app.interpreter.drag_coord_start[0], app.interpreter.drag_coord_end[0])
        xlim = (min(xlim), max(xlim))
        ylim = (app.interpreter.drag_coord_start[1], app.interpreter.drag_coord_end[1])
        ylim = (min(ylim), max(ylim))

        if self.mini_df.shape[0] == 0:
            return None
        df = self.mini_df[self.mini_df['channel'] == app.interface.channel]
        df = df[(df['t'] > xlim[0]) & (df['t'] < xlim[1])
                & (df['peak_coord_y'] > ylim[0]) & (df['peak_coord_y'] < ylim[1])]

        self.module_table.table.selection_set(list(df['t']))

    def update_event_markers(self):
        self.plot_peak(self.extract_column('peak_coord_x'), self.extract_column('peak_coord_y'))
        self.plot_decay(self.extract_column('decay_coord_x'), self.extract_column('decay_coord_y'))
        self.plot_start(self.extract_column('start_coord_x'), self.extract_column('start_coord_y'))
        app.trace_display.draw_ani()
        # app.trace_display.canvas.draw()