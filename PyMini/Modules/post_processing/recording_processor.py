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
    for c in channels:
        ys = recording.get_y_matrix(mode='continuous', channels=[c], sweeps=sweeps)
        filtered = np.convolve(ys.flatten(), kernel, mode='same')
        filtered = np.reshape(filtered, (1,1,len(filtered)))
        filtered[:, :, :int(width/2)] = ys[:,:,:int(width/2)] # prevent 0-ing of the edges
        filtered[:, :, -int(width/2):] = ys[:,:,-int(width/2):] # prevent 0-ing of the edges
        recording.replace_y_data(mode='continuous', channels=[c], sweeps=sweeps, new_data=filtered)

    return recording

