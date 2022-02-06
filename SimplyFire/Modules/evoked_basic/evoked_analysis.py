"""
SimplyFire - Customizable analysis of electrophysiology data
Copyright (C) 2022 Megumi Mori
This program comes with ABSOLUTELY NO WARRANTY

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from SimplyFire.utils.recording import Recording

def calculate_min_sweeps(recording:Recording,
                         plot_mode:str='continuous',
                         channels:list=None,
                         sweeps:list=None,
                         xlim:tuple=None):
    assert type(recording)==Recording, f'data passed must be of type {Recording}'
    assert plot_mode in ['continuous', 'overlay'], 'plot_mode argument must be in ["continuous", "overlay"]'
    if channels is None:
        channels = range(recording.channel_count)
    if sweeps is None:
        sweeps = range(recording.sweep_count)

    y_matrix = recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels, xlim=xlim)
    mins = np.min(y_matrix, axis=2, keepdims=True) # get the minimum in each sweep
    mins_std = np.std(mins, axis=1, keepdims=True)

    return mins, mins_std

def calculate_max_sweeps(recording:Recording,
                         plot_mode:str='continuous',
                         channels:list=None,
                         sweeps:list=None,
                         xlim:tuple=None):
    assert type(recording) == Recording, f'data passed must be of type {Recording}'
    assert plot_mode in ['continuous', 'overlay'], 'plot_mode argument must be in ["continuous", "overlay"]'
    if channels is None:
        channels = range(recording.channel_count)
    if sweeps is None:
        sweeeps = range(recording.sweep_count)
    y_matrix = recording.get_y_matrix(mode=plot_mode, sweeps=sweeps, channels=channels, xlim=xlim)

    maxs = np.max(y_matrix, axis=2, keepdims=True) # get the max in each sweep per channel
    maxs_std = np.std(maxs, axis=1, keepdims=True)
    return maxs, maxs_std