from simplyfire.utils.plugin_controller import PluginController
from simplyfire.utils.plugin_form import PluginForm
from simplyfire.utils.plugin_table import PluginTable
from simplyfire import app
from simplyfire.backend import plugin_manager, analyzer2
from simplyfire.utils import formatting, custom_widgets
import pandas as pd
from . import mini_analysis
import os
from tkinter import messagebox, filedialog
import numpy as np

#### set module variables #####
tab_label = 'Mini'
menu_label = 'Mini Analysis'
name = 'mini_analysis'

mini_df = pd.DataFrame(columns=['compound'])
mini_df = mini_df.astype({'compound': bool})  # set column types as necessary

saved = True  # track if mini has been saved
mini_filename = ""

markers = {'peak': None, 'decay': None, 'start': None}  # matplotlib markers
event_pick = False

parameters = {}
changes = {}
changed = False
logged = True

#### Default values ####
peak_color = 'green'
decay_color = 'blue'
start_color = 'red'
highlight_color = 'red'

peak_size = 5
decay_size = 5
start_size = 5
highlight_size = 5

# core params
detector_core_direction = 'positive'
detector_core_search_radius = 5.0
detector_core_auto_radius = 80
detector_core_lag_ms = 10
detector_core_deltax_ms = 0
detector_core_min_peak2peak = 5
detector_core_std_lag_ms = 10
detector_core_extrapolate_hw = '1'

# decay
detector_core_decay_algorithm = 'Curve fit (sing. exp.)'
detector_core_decay_p_amp = 37
detector_core_decay_ss_min = 0
detector_core_decay_ss_max = 10
detector_core_decay_ss_interval = 0.01
detector_core_decay_best_guess = 4
detector_core_decay_max_interval = 25

# compound
detector_core_compound = 1
detector_core_extrapolation_length = 100
detector_core_p_valley = 50.0
detector_core_max_compound_interval = 50

# filtering
detector_filter_min_amp = 0.3
detector_filter_max_amp = 'None'
detector_filter_min_decay = 0
detector_filter_max_decay = 'None'
detector_min_auc = 0
detector_filter_min_hw = 0
detector_filter_max_hw = 'None'
detector_filter_min_rise = 0
detector_filter_max_rise = 'None'
detector_filter_min_dr = 0
detector_filter_max_dr = 'None'
detector_filter_min_s2n = 0
detector_filter_max_s2n = 'None'

# misc
# store the column name and the name of the widget controlling its visibility
mini_header2config = {
    't': 'data_display_time',
    'amp': 'data_display_amplitude',
    'amp_unit': 'data_display_amplitude',
    'decay_const': 'data_display_decay',
    'decay_unit': 'data_display_decay',
    # ('decay_func', 'data_display_decay_func'),
    # ('decay_t', 'data_display_decay_time'),
    'rise_const': 'data_display_rise',
    'rise_unit': 'data_display_rise',
    'halfwidth': 'data_display_halfwidth',
    'halfwidth_unit': 'data_display_halfwidth',
    'baseline': 'data_display_baseline',
    'baseline_unit': 'data_display_baseline',
    'channel': 'data_display_channel',
    'stdev': 'data_display_std',
    'stdev_unit': 'data_display_std',
    'direction': 'data_display_direction',
    'compound': 'data_display_compound'
}
# store the names of widgets controlling the datapanel column visibility
data_display_options = ['data_display_time', 'data_display_amplitude', 'data_display_decay','data_display_rise',
                        'data_display_halfwidth', 'data_display_baseline', 'data_display_channel', 'data_display_std',
                        'data_display_direction', 'data_display_compound']
# store parameter translation
core_params = {
    'manual_radius': {'name': 'detector_core_search_radius', 'conversion': float},
    'auto_radius': {'name': 'detector_core_auto_radius', 'conversion': float},
    'delta_x_ms': {'name': 'detector_core_deltax_ms', 'conversion': float},
    'lag_ms': {'name': 'detector_core_lag_ms', 'conversion': float}
}
filter_params = {
            'min_amp': {'name': 'detector_filter_min_amp', 'conversion': float},
            'max_amp': {'name': 'detector_filter_max_amp', 'conversion': float},
            'min_decay': {'name': 'detector_filter_min_decay', 'conversion': float},
            'max_decay': {'name': 'detector_filter_max_decay', 'conversion': float},
            'min_hw': {'name': 'detector_filter_min_hw', 'conversion': float},
            'max_hw': {'name': 'detector_filter_max_hw', 'conversion': float},
            'min_rise': {'name': 'detector_filter_min_rise', 'conversion': float},
            'max_rise': {'name': 'detector_filter_max_rise', 'conversion': float},
            'min_drr': {'name': 'detector_filter_min_dr', 'conversion': float},
            'max_drr': {'name': 'detector_filter_max_dr', 'conversion': float},
            'min_s2n': {'name': 'detector_filter_min_s2n', 'conversion': float},
            'max_s2n': {'name': 'detector_filter_max_s2n', 'conversion': float}
        }
decay_params = {
            'decay_p_amp': {
                'name': 'detector_core_decay_p_amp',
                'conversion': float,
                'algorithm': ['% amplitude']
            },
            'decay_best_guess': {
                'name': 'detector_core_decay_best_guess',
                'conversion': float,
                'algorithm': ['Curve fit (sing. exp.)']
            },
            'decay_max_interval': {
                'name': 'detector_core_decay_max_interval',
                'conversion': float,
                'algorithm': ['Curve fit (sing. exp.)', '% amplitude']
            }
        }
compound_params = {
    'p_valley': {'name': 'detector_core_p_valley', 'conversion': float},
    'max_compound_interval': {'name': 'detector_core_max_compound_interval', 'conversion': float},
    'min_peak2peak_ms': {'name': 'detector_core_min_peak2peak', 'conversion': float},

}
#### modify the PluginController class ####
class MiniController(PluginController):
    def update_plugin_display(self, event=None):
        super().update_plugin_display()
        try:
            if self.is_visible():
                update_event_markers(draw=True)
            else:
                for m in markers:
                    try:
                        markers[m].remove()
                    except:
                        pass
                app.trace_display.draw_ani()
        except:
            pass

    app.pb['value'] = 0
    app.pb.update()

#### modify the PluginTable class ####
class MiniTable(PluginTable):
    def clear(self, event=None):
        delete_all(True)

    def delete_selected(self, event=None, undo=True):
        delete_selection([float(s) for s in self.table.selection()], undo=undo)

    def report(self, event=None):
        report_results()

    def report_selected(self, event=None):
        report_selected_results()


#### define functions ####
# private functions
def _apply_column_options(event=None):
    """
    called when column checkbox is toggled
    changes the visibility of columns in the datapanel
    """
    datapanel.show_columns(
        [k for k,v in mini_header2config.items() if form.inputs[v].get()]
    )

def _apply_parameters(event=None):
    """
    Called when 'Apply' button is pressed or the user inputs a value in the form.
    Compares the current user input with stored values. If there are any changes, stores the changes
    Used to log the changes made to the parameters by the user.
    """
    global changed
    app.interface.focus()
    for i in parameters.keys():
        if parameters[i] != form.inputs[i].get():
            changes[i] = form.inputs[i].get()
            changed = True
            parameters[i] = form.inputs[i].get()

def _columns_show_all(event=None):
    """
    Called by the 'Show All' button. Sets all the datapanel columns to 'Show'
    """
    for option in data_display_options:
        form.inputs[option].set('1')
    _apply_column_options()

def _columns_hide_all(event=None):
    """
    called by the 'Hide All' button. Sets all the datapanel columsn to 'Hidden'
    """
    for option in data_display_options:
        form.inputs[option].set('1')
    _apply_column_options()

def _default_core_params(event=None):
    """
    Called by the 'Default' button for core parameters.
    Fill the form with default values, and show/hide some widgets accordingly
    """
    form.set_to_default('detector_core')
    _populate_decay_algorithms()
    _populate_compound_params()

# populate widgets
def _populate_decay_algorithms(event=None):
    algorithm = form.inputs['detector_core_decay_algorithm'].get()
    for k, d in decay_params.items():
        if algorithm in d['algorithm']:
            form.show_widget(form.inputs[d['name']])
        else:
            form.hide_widget(form.inputs[d['name']])
    record_param_change('decay algorithm', algorithm)

def _populate_compound_params(event=None):
    state = form.inputs['detector_core_compound'].get()
    if state:
        for k, d in compound_params.items():
            form.show_widget(form.inputs[d['name']])
    else:
        for k, d in compound_params.items():
            form.hide_widget(form.inputs[d['name']])

# canvas response
def canvas_mouse_release(event=None):
    """
    bound to canvas mouse release event within trace_display
    """
    global event_pick
    if event_pick:
        event_pick = False
        # a marker had been selected. Do not analyze the area
        return
    if app.trace_display.canvas.toolbar.mode != "":
        # the matplotlib canvas is on pan/zoom or rect zoom mode
        # do nothing
        return
    if len(app.interface.recordings) == 0:
        # no recording file has been opened yet
        return
    if form.has_focus(): # limit function to when the plugin is in focus
        if app.inputs['trace_mode'].get() != 'continuous': # should be disabled - contingency
            messagebox.showerror('Error', 'Please switch to continuous mode to analyze minis')
            return
        datapanel.unselect()
        try:
            find_mini_manual(app.interpreter.mouse_event.xdata) # get the stored mouse event from interpreter
        except:
            pass




# batch specific functions
def batch_find_all():
    _find_mini_all_thread(popup=False, undo=False)
    app.batch_popup.batch_log.insert(f'{mini_df.shape[0]} minis found.\n')


def batch_find_in_range():
    _find_mini_range_thread(popup=False, undo=False)
    app.batch_popup.batch_log.insert(f'{mini_df.shape[0]} minis found.\n')


def batch_save_minis():
    if mini_df.shape[0] == 0:
        app.batch_popup.batch_log.insert('Warning: Exporting an empty data table.\n')
    fname = formatting.format_save_filename(
        os.path.splitext(app.batch_popup.current_filename)[0] + '.mini', overwrite=False
    )
    save_minis(fname, overwrite=False)
    app.batch_popup.batch_log.insert(f'Saved minis to: {fname}\n')

def batch_export_minis():
    if len(datapanel.table.get_children()) == 0:
        app.batch_popup.batch_log.insert('Warning: Exporting an empty data table.\n')
    fname = formatting.format_save_filename(
        os.path.splitext(app.batch_popup.current_filename)[0] + '_minis.csv', overwrite=False
    )
    datapanel.export(fname, overwrite=False)
    app.batch_popup.batch_log.insert(f"Exported minis to: {fname}\n")

# result deletion
def delete_clear(undo=False, draw=True):
    """
    Delete all results, including those from other channels
    """
    global mini_df
    if undo and mini_df.shape[0]>0: # there are results to be stored
        if app.interface.is_accepting_undo():
            # store the current data in a temp file. Open the csv if undo is called
            filename = app.interface.get_temp_filename()
            mini_df.to_csv(filename)
            controller.add_undo([
                lambda f=filename: open_minis(filename, log=False, undo=False, append=True),
                lambda f=filename: os.remove(f)
            ])
    mini_df = mini_df.iloc[0:0] # delete all data
    update_module_table()
    if draw:
        update_event_markers(draw=True)

def delete_all(undo=True, draw=True):
    """
    Delete all results in the datapanel
    """
    global mini_df
    if undo and len(datapanel.table.get_children())>0: # there are results to be stored
        if app.interface.is_accepting_undo():
            # store the current data in a temp file. Open the csv if undo is called
            filename = app.interface.get_temp_filename()
            mini_df.to_csv(filename)
            controller.add_undo([
                lambda f=filename: open_minis(filename, log=False, undo=False, append=True),
                lambda f=filename: os.remove(f)
            ])
    try:
        mini_df = mini_df[mini_df['channel'] != app.interface.current_channel]
    except:
        # probably no data yet (KeyError)
        pass
    if draw:
        update_event_markers(draw=True)
    update_module_table()

def delete_from_canvas(event=None, undo=True):
    """
    Delete button was pressed on the canvas while a mini was highlighted
    """
    datapanel.delete_selected(undo) # highlight = datapanel should be selected

def delete_in_window(event=None, undo=True):
    global mini_df
    xlim = app.trace_display.ax.get_xlim()
    selection = mini_df[(mini_df['t']>xlim[0])
                        & (mini_df['t']<xlim[1])
                        & (mini_df['channel'] == app.interface.current_channel)].t.values # corresponding t values
    delete_selection(selection, undo)

def delete_selection(selection:list, undo:bool=True, draw:bool=True):
    """
    Deletes data for minis specified by the 't' data.
    Not to be confused with delete_selected (which deletes whatever is selected in the GUI).
    """
    global mini_df
    if len(selection)==0:
        return # nothing to delete
    if undo and mini_df.shape[0]>0:
        if app.interface.is_accepting_undo():
            filename = app.interface.get_temp_filename()
            mini_df.to_csv(filename)
            controller.add_undo([
                lambda f=filename: open_minis(filename, log=False, undo=False, append=True),
                lambda f=filename: os.remove(f)
            ])
    mini_df = mini_df[(~mini_df['t'].isin(selection)) | (mini_df['channel'] != app.interface.current_channel)]
    datapanel.delete(selection) # delete the entries in the datapanel
    update_event_markers(draw=draw)

# getters
def extract_column(colname:str, t:list=None) -> list:
    """
    Called to extract data for specific column from the mini_df
    """
    try:
        return list(extract_channel_subset(t)[colname])
    except:
        pass

def extract_channel_subset(t:list=None) -> pd.DataFrame:
    """
    Call to get the mini data for the current channel only
    """
    global mini_df
    if len(app.interface.recordings) == 0: # not recording open yet
        return
    if mini_df.shape[0] == 0: # no data yet
        return
    if t: # the 't' values were specified
        return mini_df[(mini_df['t'].isin(t)) & (mini_df['channel'] == app.interface.current_channel)]
    else:
        return mini_df[mini_df['channel'] == app.interface.current_channel]

# mini finding
def find_mini_all(event=None, popup:bool=True, undo:bool=True):
    """
    Call to start the find_all process. Called by 'Find all' button.
    The function uses threading to run the find-all function.
    """
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    datapanel.unselect()
    if app.inputs['trace_mode'].get() != 'continuous': # should be disabled. Don't do anything
        return
    controller.start_thread(lambda i=popup, u=undo: _find_mini_all_thread(i, undo=u), mini_analysis,
                             popup)
    # if detector_tab.changed:
    #     log_display.search_update('Auto')
    #     log_display.param_update(detector_tab.changes)
    #     detector_tab.changes = {}
    #     detector_tab.changed = False
    log()

def _find_mini_all_thread(popup=True, undo=True):
    """
    Used to call the find-all algorithm from the mini_analysis module.
    Use this inside of a thread
    """
    global mini_df
    params = get_params()
    try:
        xs = app.trace_display.sweeps['Sweep_0'].get_xdata()
        ys = app.trace_display.sweeps['Sweep_0'].get_ydata()
    except:  # no traces yet
        return
    df = app.interface.al.find_mini_auto(xlim=None, xs=xs, ys=ys, x_sigdig=app.interface.recordings[0].x_sigdig,
                                         sampling_rate=app.interface.recordings[0].sampling_rate,
                                         channel=app.interface.current_channel,
                                         reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                                         x_unit=app.interface.recordings[0].x_unit, progress_bar=app.pb, **params)
    mini_df = pd.concat([mini_df, df])
    global saved
    if df.shape[0] > 0:
        # if int(app.widgets['config_undo_stack'].get()) > 0:
        #     add_undo([
        #         lambda iid=df['t'].values, u=False: delete_event(iid, undo=u),
        #         lambda msg='Undo mini search': detector_tab.log(msg)
        #     ])
        update_event_markers(draw=True)
        datapanel.append(df, undo=False)
        saved = False  # track change
        if undo and app.interface.is_accepting_undo():
            controller.add_undo(
                [lambda s=df[df.channel == app.interface.current_channel]['t']: delete_selection(s, undo=False)]
            )
    app.clear_progress_bar()
    if popup:
        controller.destroy_interrupt_popup()

def find_mini_at(x1, x2):
    """
    Searches for a single mini within [x1, x2)
    """
    global mini_df
    xs = app.trace_display.sweeps['Sweep_0'].get_xdata() # have a proper getter?
    ys = app.trace_display.sweeps['Sweep_0'].get_ydata()
    params = get_params()
    mini = app.interface.al.find_mini_manual(xlim=(x1,x2), xs=xs, ys=ys,
                                          x_sigdig=app.interface.recordings[0].x_sigdig,
                                          sampling_rate=app.interface.recordings[0].sampling_rate,
                                          channel=app.interface.current_channel,
                                          reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                                          x_unit=app.interface.recordings[0].x_unit, **params)

    global saved
    if mini['success']:
        mini_df = mini_df.append(mini,
                                           ignore_index=True,
                                           sort=False)
        mini_df = mini_df.sort_values(by='t')
        datapanel.add({key: value for key, value in mini.items() if key in mini_header2config},
                                 undo=False)
        update_event_markers(draw=True)
        saved = False  # track change
        controller.add_undo(
            [lambda s=(mini.get('t'),): delete_selection(s, undo=False)]
        )
    report_to_guide(mini=mini)

def find_mini_manual(x):
    """
    Searches for a single mini centering around x
    """
    if x is None: # no x
        return
    datapanel.unselect()
    xlim = app.trace_display.ax.get_xlim() # get the current window limits
    r = (xlim[1] - xlim[0]) * float(form.inputs['detector_core_search_radius'].get())/100 # calculate the search radius
    find_mini_at(max(x-r, xlim[0]), min(x+r, xlim[1]))
    log()

def find_mini_range(event=None, popup=True, undo=True):
    """
        Call to start the find-in-window process. Called by 'Find in window' button.
        The function uses threading to run the find-in-window algorithm
        """
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    datapanel.unselect()
    controller.start_thread(lambda i=popup, u=undo: _find_mini_range_thread(popup=i, undo=u), mini_analysis,
                             popup)
    log()

def _find_mini_range_thread(popup=True, undo=True):
    """
    Used to call the find-in-range algorithm from the mini_analysis module.
    Use this inside of a thread
    """
    global mini_df
    try:
        xs = app.trace_display.sweeps['Sweep_0'].get_xdata()
        ys = app.trace_display.sweeps['Sweep_0'].get_ydata()
    except:  # no traces yet
        return
    params = get_params()

    df = app.interface.al.find_mini_auto(xlim=app.trace_display.ax.get_xlim(), xs=xs, ys=ys,
                                         x_sigdig=app.interface.recordings[0].x_sigdig,
                                         sampling_rate=app.interface.recordings[0].sampling_rate,
                                         channel=app.interface.current_channel,
                                         reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                                         x_unit=app.interface.recordings[0].x_unit, progress_bar=app.pb, **params)
    mini_df = pd.concat([mini_df, df])
    global saved
    if df.shape[0] > 0:
        update_event_markers(draw=True)
        datapanel.append(df, undo=False)
        saved = False  # track change
        if undo and app.interface.is_accepting_undo():
            controller.add_undo(
                [lambda s=df[df.channel == app.interface.current_channel]['t']: delete_selection(s, undo=False)]
            )
    app.clear_progress_bar()
    if popup:
        controller.destroy_interrupt_popup()

def find_mini_reanalyze(selection:list, accept:bool=False):
    """
    reanalyze previously found (or analyzed) minis
    """
    global mini_df
    global saved
    try:
        xs = app.trace_display.sweeps['Sweep_0'].get_xdata()
        ys = app.trace_display.sweeps['Sweep_0'].get_ydata()
    except:  # no traces yet
        return

    data = mini_df[
        (mini_df['t'].isin(selection)) & (mini_df['channel'] == app.interface.current_channel)]
    if app.interface.is_accepting_undo():
        filename = app.interface.get_temp_filename()
        mini_df.to_csv(filename)
        controller.add_undo([
            lambda f=filename: open_minis(filename, log=False, undo=False, append=True),
            lambda f=filename: os.remove(f),
        ])
    try:
        if data.shape[0] > 0:  # assume reanalyzing all existing minis
            delete_selection(selection)
            peaks = data['peak_idx']
        else:
            peaks = [analyzer2.search_index(s, xs, app.interface.recordings[0].sampling_rate) for s in selection]
    except:  # analyzing something not in the table
        return

    hits = []
    params = get_params()
    if accept:
        params['min_amp'] = 0.0
        params['max_amp'] = np.inf
        params['min_decay'] = 0.0
        params['max_decay'] = np.inf
        params['min_hw'] = 0.0
        params['max_hw'] = np.inf
        params['min_rise'] = 0.0
        params['max_rise'] = np.inf
        params['min_drr'] = 0.0
        params['max_drr'] = np.inf
        params['min_s2n'] = 0.0
        params['max_s2n'] = np.inf
    for peak_idx in peaks:
        mini = app.interface.al.analyze_candidate_mini(xs=xs, ys=ys, peak_idx=peak_idx,
                                                       x_sigdig=app.interface.recordings[0].x_sigdig,
                                                       sampling_rate=app.interface.recordings[0].sampling_rate,
                                                       channel=app.interface.current_channel,
                                                       reference_df=mini_df,
                                                       y_unit=app.interface.recordings[0].y_unit,
                                                       x_unit=app.interface.recordings[0].x_unit, **params)
        if mini['success']:
            hits.append(mini)
    new_df = pd.DataFrame.from_dict(hits)
    if new_df.shape[0] > 0:
        mini_df = mini_df.append(new_df,
                                           ignore_index=True,
                                           sort=False)
        mini_df = mini_df.sort_values(by='t')
        datapanel.append(new_df, undo=False)
        saved = False  # track change
    if new_df.shape[0] <= 1:
        report_to_guide(mini=mini)
    update_event_markers(draw=True)
# result filtering
def filter_all(event=None):
    """
    Filters all the minis for the current channel
    """
    global mini_df
    if mini_df.shape[0] == 0: # no minis found yet, nothing to filter
        return
    if len(datapanel.table.get_children()) == 0: # no minis in the current channel
        return
    params = get_params()
    mini_df = mini_analysis.filter_mini(mini_df=mini_df, xlim=None, **params)
    update_event_markers(draw=True)
    update_module_table()
    app.clear_progress_bar()

def filter_window(event=None):
    global mini_df
    if mini_df.shape[0] == 0:  # no minis found yet, nothing to filter
        return
    if len(datapanel.table.get_children()) == 0:  # no minis in the current channel
        return
    params=get_params()
    xlim = app.trace_display.ax.get_xlim()
    mini_df = mini_analysis.filter_mini(mini_df=mini_df, xlim=xlim, **params)
    update_event_markers(draw=True)
    update_module_table()
    app.clear_progress_bar()

# parameter
def get_params():
    params = {}
    params['direction'] = {'negative': -1, 'positive': 1}[
        form.inputs['detector_core_direction'].get()]  # convert direction to int value
    params['compound'] = form.inputs['detector_core_compound'].get() == '1'
    params['decay_algorithm'] = form.inputs['detector_core_decay_algorithm'].get()

    for k, d in core_params.items():
        try:
            params[k] = d['conversion'](form.inputs[d['name']].get())
        except:
            if form.inputs[d['name']].get() == 'None':
                params[k] = None
            else:
                params[k] = form.inputs[d['name']].get()
    for k, d in filter_params.items():
        try:
            params[k] = d['conversion'](form.inputs[d['name']].get())
        except:
            if form.inputs[d['name']].get() == 'None' or form.inputs[d['name']].get() == '':
                params[k] = None
            else:
                params[k] = form.inputs[d['name']].get()
    for k, d in decay_params.items():
        try:
            params[k] = d['conversion'](form.inputs[d['name']].get())
        except:
            if form.inputs[d['name']].get() == 'None':
                params[k] = None
            else:
                params[k] = form.inputs[d['name']].get()
    if params['decay_algorithm'] == 'Curve fit (sing. exp.)':
        params['decay_algorithm'] = 'Curve fit'
    if params['compound']:
        for k, d in compound_params.items():
            try:
                params[k] = d['conversion'](form.inputs[d['name']].get())
            except:
                params[k] = form.inputs[d['name']].get()
    print(params)
    return params

# log
def log(event=None):
    """
    Log a message in the log_display
    """
    global logged
    # controller.log(f'Find mini.\n{str(changes)}', header=True)
    logged = True

def open_guide(event=None):
    pass

# open mini files
def open_minis(filename, log=True, undo=True, append=False):
    global mini_df
    global saved
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    # handle undo later
    filetype = os.path.splitext(filename)[1]
    if filetype not in ('.mini','.csv','.temp','.minipy'):
        if not messagebox.askyesno('Warning', f'{filetype} is not a recognized filetype. The file may not be read properly. Proceed?'):
            return
    filetype = os.path.splitext(filename)[1]
    df = pd.DataFrame()
    if filetype in ('.csv', '.temp', '.event', '.mini'):
        df = open_mini_csv(filename)
    elif filetype == '.minipy':
        df = open_minipy(filename)
    df = df.replace({np.nan: None})
    if undo and app.interface.is_accepting_undo():
        temp_filename = app.interface.get_temp_filename()
        save_minis(temp_filename, overwrite=True, log=False, update_status=False)
        controller.add_undo([
            lambda: open_minis(temp_filename, log=False, undo=False, append=False),
            lambda f=filename: os.remove(f)
            ])

    if not append:
        mini_df = df
        update_module_table()
        saved = True
    else:
        delete_clear(undo=False, draw=False)
        mini_df = mini_df.append(df)
        update_module_table()
    if log:
        controller.log(f'Open: {filename}', True)
    update_event_markers(draw=True)

    app.clear_progress_bar()

def open_mini_csv(self,filename):
    df = pd.read_csv(filename, comment='@')
    return df

def open_minipy(self,filename):
    """
    open mini files from Minipy (ancestral version)
    """
    channel = 0
    minis = []
    header_idx = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        for l in lines:
            info = l.strip().split(',')
            if info[0] == "@Trace":
                recording_filename = info[1]
            elif info[0] == '@Channel':
                channel = int(info[1])
            elif info[0] == '@Header':
                for i, h in enumerate(info):
                    header_idx[h] = i
                xs = app.interface.recordings[0].get_xs(mode='continuous', channel=channel)
                ys = app.interface.recordings[0].get_ys(mode='continuous', channel=channel)
            elif info[0] == '@Data':
                mini = {
                    't': float(info[header_idx['x']]),
                    'peak_coord_x': float(info[header_idx['x']]),
                    'peak_coord_y': float(info[header_idx['y']]),
                    'amp': float(info[header_idx['Vmax']]) * float(info[header_idx['direction']]),
                    'baseline': float(info[header_idx['baseline']]),
                    'compound': False,
                    'decay_A': float(info[header_idx['Vmax']]),
                    'decay_const': float(info[header_idx['tau']]) * 1000,
                    'decay_baseline': 0,
                    'decay_coord_x': float(info[header_idx['tau_x']]),
                    'decay_coord_y': float(info[header_idx['tau_y']]),
                    'decay_max_points': int(
                        float(self.widgets['detector_core_decay_max_interval'].get()) / 1000 * app.interface.recordings[
                            0].sampling_rate),
                    'failure': None,
                    'lag': int(info[header_idx['lag']]),
                    'rise_const': float(info[header_idx['rise_time']]) * 1000,
                    'start_coord_x': float(info[header_idx['left_x']]),
                    'start_coord_y': float(info[header_idx['left_y']]),
                    'amp_unit': app.interface.recordings[0].channel_units[channel],
                    'baseline_unit': app.interface.recordings[0].channel_units[channel],
                    'decay_unit': 'ms',
                    'halfwidth_unit': 'ms',
                    'rise_unit': 'ms',
                    'channel': channel,
                    'delta_x': 0,
                    'direction': int(info[header_idx['direction']]),
                    'end_coord_x': float(info[header_idx['right_x']]),
                    'end_coord_y': float(info[header_idx['right_y']]),
                    'max_amp': np.inf,
                    'min_amp': 0.0,
                    'max_rise': np.inf,
                    'min_rise': 0.0,
                    'max_decay': np.inf,
                    'min_decay': 0.0,
                    'max_hw': np.inf,
                    'min_hw': 0.0,
                    'max_s2n': np.inf,
                    'min_s2n': 0.0,
                    'stdev_unit': app.interface.recordings[0].channel_units[channel],
                    'success': True,
                }
                pass
                mini['start_idx'] = int(analyzer2.search_index(mini['start_coord_x'], xs,
                                                               rate=app.interface.recordings[0].sampling_rate))
                mini['baseline_idx'] = mini['start_idx']
                mini['base_idx_L'] = mini['start_idx'] - mini['lag']
                mini['base_idx_R'] = mini['start_idx']
                mini['decay_idx'] = int(analyzer2.search_index(mini['start_coord_x'] + mini['decay_const'], xs,
                                                               rate=app.interface.recordings[0].sampling_rate))
                mini['peak_idx'] = int(analyzer2.search_index(mini['peak_coord_x'], xs,
                                                              rate=app.interface.recordings[0].sampling_rate))
                mini['decay_start_idx'] = mini['peak_idx']
                mini['end_idx'] = analyzer2.search_index(mini['end_coord_x'], xs,
                                                         rate=app.interface.recordings[0].sampling_rate)
                mini['stdev'] = np.std(ys[mini['base_idx_L']:mini['base_idx_R']])

                # try finding halfwidth
                hw_start_idx, hw_end_idx = app.interface.al.find_mini_halfwidth(amp=mini['amp'],
                                                                                xs=xs[mini['baseline_idx']:mini[
                                                                                    'end_idx']],
                                                                                ys=ys[mini['baseline_idx']:mini[
                                                                                    'end_idx']],
                                                                                peak_idx=mini['peak_idx'] - mini[
                                                                                    'baseline_idx'],
                                                                                baseline=mini['baseline'],
                                                                                direction=mini['direction'])
                if hw_start_idx is not None and hw_end_idx is None:
                    if form.inputs['detector_core_extrapolate_hw'].get():
                        t = np.log(0.5) * (-1) * mini['decay_const'] / 1000
                        hw_end_idx = analyzer2.search_index(xs[mini['peak_idx']] + t, xs[mini['baseline_idx']:],
                                                            app.interface.recordings[0].sampling_rate)
                if hw_start_idx is None or hw_end_idx is None:
                    mini['halfwidth'] = 0  # could not be calculated
                else:
                    mini['halfwidth_start_idx'] = hw_start_idx + mini['baseline_idx']
                    mini['halfwidth_end_idx'] = hw_end_idx + mini['baseline_idx']
                    mini['halfwidth'] = (xs[int(mini['halfwidth_end_idx'])] - xs[
                        int(mini['halfwidth_start_idx'])]) * 1000
                    mini['halfwidth_start_coord_x'] = xs[mini['halfwidth_start_idx']]
                    mini['halfwidth_end_coord_x'] = xs[mini['halfwidth_end_idx']]
                    mini['halfwidth_start_coord_y'] = mini['halfwidth_end_coord_y'] = mini['baseline'] + 0.5 * mini[
                        'amp']

                minis.append(mini)
        if len(minis) > 0:
            df = pd.DataFrame.from_dict(minis)
            return df
        return pd.DataFrame()  # empty

def ask_open_minis(self, event=None):
    global mini_df
    if not saved and mini_df.shape[0]>0:
        choice = messagebox.askyesnocancel('Warning', 'Save mini data?')
        if choice is None:
            return
        if choice:
            ask_save_minis()

    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    filename = filedialog.askopenfilename(filetype=[('mini data files', '*.mini *.minipy *.csv'), ('All files', "*.*")],
                                          defaultextension='.mini')
    if filename:
        open_minis(filename)
    app.clear_progress_bar()
# plotting in trace_display
def plot_peak(xs, ys):
    try:
        markers['peak'].remove()
    except:
        pass
    try:
        markers['peak'] = app.trace_display.ax.scatter(xs, ys, marker='o', color=peak_color,
                                                                          s=peak_size**2, picker=True, animated=False)
    except:
        pass

def plot_decay(xs, ys):
    try:
        markers['decay'].remove()
    except:
        pass
    try:
        markers['decay'], = app.trace_display.ax.plot(xs, ys, marker='x', color=decay_color,
                                                                         markersize=decay_size, linestyle='None',
                                                                         animated=False)
    except:
        markers['decay'], = app.trace_display.ax.plot([], [], marker='x', color=decay_color,
                                                                         markersize=decay_size, linestyle='None',
                                                                         animated=False)
        pass

def plot_highlight(xs, ys):
    try:
        markers['highlight'].remove()
        markers['highlight'] = None
    except:
        pass
    try:
        markers['highlight'], = app.trace_display.ax.plot(xs, ys, marker='o', c=highlight_color,
                                                                             markersize=highlight_size, linestyle='None',
                                                                             animated=False, alpha=0.5)
    except:
        pass

def plot_start(xs, ys):
    try:
        markers['start'].remove()
    except:
        pass
    try:
        markers['start'], = app.trace_display.ax.plot(xs, ys, marker='x', color=start_color,
                                                                         markersize=start_size, linestyle='None',
                                                                         animated=False)
    except:
        markers['start'], = app.trace_display.ax.plot([], [], marker='x', color=decay_color,
                                                                         markersize=decay_size, linestyle='None',
                                                                         animated=False)

def record_param_change(pname, pvalue):
    """
    call this function to record the change in parameter
    Sets the changed attribute to True and records the parameter and value within changes
    """
    global changed
    global changes
    changed = True
    changes[pname] = pvalue

# report to other components
def report_results(event=None):
    """
    summarize the data in the datapanel and enter into the result_display
    It ignores many of the data that's found in mini_df
    """
    if len(app.interface.recordings)==0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return
    global mini_df
    if mini_df.shape[0] == 0:
        app.results_display.report({
            'filename': app.interface.recordings[0].filename,
            'analysis': 'mini',
            'num_minis': 0,
            'channel': app.interface.current_channel
        })
        return None
    df = mini_df[mini_df['channel'] == app.interface.current_channel]
    if df.shape[0] == 0:
        app.results_display.report({
            'filename': app.interface.recordings[0].filename,
            'analysis': 'mini',
            'num_minis': 0,
            'channel': app.interface.current_channel
        })
        return None
    data = {
        'filename': app.interface.recordings[0].filename,
        'analysis': 'mini',
        'num_minis': df.shape[0]
    }
    if 'amp' in datapanel.columns:
        data['amp'] = df['amp'].mean()
        data['amp_unit'] = df['amp_unit'].iloc[0]
        data['amp_std'] = df['amp'].std()
    if 'decay_const' in datapanel.columns:
        data['decay_const'] = df['decay_const'].mean()
        data['decay_unit'] = df['decay_unit'].iloc[0]
        data['decay_std'] = df['decay_const'].std()
    if 'rise_const' in datapanel.columns:
        data['rise_const'] = df['rise_const'].mean()
        data['rise_unit'] = df['rise_unit'].iloc[0]
        data['decay_std'] = df['rise_const'].std()
    if 'halfwidth' in datapanel.columns:
        data['halfwidth'] = df['halfwidth'].mean()
        data['halfwidth_unit'] = df['halfwidth_unit'].iloc[0]
        data['halfwidth_std'] = df['halfwidth'].std()
    if 'baseline' in datapanel.columns:
        data['baseline'] = df['baseline'].mean()
        data['baseline_unit'] = df['baseline_unit'].iloc[0]
        data['baseline_std'] = df['baseline'].std()
    if 'channel' in datapanel.columns:
        data['channel'] = app.interface.current_channel
    if 'compound' in datapanel.columns:
        data['num_compound'] = df['compound'].sum()
    # calculate frequency
    data['Hz'] = df.shape[0] / (df['t'].max() - df['t'].min())

    app.results_display.report(data)

def report_selected_results(self):
    """
    summarize the selected entries in the datapanel and enter into the result_display
    It ignores many of the data that's found in mini_df
    """
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        return None
    selection = [float(i) for i in datapanel.table.selection()]
    if len(selection) == 0:
        app.results_display.report({
            'filename': app.interface.recordings[0].filename,
            'analysis': 'mini',
            'num_minis': 0,
            'channel': app.interface.current_channel
        })
        return None
    global mini_df
    df = mini_df[
        (mini_df['channel'] == app.interface.current_channel) & (mini_df['t'].isin(selection))]
    data = {
        'filename': app.interface.recordings[0].filename,
        'analysis': 'mini',
        'num_minis': df.shape[0]
    }
    if 'amp' in datapanel.columns:
        data['amp'] = df['amp'].mean()
        data['amp_unit'] = df['amp_unit'].iloc[0]
        data['amp_std'] = df['amp'].std()
    if 'decay_const' in datapanel.columns:
        data['decay_const'] = df['decay_const'].mean()
        data['decay_unit'] = df['decay_unit'].iloc[0]
        data['decay_std'] = df['decay_const'].std()
    if 'rise_const' in datapanel.columns:
        data['rise_const'] = df['rise_const'].mean()
        data['rise_unit'] = df['rise_unit'].iloc[0]
        data['decay_std'] = df['rise_const'].std()
    if 'halfwidth' in datapanel.columns:
        data['halfwidth'] = df['halfwidth'].mean()
        data['halfwidth_unit'] = df['halfwidth_unit'].iloc[0]
        data['halfwidth_std'] = df['halfwidth'].std()
    if 'baseline' in datapanel.columns:
        data['baseline'] = df['baseline'].mean()
        data['baseline_unit'] = df['baseline_unit'].iloc[0]
        data['baseline_std'] = df['baseline'].std()
    if 'channel' in datapanel.columns:
        data['channel'] = app.interface.current_channel
    if 'compound' in datapanel.columns:
        data['num_compound'] = df['compound'].sum()
    # calculate frequency
    data['Hz'] = df.shape[0] / (df['t'].max() - df['t'].min())

    app.results_display.report(data)

def report_to_guide(event=None, mini=None):
    pass # do this later
    # if self.module.guide_window.visible:
    #     self.module.guide_window.clear()
    #     if mini is None:
    #         selection = [float(t) for t in self.module.data_tab.table.selection()]
    #         if len(selection) == 1:
    #             mini = self.mini_df[
    #                 (self.mini_df['t'].isin(selection)) & (self.mini_df['channel'] == app.interface.current_channel)]
    #             mini = mini.to_dict(orient='records')[0]
    #         else:
    #             return
    #     self.module.guide_window.report(xs=app.trace_display.sweeps['Sweep_0'].get_xdata(),
    #                                     ys=app.trace_display.sweeps['Sweep_0'].get_ydata(),
    #                                     data=mini)

# save minis
def save_minis(filename, overwrite=True, log=False, update_status = True):
    """
    Saves pandas dataframe mini_df to csv.
    """
    global mini_df
    global saved
    if overwrite:
        mode = 'w'
    else:
        mode = 'x'
    filename = formatting.format_save_filename(filename, overwrite)
    with open(filename, mode) as f:
        f.write(f'@filename: {app.interface.recordings[0].filename}\n')
        f.write(f'@version: {app.config.version}\n')
        f.write(mini_df.to_csv(index=False))
    if update_status:
        saved = True
    if log:
        controller.log(f'Minis saved to: {filename}', header=True)
    app.clear_progress_bar()

def ask_save_minis(self, event=None):
    """
    filedialog to ask where to save the mini data
    """
    global mini_df
    global saved
    if len(app.interface.recordings) == 0:
        messagebox.showerror('Error', 'Please open a recording file first')
        app.interface.focus()
        return None
    if mini_df.shape[0] == 0:
        if not messagebox.askyesno('Warning', 'No minis to save. Proceed?'):
            app.interface.focus()
            return None
    if not mini_filename:
        initialfilename = os.path.splitext(app.interface.recordings[0].filename)[0]

    filename = filedialog.asksaveasfilename(filetypes=[('mini file', '*.mini'),('csv file', '*.csv'), ('All files', '*.*')],
                                 defaultextension='.mini',
                                 initialfile=initialfilename)
    if not filename:
        app.interface.focus()
        return None
    try:
        save_minis(filename, overwrite=True, log=True, update_status=True)
        app.interface.focus()
        return filename
    except Exception as e:
        messagebox.showerror('Error', f'Could not write data to file.\n Error: {e}')
        app.interface.focus()
        return None

# mini selection
def select_all(event=None):
    pass

def select_from_event_pick(event=None):
    """
    Fire this function whenever a peak (pickable matplotlib scatter) is clicked by the user
    The mouse event should be passed as an argument
    """
    if not form.has_focus():
        return None
    global event_pick
    event_pick = True  # use this to avoid invoking other mouse-related events
    xdata, ydata = event.artist.get_offsets()[event.ind][0]
    if app.interpreter.multi_select:
        datapanel.selection_toggle([round(xdata, app.interface.recordings[0].x_sigdig)])
    else:
        datapanel.selection_set([round(xdata, app.interface.recordings[0].x_sigdig)])

def select_from_table(event=None):
    """
    This function should be called after the user selects entries on the datapanel
    """
    if not form.is_enabled():
        return None
    selection = [float(i) for i in datapanel.table.selection()]
    # pass a list of str for 't' column (index for table)
    if selection:
        xs = extract_column('peak_coord_x', selection)
        ys = extract_column('peak_coord_y', selection)
        if len(selection) == 1:
            app.trace_display.center_plot_on(xs, ys)
            report_to_guide()
        elif len(selection) > 1:
            app.trace_display.center_plot_area(min(xs), max(xs), min(ys), max(ys))

    else:
        xs = None
        ys = None
    plot_highlight(xs, ys)  # get peak coordinates
    app.trace_display.draw_ani()

def select_from_rect(self, event=None):
    """
    This function should be called in response to the user drawing a rect on the convas (drag)
    """
    if not form.has_focus():
        return None

    xlim = (app.interpreter.drag_coord_start[0], app.interpreter.drag_coord_end[0])
    xlim = (min(xlim), max(xlim))
    ylim = (app.interpreter.drag_coord_start[1], app.interpreter.drag_coord_end[1])
    ylim = (min(ylim), max(ylim))

    if mini_df.shape[0] == 0:
        return None
    df = mini_df[mini_df['channel'] == app.interface.current_channel]
    df = df[(df['t'] > xlim[0]) & (df['t'] < xlim[1])
            & (df['peak_coord_y'] > ylim[0]) & (df['peak_coord_y'] < ylim[1])]

    datapanel.selection_set(list(df['t']))

def select_clear(event=None):
    """
    Call this function to clear the mini selection
    """
    if not form.has_focus():
        return
    datapanel.unselect()

# update components
def update_event_markers(event=None, draw=False):
    """
    Sync the markers drawn on the canvas with the data stored in the plugin
    """
    if app.inputs['trace_mode'].get() == 'overlay':
        plot_peak(None, None)
        plot_decay(None, None)
        plot_start(None, None)
    elif app.inputs['trace_mode'].get() == 'continuous':
        plot_peak(extract_column('peak_coord_x'), extract_column('peak_coord_y'))
        plot_decay(extract_column('decay_coord_x'), extract_column('decay_coord_y'))
        plot_start(extract_column('start_coord_x'), extract_column('start_coord_y'))
        try:
            hxs = markers['highlight'].get_xdata()
            hys = markers['highlight'].get_ydata()
            plot_highlight(hxs, hys)
        except:
            pass
    if draw:
        app.trace_display.draw_ani()

def update_module_table():
    """
    Sync the datapanel entries with the data stored in the plugin
    """
    datapanel.set_data(extract_channel_subset())

#### Make GUI Components ####

controller = MiniController(name=name, menu_label=menu_label)
form = PluginForm(plugin_controller=controller, tab_label=tab_label, scrollbar=True, notebook=app.cp_notebook)
datapanel = MiniTable(plugin_controller=controller, tab_label=tab_label, notebook=app.data_notebook)


controller.children.append(form)
controller.children.append(datapanel)

#### Set up Form GUI ####

form.insert_title(text='Mini Analysis')
form.insert_button(text='Find all', command=find_mini_all)
form.insert_button(text='Delete all', command=delete_all)
form.insert_button(text='Find in\nwindow', command=find_mini_range)
form.insert_button(text='Delete in\nwindow', command=delete_in_window)
form.insert_button(text='Report stats', command=report_results)
form.insert_button(text='Open guide', command=open_guide)

form.insert_title(text='Core Parameters')
form.insert_label_optionmenu(name='detector_core_direction', text='Direction', options=['positive', 'negative'],
                             default=detector_core_direction)
# make dict of core parameters
form.insert_label_entry(name='detector_core_search_radius',
                        text='Search radius in % of the visible x-axis (Manual)',
                        validate_type='float',
                        default=detector_core_search_radius)
form.insert_label_entry(name='detector_core_auto_radius',
                        text='Search window in ms (Auto)',
                        validate_type='float',
                        default=detector_core_auto_radius)
form.insert_label_entry(name='detector_core_deltax_ms',
                        label='Window before peak to estimate baseline (ms)',
                        validate_type='float/zero',
                        default=detector_core_deltax_ms)
form.insert_label_entry(name='detector_core_lag_ms',
                        label='Window averaged to find start of mini (ms)',
                        validate_type='float',
                        default=detector_core_lag_ms)
form.insert_label_checkbox(name='detector_core_extrapolate_hw',
                           text='Use decay to extrapolate halfwidth',
                           onvalue='1',
                           offvalue='',
                           default=detector_core_extrapolate_hw)
# decay
form.insert_title(text='Decay fitting options')
form.insert_label_optionmenu(name='detector_core_decay_algorithm',
                             text='Decay calculation method:',
                             options=['Curve fit (sing. exp.)', '% amplitude'],
                             command=_populate_decay_algorithms,
                             default=detector_core_decay_algorithm)
form.insert_label_entry(name='detector_core_decay_p_amp',
                        text='Percent peak to mark as decay constant (%)',
                        validate_type='float',
                        default=detector_core_decay_p_amp)
form.insert_label_entry(name='detector_core_decay_best_guess',
                        text='Starting seed for exponential decay fit (ms)',
                        validate_type='float',
                        default=detector_core_decay_best_guess)
form.insert_label_entry(name='detector_core_decay_max_interval',
                        text='Maximum x-interval considered for decay (ms)',
                        validate_type='float',
                        default=detector_core_decay_max_interval)
# compound options
form.insert_label_checkbox(name='detector_core_compound',
                           text='Analyze compound minis',
                           onvalue='1',
                           offvalue='',
                           command=_populate_compound_params,
                           default=detector_core_compound)
form.insert_label_entry(name='detector_core_p_valley',
                        text='Minimum valley size in % of peak amplitude',
                        validate_type='float',
                        default=detector_core_p_valley)
form.insert_label_entry(name='detector_core_max_compound_interval',
                        text='Maximum inverval between two peaks to use compound mini analysis (ms)',
                        validate_type='flat',
                        default=detector_core_max_compound_interval)
form.insert_label_entry(name='detector_core_min_peak2peak',
                        text='Ignore minis closer than (ms)',
                        validate_type='float',
                        default=detector_core_min_peak2peak)

form.insert_button(text='Apply', command=_apply_parameters)
form.insert_button(text='Defauly', command=_default_core_params)

form.insert_title(text='Filtering parameters')

form.insert_label_entry(name='detector_filter_min_amp',
                        text='Minimum amplitude (absolute value)',
                        validate_type='float/None',
                        default=detector_filter_min_amp)
form.insert_label_entry(name='detector_filter_max_amp',
                        text='Maximum amplitude (aboslute value)',
                        validate_type='float/None',
                        default=detector_filter_max_amp)
form.insert_label_entry(name='detector_filter_min_decay',
                        text='Minimum decay constant (tau) (ms)',
                        validate_type='float/None',
                        default=detector_filter_min_decay)
form.insert_label_entry(name='detector_filter_max_decay',
                        text='Maximum decay constant (tau) (ms)',
                        validate_type='float/None',
                        default=detector_filter_max_decay)
form.insert_label_entry(name='detector_filter_min_hw',
                        text='Minimum halfwidth (ms)',
                        validate_type='float/None',
                        default=detector_filter_min_hw)
form.insert_label_entry(name='detector_filter_max_hw',
                        text='Maximum halfwidth (ms)',
                        validate_type='float/None',
                        default=detector_filter_max_hw)
form.insert_label_entry(name='detector_filter_min_rise',
                        text='Minimum rise constant (ms)',
                        validate_type='float/None',
                        default=detector_filter_min_rise)
form.insert_label_entry(name='detector_filter_max_rise',
                        text='Maximum rise constant (ms)',
                        validate_type='float/None',
                        default=detector_filter_max_rise)
form.insert_label_entry(name='detector_filter_min_dr',
                        text='Minimum decay/rise ratio',
                        validate_type='float/None',
                        default=detector_filter_min_dr)
form.insert_label_entry(name='detector_filter_max_dr',
                        text='Maximum decay/rise ratio',
                        validate_type='float/None',
                        default=detector_filter_max_dr)
form.insert_label_entry(name='detector_filter_min_s2n',
                        text='Minimum signal-to-noise ratio (amp/std)',
                        validate_type='float/None',
                        default=detector_filter_min_s2n)
form.insert_label_entry(name='detector_filter_max_s2n',
                        text='Maximum signal-to-noise ratio (amp/std)',
                        validate_type='float/None',
                        default=detector_filter_max_s2n)
form.insert_button(text='Confirm', command=_apply_parameters)
form.insert_button(text='Default', command=lambda filter='detector_filter':form.set_to_default(filter))
form.insert_button(text='Apply filter\n(all)', command=filter_all)
form.insert_button(text='Apply filter\n(window)', command=filter_window)

# column display
form.insert_label_checkbox(name='data_display_time',
                           text='Peak time',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_amplitude',
                           text='Amplitude',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_decay',
                           text='Decay constant',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_rise',
                           text='Rise duration',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_halfwidth',
                           text='Halfwidth',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_baseline',
                           text='Baseline',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_channel',
                           text='Channel',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_std',
                           text='Baseline stdev',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_direction',
                           text='Peak direction',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_label_checkbox(name='data_display_compound',
                           text='Compound',
                           command=_apply_column_options,
                           onvalue='1',
                           offvalue='',
                           default='1')
form.insert_button(text='Show All', command=_columns_show_all)
form.insert_button(text='Hide All', command=_columns_hide_all)
for widget in form.inputs:
    if type(widget) == type(custom_widgets.VarEntry):
        widget.bind('<Return>', _apply_parameters, add='+')
        widget.bind('<FocusOut>', _apply_parameters, add='+')

##### Batch Commands #####
controller.create_batch_category()
controller.add_batch_command('Find all', func=batch_find_all, interrupt=app.interface.al)
controller.add_batch_command('Find in window', func=batch_find_in_range, interrupt=app.interface.al)
controller.add_batch_command('Delete all', func=lambda u=False: delete_all(undo=u))
controller.add_batch_command('Delete in window', func=lambda u=False: delete_in_window(undo=u))
controller.add_batch_command('Report results', func=report_results)
controller.add_batch_command('Save minis', func=batch_save_minis)
controller.add_batch_command('Export minis', func=batch_export_minis)

#### setup Table GUI ####
for key in app.config.key_delete:
    datapanel.table.bind(key, datapanel.delete_selected, add='')
datapanel.define_columns(tuple([key for key in mini_header2config]), iid_header='t')
datapanel.table.bind('<<TreeviewSelect>>', select_from_table)


#### Modify Other GUI Components ####
# File menu
controller.add_file_menu_command(label='Open mini file', command=ask_open_minis)
controller.add_file_menu_command(label='Save minis as...', command=ask_save_minis)
controller.add_file_menu_command(label='Export data table', command=datapanel.ask_export_data)


controller.load_values()
_populate_decay_algorithms()

if app.inputs['trace_mode'].get() != 'continuous':
    try:
        controller.disable_module()
    except:
        pass

controller.listen_to_event('<<LoadCompleted>>', _apply_column_options)
controller.listen_to_event('<<LoadCompleted>>', controller.update_plugin_display)
def _on_open(event=None):
    delete_clear(undo=False, draw=False)
    logged = False
controller.listen_to_event('<<OpenRecording>>', _on_open)
form.listen_to_event('<<CanvasDrawRect>>', select_from_rect, condition='focused')
controller.listen_to_event('<<Plot>>', update_event_markers, condition='enabled')
controller.listen_to_event('<<Plotted>>', update_module_table, condition='enabled')
controller.listen_to_event('<<ChangeToOverlayView>>', controller.disable_module)
controller.listen_to_event('<<ChangeToContinuousView>>', controller.enable_module)
form.listen_to_event('<<CanvasMouseRelease>>', canvas_mouse_release, condition='focused')

parameters = get_params()
plugin_manager.mini_analysis.save = controller.save
