import numpy as np
from PyMini.Backend import analyzer2

def subtract_baseline(recording:analyzer2.Recording,
                      plot_mode:str='continuous',
                      channels:list=None,
                      sweeps:list=None,
                      xlim:tuple=None,
                      shift:float=None,
                      inplace:bool=True):
    """

    """
    assert type(recording) == analyzer2.Recording, f'data passed must be of type {analyzer2.Recording}'
    assert plot_mode in ['continuous', 'overlay'], 'plot_mode argument must be in ["continuous", "overlay"]'
    if not channels:
        channels = range(recording.channel_count)
    if not sweeps:
        sweeps = range(recording.sweep_count)
    if shift is not None:
        baseline = shift
    else:
        baseline = np.mean(recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps, xlim=xlim),
                           axis=2,  # per sweep per channel
                           keepdims=True)
        pass
    result = recording.get_y_matrix(mode=plot_mode, channels=channels, sweeps=sweeps) - baseline
    final_result = recording.replace_y_data(mode=plot_mode, channels=channels, sweeps=sweeps, new_data=result,
                                            inplace=inplace)
    return final_result, baseline

def filter_Boxcar(recording:analyzer2.Recording,
                  params:dict=None,
                  channels:list=None,
                  sweeps:list=None,
                  ):
    assert type(recording) == analyzer2.Recording, f'data passed must be of type {analyzer2.Recording}'
    width = int(params['width'])
    kernel = np.ones(width)/width
    if not channels:
        channels = range(recording.channel_count)
    if not sweeps:
        sweeps = range(recording.sweep_count)
    for c in channels:
        ys = recording.get_y_matrix(mode='continuous', channels=[c], sweeps=sweeps)
        filtered = np.convolve(ys.flatten(), kernel, mode='same')
        filtered = np.reshape(filtered, (1,1,len(filtered)))
        filtered[:, :, :int(width/2)] = ys[:,:,:int(width/2)] # prevent 0-ing of the edges
        filtered[:, :, -int(width/2):] = ys[:,:,-int(width/2):] # prevent 0-ing of the edges
        recording.replace_y_data(mode='continuous', channels=[c], sweeps=sweeps, new_data=filtered)

    return recording


# implement Boxel 8pole 1000Hz!

def average_sweeps(recording:analyzer2.Recording,
                   channels:list=None,
                   sweeps:list=None):
    assert type(recording) == analyzer2.Recording, f'data passed must be of type {analyzer2.Recording}'
    if not channels:
        channels = range(recording.channel_count)
    if not sweeps:
        sweeps = range(recording.sweep_count)
    print(recording.y_data.dtype)
    # create an empty matrix
    result = np.full((recording.channel_count, 1, recording.sweep_points),
                     fill_value=0,
                     dtype=np.float32)
    result[channels] = np.mean(recording.get_y_matrix(mode='overlay', sweeps=sweeps, channels=channels),
                               axis=1, #average sweeps per channel
                               keepdims=True)
    return result