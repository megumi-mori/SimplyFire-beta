from PyMini import app
from PyMini.Backend import analyzer2

def find_mini_manual(x, params, mini_df):
    # connect to param_guide later
    xlim = app.trace_display.ax.get_xlim()
    xlim = (min(xlim), max(xlim))
    ylim = app.trace_display.ax.get_ylim()
    ylim = (min(ylim), max(ylim))

    # convert % x-axis to points search using sampling rate?
    r = (xlim[1] - xlim[0]) * float(params['manual_radius']) / 100
    xs = app.trace_display.ax.lines[0].get_xdata()
    ys = app.trace_display.ax.lines[0].get_ydata()

    mini = app.interface.al.find_mini_manual(xlim=(max(x - r, xlim[0]), min(x + r, xlim[1])), xs=xs, ys=ys,
                           x_sigdig=app.interface.recordings[0].x_sigdig,
                           sampling_rate=app.interface.recordings[0].sampling_rate, channel=app.interface.recordings[0].channel,
                           reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                           x_unit=app.interface.recordings[0].x_unit, **params)

    return mini

def find_mini_in_range(params, mini_df, xlim=None, ylim=None):
    app.pb['value'] = 0
    app.pb.update()

    try:
        xs = app.trace_display.ax.lines[0].get_xdata()
        ys = app.trace_display.ax.lines[0].get_ydata()
    except:
        return

    # temp_filename = os.path.join(pkg_resources.resource_filename('PyMini', 'temp/'), 'temp_{}.temp'.format(get_temp_num()))
    # save_events(temp_filename)
    # add_undo([
    #     lambda f=temp_filename: al.load_minis_from_file(f),
    #     restore_events,
    #     lambda msg='Undo auto mini detection in range: {} - {}'.format(xlim[0], xlim[1]): detector_tab.log(msg)
    # ])

    df = app.interface.al.find_mini_auto(xlim=xlim, xs=xs, ys=ys, x_sigdig=app.interface.recordings[0].x_sigdig,
                               sampling_rate=app.interface.recordings[0].sampling_rate, channel=app.interface.recordings[0].channel,
                      reference_df=mini_df, y_unit=app.interface.recordings[0].y_unit,
                               x_unit=app.interface.recordings[0].x_unit, progress_bar=app.pb, **params)
    return df