import tkinter as Tk
from tkinter import ttk
from math import isnan
from PyMini import app
from PyMini.Backend import analyzer2, interface
from PyMini.utils import widget
from PyMini.utils.widget import NavigationToolbar
from PyMini.config import config
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PyMini.DataVisualizer import trace_display, data_display
from functools import partial
import gc

def _on_close():
    app.widgets['window_param_guide'].set(0)
    window.withdraw()

def load():
    try:
        window.deiconify()
        print('recalling window')
    except:
        create_window()

def create_window():
    global window
    window=Tk.Toplevel(app.root)
    window.protocol('WM_DELETE_WINDOW', _on_close)
    window.title('Parameter guide')
    window.geometry('{}x{}'.format(config.geometry_param_guide[0], config.geometry_param_guide[1]))

    window.bind(config.key_reset_focus, lambda e: data_display.table.focus_set())


    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # notebook_frame = Tk.Frame(
    #     window
    # )
    # notebook_frame
    # notebook_frame.grid(column=0, row=0, sticky='news')
    notebook = ttk.Notebook(window)
    notebook.grid(column=0, row=0, sticky='news')
    pw = Tk.PanedWindow(
        window,
        # notebook_frame,
        orient=Tk.VERTICAL,
        showhandle=True,
        sashrelief=Tk.SUNKEN,
        handlesize=config.default_pw_handlesize
    )
    notebook.add(pw, text='Panel')
    # pw.grid(column=0, row=0, sticky='news')
    #
    frame = Tk.Frame(
        pw,
        bg='red'
    )
    fig = Figure()
    fig.set_tight_layout(True)
    frame.grid(column=0, row=0, sticky='news')
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=1)
    pw.add(frame)
    pw.paneconfig(frame, height=config.default_param_guide_height)

    plot_frame = Tk.Frame(frame, bg='pink')
    plot_frame.grid(column=0, row=1, sticky='news')

    global ax
    ax = fig.add_subplot(111)
    fig.subplots_adjust(right=1, top=1)

    global canvas
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    ax.plot()

    msg_frame = Tk.Frame(pw)
    msg_frame.grid(column=0, row=0, sticky='news')
    msg_frame.grid_columnconfigure(0, weight=1)
    msg_frame.grid_rowconfigure(0, weight=1)

    button_frame = Tk.Frame(msg_frame)
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)
    button_frame.grid(column=0, row=1, sticky='news')

    global accept_button
    accept_button = ttk.Button(button_frame, text='Ignore filter\nparams')
    accept_button.grid(column=0, row=0, sticky='news')
    accept_button.config(state='disabled')
    accept_button.bind('<Button>', accept)

    global reanalyze_button
    reanalyze_button = ttk.Button(button_frame, text='Reanalyze')
    reanalyze_button.grid(column=1, row=0, sticky='news')
    reanalyze_button.config(state='disabled')
    reanalyze_button.bind('<Button>', reanalyze)

    global reject_button
    reject_button = ttk.Button(button_frame, text='Reject')
    reject_button.grid(column=2, row=0, sticky='news')
    reject_button.config(state='disabled')
    reject_button.bind('<Button>', reject)

    # global goto_button
    # goto_button = ttk.Button(button_frame, text='Select')
    # goto_button.grid(column=3, row=0, sticky='news')
    # goto_button.config(state='disabled')
    # goto_button.bind('<Button>', canvas.get_tk_widget().focus_set())



    pw.add(msg_frame)


    global msg_label
    msg_label = widget.VarText(parent=msg_frame, name='param_guide_msg', value="", default="", state='disabled')
    msg_label.grid(column=0, row=0, sticky='news')
    Tk.Text.configure(msg_label, font=Tk.font.Font(size=int(float(app.widgets['font_size'].get()))))

    vsb = ttk.Scrollbar(msg_frame, orient=Tk.VERTICAL, command=msg_label.yview)
    vsb.grid(column=1, row=0, sticky='ns')
    # msg_label.configure(yscrollcommand=vsb.set)

    toolbar_frame = Tk.Frame(frame)

    toolbar = NavigationToolbar(canvas, toolbar_frame)
    toolbar.grid(column=0, row=0, sticky='news')
    toolbar_frame.grid(column=0, row=0, sticky='news')


    update()

def accept(e=None):
    global mini_data
    interface.reanalyze(mini_data, accept_all=True)
    canvas.get_tk_widget().focus_set()

def update():
    try:
        ax.set_xlabel(trace_display.ax.get_xlabel(), fontsize=int(float(app.widgets['font_size'].get())))
        ax.set_ylabel(trace_display.ax.get_ylabel(), fontsize=int(float(app.widgets['font_size'].get())))
        ax.tick_params(axis='y', which='major', labelsize=int(float(app.widgets['font_size'].get())))
        ax.tick_params(axis='x', which='major', labelsize=int(float(app.widgets['font_size'].get())))
        canvas.draw()
    except Exception as e:
        print(f'param_guide update error {e}')
        pass
def clear():
    try:
        accept_button.config(state='disabled')
        reanalyze_button.config(state='disabled')
        reject_button.config(state='disabled')
        # goto_button.config(state='disabled')
        msg_label.clear()
        for l in ax.lines:
            l.remove()
        for c in ax.collections:
            c.remove()
        ax.clear()
        canvas.draw()
        gc.collect()
        global peak
        peak = None
    except:
        pass

def configure_buttons(**kwargs):
    global accept_button
    accept_button.config(**kwargs)

    global reanalyze_button
    reanalyze_button.config(**kwargs)

    global reject_button
    reject_button.config(**kwargs)

def plot_trace(xs, ys, label=None):
    if label is None:
        label = 'Recording'
    try:
        ax.plot(xs, ys, linewidth=app.widgets['style_trace_line_width'].get(),
                c=app.widgets['style_trace_line_color'].get(), label=label)
        ax.autoscale(enable=True, axis='both', tight=True)
        ax.relim()
    except Exception as e:
        print('plot_trace error {}'.format(e))
        pass
def plot_recording(xs, ys, xlim=None):
    ax.plot(xs, ys, linewidth=app.widgets['style_trace_line_width'].get(),
            c=app.widgets['style_trace_line_color'].get(),
            label='Recording')
    ax.autoscale(enable=True,axis='both',tight=True)
    ax.relim()
    if xlim:
        ax.set_xlim(xlim)
        xlim_idx = (analyzer2.search_index(xlim[0], xs), analyzer2.search_index(xlim[1], xs))
        ax.set_ylim(min(ys[xlim_idx[0]:xlim_idx[1]]), max(ys[xlim_idx[0]: xlim_idx[1]]))





def plot_search(xs, ys):
    ax.plot(xs, ys, linewidth=1,
            c='blue',
            alpha=0.1,
            label='Search range')



def plot_baseline_calculation(xs, ys):
    try:
        ax.plot(xs, ys, linewidth=app.widgets['style_trace_line_width'].get(),
                c=app.widgets['style_event_start_color'].get(), label='baseline')
        # canvas.draw()
    except:
        pass

def plot_start(x, y):
    try:
        ax.scatter(x, y, marker='x', c=app.widgets['style_event_start_color'].get(),
                   label='Event start')
        # canvas.draw()
    except Exception as e:
        print(f'plot start error param_guide: {e}')
        pass

def plot_base_range(xs, ys):
    ax.plot(xs, ys, linewidth=3,
            c='pink',
            alpha=0.5,
            label='Baseline sample')

def plot_peak(x, y):
    try:
        global peak
        peak = ax.scatter(x, y, marker='o', c=app.widgets['style_event_peak_color'].get(),
                          s=float(app.widgets['style_event_peak_size'].get())**2,
                          label='Peak')
        # canvas.draw()
    except Exception as e:
        print(e)
        pass

def plot_amplitude(peak_coord, baseline):
    ax.plot([peak_coord[0], peak_coord[0]], [peak_coord[1], baseline],
            linewidth = app.widgets['style_trace_line_width'].get(),
            c='black',
            # label='Amplitude'
            )

def plot_base_simple(start_x, end_x, baseline):
    ax.plot([start_x, end_x], [baseline, baseline],
            linewidth = app.widgets['style_trace_line_width'].get(),
            c='black',
            # label='Baseline'
            )

def plot_base_extrapolate(xs, A, decay, baseline, direction):
    ax.plot(xs, analyzer2.single_exponent(xs-xs[0], A, decay) * direction + baseline,
            linewidth=2,
            c='blue',
            alpha=0.1,
            label='Prev decay'
            )
    pass
def plot_ruler(coord1, coord2):
    try:
        ax.plot([coord1[0], coord2[0]], [coord1[1], coord2[1]], linewidth = float(app.widgets['style_trace_line_width'].get()), c='black')
        # canvas.draw()
    except Exception as e:
        print(e)
        pass

def plot_decay_fit(xs, A, decay, decay_base=0, baseline=0, direction=1):
    # try:
    ax.plot(xs, analyzer2.single_exponent_constant(xs-xs[0], A, decay, decay_base)*direction + baseline,
            linewidth=app.widgets['style_trace_line_width'].get(),
            c=app.widgets['style_event_decay_color'].get(),
            label='Decay fit')
def plot_decay_extrapolate(xs,A,decay,decay_base,baseline,prev_A,prev_decay,prev_base,prev_t,direction):
    y = analyzer2.single_exponent_constant(xs-xs[0],A,decay,decay_base)*direction
    prev_y = analyzer2.single_exponent_constant(xs-prev_t,prev_A, prev_decay, prev_base) * direction
    ys = y + prev_y
    ax.plot(xs, ys,linewidth = app.widgets['style_trace_line_width'].get(),
            c=app.widgets['style_event_decay_color'].get(),
            label='Decay fit')
    pass

def plot_decay_point(x, y):
    ax.scatter(x, y, marker='x', c=app.widgets['style_event_decay_color'].get(),
               label='t=decay constant')

def plot_halfwidth(coord1, coord2):
    ax.plot([coord1[0], coord2[0]], [coord1[1],coord2[1]],
            linewidth=app.widgets['style_trace_line_width'].get(),
            c='black')

def reanalyze(e=None):
    global mini_data
    interface.reanalyze(mini_data)
    canvas.get_tk_widget().focus_set()

def reject(e=None):
    global mini_data
    interface.delete_event([mini_data['t']])
    canvas.get_tk_widget().focus_set()
def report(xs, ys, data, clear_plot=False):
    global mini_data
    mini_data = data
    global msg_label
    if clear:
        clear()
    print(data['failure'])
    if data['failure'] is not None:
        msg_label.insert(data['failure']+'\n')
    try:
        try:
            start = int(min(max(data['start_idx'] - data['lag'] - data['delta_x'], 0), data['xlim_idx_L']))
        except:
            start = int(max(data['start_idx'] - data['lag'] - data['delta_x'], 0))
        if data['compound']:
            start = min(start, int(data['prev_peak_idx']))
        try:
            end = int(max(min(data['peak_idx'] + data['decay_max_points'], len(xs)), data['xlim_idx_R']))
        except:
            end = int(min(data['peak_idx'] + data['decay_max_points'], len(xs)))
        plot_recording(
            xs[start:end],
            ys[start:end],
            xlim=(xs[int(max(data['start_idx'] - data['lag'], 0))],
                  xs[int(min(data['peak_idx'] + data['decay_max_points'], len(xs) - 1))])
        )
        plot_start(data['start_coord_x'], data['start_coord_y'])
    except Exception as e:  # start not found
        print(f'param_guide report plot recording call {e}')
        pass

    try:
        msg_label.insert(f"Peak: {data['peak_coord_x']:.3f},{data['peak_coord_y']:.3f}\n")
        plot_peak(data['peak_coord_x'], data['peak_coord_y'])
        plot_amplitude((data['peak_coord_x'], data['peak_coord_y']), data['baseline'])
    except:  # peak not found
        pass

    try:
        if data['base_idx_L'] is not None and not data['compound']:
            plot_base_range(
                xs[int(data['base_idx_L']):int(data['base_idx_R'])],
                ys[int(data['base_idx_L']):int(data['base_idx_R'])]
            )
    except Exception as e:
        print(f'base idx plotting exception {e}')
        pass
    try:
        msg_label.insert('Baseline: {:.3f} {}\n'.format(data['baseline'], data['baseline_unit']))
        msg_label.insert('Amplitude: {:.3f} {}\n'.format(data['amp'], data['amp_unit']))
        msg_label.insert('Rise: {:.3f} {}\n'.format(data['rise_const'], data['rise_unit']))
    except:
        pass
    try:
        if not data['compound']:
            plot_base_simple(xs[int(data['start_idx'])], xs[end], data['baseline'])
        else:
            plot_base_extrapolate(
                xs=xs[int(data['prev_peak_idx']):end],
                A=data['prev_decay_A'],
                decay=data['prev_decay_const'] / 1000,
                baseline=data['prev_baseline'],
                direction=data['direction']
            )
            pass
    except:
        pass
    try:
        msg_label.insert('Decay: {:.3f} {}\n'.format(data['decay_const'], data['decay_unit']))
        msg_label.insert(f'Decay:rise ratio: {data["decay_const"] / data["rise_const"]}\n')
        try:
            if not data['compound']:
                plot_decay_fit(xs=xs[int(data['peak_idx']):end],
                               A=data['decay_A'],
                               decay=data['decay_const'] / 1000,
                               decay_base=data['decay_baseline'],
                               baseline=data['baseline'],
                               direction=data['direction'])
            else:
                plot_decay_extrapolate(xs=xs[int(data['peak_idx']):end],
                                       A=data['decay_A'],
                                       decay=data['decay_const']/1000,
                                       decay_base=data['decay_baseline'],
                                       baseline=data['baseline'],
                                       prev_A=data['prev_decay_A'],
                                       prev_decay=data['prev_decay_const']/1000,
                                       prev_base=data['prev_decay_baseline'],
                                       prev_t=data['prev_t'],
                                       direction=data['direction'])
        except:
            plot_decay_fit(xs=xs[int(data['peak_idx']):end],
                           A=data['decay_A'],
                           decay=data['decay_const'] / 1000,
                           baseline=data['baseline'],
                           direction=data['direction'])
        plot_decay_point(data['decay_coord_x'], data['decay_coord_y'])
    except Exception as e:
        print(e)
    try:
        plot_halfwidth((data['halfwidth_start_coord_x'], data['halfwidth_start_coord_y']),
                                   (data['halfwidth_end_coord_x'], data['halfwidth_end_coord_y']))
        msg_label.insert(f'Halfwidth: {data["halfwidth"]:.3f} {data["halfwidth_unit"]}\n')
    except:
        pass
    try:
        msg_label.insert(f'Signal-to-noise ratio: {data["amp"]*data["direction"]/data["stdev"]:.3f}\n')
    except:
        pass
    show_legend()
    canvas.draw()
    update()

    global accept_button
    accept_button.config(state='normal')

    global reanalyze_button
    reanalyze_button.config(state='normal')

    global reject_button
    if data['success']:
        reject_button.config(state='normal')
    else:
        reject_button.config(state='disabled')

def show_legend():
    ax.legend(frameon=False)

def hide_legend():
    ax.legend().set_visible(False)

