from PyMini.Modules.base_module_popup import BaseModulePopup
from PyMini.Backend import analyzer2 as analyzer
from tkinter import ttk
import tkinter as Tk
from PyMini import app
from PyMini.utils import custom_widgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import gc
import numpy as np
class ModulePopup(BaseModulePopup):
    def __init__(self, module):
        super().__init__(
            module=module,
            name='guide_window'
        )
        self.data = None
        self._load_layout()
        self.tracker = False
    def clear(self, event=None):
        self.tracker = False
        try:
            # buttons
            self.msg_label.clear()
            for l in self.ax.lines:
                l.remove()
            for c in self.ax.collections:
                c.remove()
            self.ax.clear()
            self.canvas.draw()
            gc.collect()
        except:
            pass
        self.data = None

    def report(self, xs:np.ndarray, ys:np.ndarray, data:dict):
        print('report called')
        self.clear()
        self.data = data
        if data['failure']:
            self.msg_label.insert(text=str(data.get('failure'))+'\n')
        else:
            self.msg_label.insert(text='Success!'+'\n')
        try:
            start, end = self.plot_recording(xs, ys, data) # start coordinate and the plot
        except:
            pass
        try:
            self.msg_label.insert(f'Peak: {data["peak_coord_x"]:.3f}, {data["peak_coord_y"]:.3f}\n')
            self.plot_peak(data['peak_coord_x'], data['peak_coord_y'])
            self.plot_amplitude(data['peak_coord_x'], data['peak_coord_y'], data['baseline'])
        except KeyError:
            pass
        try:
            if data['base_idx_L'] is not None and not data['compound']:
                self.plot_base_range(xs, ys, data)
        except:
            pass

        try:
            self.msg_label.insert(f'Baseline: {data["baseline"]:.3f} {data["baseline_unit"]}\n')
            if data['compound']:
                self.msg_label.insert(f'Baseline extrapolated from preceding mini\n')
            else:
                left_idx = data.get('base_idx_L', None)
                right_idx = data.get('base_idx_R', None)
                if left_idx and right_idx:
                    self.msg_label.insert(f'Baseline calculated by averaging: {xs[int(left_idx)]:.3f}-{xs[int(right_idx)]:.3f}\n')
                else:
                    self.msg_label.inesrt(f'Baseline calculated by averaging data points.\n')
        except:
            pass

        try:
            self.msg_label.insert(f"Amplitude: {data['amp']:.3f} {data['amp_unit']}\n")
        except:
            pass
        try:
            self.msg_label.insert(f"Rise: {data['rise_const']:.3f} {data['rise_unit']}\n")
        except:
            pass

        try:
            if not data['compound']:
                self.plot_base_simple(xs, end, data)
            else:
                self.plot_base_extrapolate(xs, end, data)
        except:
            pass

        try:
            self.msg_label.insert(f'Decay: {data["decay_const"]:.3f} {data["decay_unit"]}\n')
            if data['min_drr'] > 0 or data['max_drr'] is not np.inf:
                self.msg_label.insert(f'Decay:rise ratio: {data["decay_const"]/data["rise_const"]:.3f}\n')
        except:
            pass

        try:
            if not data['compound']:
                self.plot_decay_fit(xs, end, data)
            else:
                self.plot_decay_extrapolate(xs, end, data)
        except:
            pass

        try:
            self.plot_decay_point(data)
        except:
            pass

        try:
            self.plot_halfwidth(data)
            self.msg_label.insert(f'Halfwidth: {data["halfwidth"]:.3f} {data["halfwidth_unit"]}\n')
        except:
            pass

        try:
            self.msg_label.insert(f'Signal-to-noise ratio: {data["amp"]*data["direction"]/data["stdev"]:.3f}\n')
        except:
            pass
        self.ax.legend(frameon=False)
        self.ax.autoscale(enable=True, axis='y', tight=False)
        self.ax.relim()

        self.canvas.draw()
    #### plotting to guide ####
    def plot_amplitude(self, x, y, baseline):
        if not x or not y:
            return None
        self.ax.plot((x, x), (y, baseline),
                     linewidth=app.trace_display.trace_width,
                     c='black',
                     alpha=0.9)

    def plot_base_extrapolate(self, xs, end, data):
        print('plot base extrapolate called')
        self.tracker = True
        try:
            if self.tracker:
                raise
        except:
            pass
        xs = xs[int(data['prev_peak_idx']):end]
        A = data['prev_decay_A']
        decay = data['prev_decay_const']/1000
        baseline = data['prev_baseline']
        direction = data['direction']
        self.ax.plot(xs, analyzer.single_exponent(xs-xs[0], A, decay) * direction + baseline,
                     linewidth=app.trace_display.trace_width,
                     c='black',
                     alpha=0.9,
                     label='Prev decay'
                     )

    def plot_base_range(self, xs, ys, data):
        self.ax.plot(xs[int(data['base_idx_L']): int(data['base_idx_R'])],
                     ys[int(data['base_idx_L']): int(data['base_idx_R'])],
                     linewidth=app.trace_display.trace_width*3,
                     c='pink',
                     alpha=0.9,
                     label='Baseline sample')

    def plot_base_simple(self, xs, end, data):
        x1 = xs[int(data['start_idx'])]
        x2 = xs[end]
        baseline = data['baseline']
        self.ax.plot([x1, x2], [baseline, baseline],
                     linewidth=app.trace_display.trace_width,
                     c='black',
                     alpha=0.9)

    def plot_decay_fit(self, xs, end, data):
        xs = xs[int(data['peak_idx']):end]
        A = data['decay_A']
        tau = data['decay_const']/1000
        decay_base = data['decay_baseline'] # support for constant
        baseline = data['baseline']
        direction = data['direction']

        self.ax.plot(xs,
                     analyzer.single_exponent_constant(xs-xs[0], A, tau, decay_base)*direction + baseline,
                     linewidth=app.trace_display.trace_width,
                     c=self.module.control_tab.decay_color,
                     label='Decay fit')

    def plot_decay_extrapolate(self, xs, end, data):
        xs = xs[int(data['peak_idx']):end]
        A = data['decay_A']
        tau = data['decay_const']/1000
        decay_base = data['decay_baseline'] # support for constant
        baseline = data['baseline']
        direction = data['direction']

        ys = analyzer.single_exponent_constant(xs-xs[0], A, tau, decay_base)*direction

        delta_t = data['t'] - data['prev_t']
        prev_A = data['prev_decay_A']
        prev_decay=data['prev_decay_const'] / 1000
        prev_base=data['prev_decay_baseline']

        prev_ys = analyzer.single_exponent_constant(xs-xs[0]+delta_t, prev_A, prev_decay, prev_base) *direction

        ys = ys + prev_ys + baseline

        self.ax.plot(xs, ys, linewidth=app.trace_display.trace_width,
                     c=self.module.control_tab.decay_color,
                     label='Decay fit')

    def plot_decay_point(self, data):
        self.ax.plot(data['decay_coord_x'], data['decay_coord_y'], marker='x',
                     c=self.module.control_tab.decay_color,
                     markersize=self.module.control_tab.decay_size,
                     label='t=tau')
    def plot_halfwidth(self, data):
        self.ax.plot((data['halfwidth_start_coord_x'], data['halfwidth_end_coord_x']),
                     (data['halfwidth_start_coord_y'], data['halfwidth_end_coord_y']),
                     linewidth=app.trace_display.trace_width,
                     alpha=0.9,
                     c='black'
                     )
    def plot_peak(self, x, y):
        if not x or not y:
            return None
        self.peak = self.ax.plot(x, y, marker='o', c=self.module.control_tab.peak_color,
                     markersize=self.module.control_tab.peak_size,
                     linestyle='None',
                     label='Peak')

    def plot_recording(self, xs, ys, data):
        start_lim_idx = int(max(data.get('start_idx', 0) - data.get('lag', 0) - data.get('delta_x', 0), 0))
        start_idx = int(min(start_lim_idx, data.get('xlim_idx_L', np.inf)))
        if data['compound']:
            start_idx = int(min(start_idx, int(data['prev_peak_idx'])))

        end_lim_idx = int(min(data.get('peak_idx', 0) + data.get('decay_max_points', 0), len(xs)-1))
        end_idx = int(max(end_lim_idx, data.get('xlim_idx_R', 0)))

        self.ax.plot(xs[start_idx:end_idx],
                ys[start_idx:end_idx],
                linewidth=app.trace_display.trace_width,
                color=app.trace_display.trace_color,
                )
        self.ax.set_xlim((xs[start_lim_idx], xs[end_lim_idx]))
        self.plot_start(xs[int(data['start_idx'])], ys[int(data['start_idx'])])
        return start_idx, end_idx

    def plot_start(self, x, y):
        self.ax.plot(x, y, marker='x', c=self.module.control_tab.start_color,
                     markersize=self.module.control_tab.start_size,
                     label='Event start')

    def update(self, event=None):
        self.ax.set_xlabel(app.trace_display.ax.get_xlabel(),
                           fontsize=int(app.widgets['font_size'].get()))
        self.ax.set_ylabel(app.trace_display.ax.get_ylabel(),
                           fontsize=int(app.widgets['font_size'].get()))
        self.ax.tick_params(axis='y', which='major', labelsize=int(app.widgets['font_size'].get()))
        self.ax.tick_params(axis='y', which='major', labelsize=int(app.widgets['font_size'].get()))
        self.canvas.draw()

    ###############################
    def accept(self, event=None):
        self.module.control_tab.find_mini_reanalyze((self.data['t'],), accept=True)
        pass

    def reanalyze(self, event=None):
        self.module.control_tab.find_mini_reanalyze((self.data['t'],))

        pass

    def reject(self, event=None):
        self.select_mini()
        self.module.data_tab.delete_selected()
        pass

    def select_mini(self, event=None):
        try:
            self.module.data_tab.table.selection_set([str(self.data['t'])])
        except:
            pass

    def _update_geometry_var(self, event=None):
        self.widgets['guide_geometry_height'].set(
            self.winfo_height()
        )
        self.widgets['guide_geometry_width'].set(
            self.winfo_width()
        )
    def _load_layout(self):
        self.widgets['guide_geometry_height'] = Tk.IntVar(
            value=self.module.values.get('guide_geometry_height', self.module.default.get('guide_geometry_height', 600)))
        self.widgets['guide_geometry_width'] = Tk.IntVar(
            value=self.module.values.get('geometry_width', self.module.default.get('guide_geometry_width', 200)))

        # self.geometry(f'{self.widgets["guide_geometry_height"].get()}x{self.widgets["guide_geometry_width"].get()}')
        self.geometry(f'400x600')
        # # self.geometry(f'200x600')
        # self.bind('<Configure>', self._update_geometry_var, add='+')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # self.notebook = ttk.Notebook(self)
        # self.notebook.grid(column=0, row=0, sticky='news')
        self.pw = Tk.PanedWindow(
            self,
            orient=Tk.VERTICAL,
            showhandle=True,
            sashrelief=Tk.SUNKEN,
            handlesize=app.config.default_pw_handlesize
        )

        self.pw.grid(column=0, row=0, sticky='news')

        frame = Tk.Frame(
            self.pw
        )

        frame.grid(column=0, row=0,sticky='news')
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        self.pw.add(frame)
        self.pw.paneconfig(frame, height=self.module.values.get('guide_panel_height',
                                                                self.module.default.get('guide_panel_height', 400)))
        self.fig = Figure()
        self.fig.set_tight_layout(True)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(right=1, top=1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(column=0, row=1, sticky='news')
        self.ax.plot()

        self.toolbar = custom_widgets.NavigationToolbar(self.canvas, frame)
        self.toolbar.grid(column=0, row=0, sticky='news')

        msg_frame = Tk.Frame(self.pw)
        msg_frame.grid(column=0, row=0, sticky='news')
        msg_frame.grid_columnconfigure(0, weight=1)
        msg_frame.grid_rowconfigure(0, weight=1)

        button_frame = Tk.Frame(msg_frame)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_columnconfigure(0, weight=0)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)
        button_frame.grid_columnconfigure(3, weight=0)
        button_frame.grid(column=0, row=1, sticky='news')

        self.accept_button = ttk.Button(button_frame, text='Remove\nRestrictions', command=self.accept)
        self.accept_button.grid(column=0, row=0, sticky='news')

        self.reanalyze_button = ttk.Button(button_frame, text='Reanalyze', command=self.reanalyze)
        self.reanalyze_button.grid(column=1, row=0, sticky='news')

        self.reject_button = ttk.Button(button_frame, text='Reject', command=self.reject)
        self.reject_button.grid(column=2, row=0, sticky='news')

        self.pw.add(msg_frame)

        self.msg_label = custom_widgets.VarText(parent=msg_frame,
                                                name='guide_msg',
                                                value='',
                                                default='',
                                                state='disabled')
        self.msg_label.grid(column=0, row=0, sticky='news')
        Tk.Text.configure(self.msg_label, font=Tk.font.Font(size=int(float(app.widgets['font_size'].get()))))

        vsb = ttk.Scrollbar(msg_frame, orient=Tk.VERTICAL, command=self.msg_label.yview)
        vsb.grid(column=1, row=0, sticky='ns')

        self.update()


