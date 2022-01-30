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

