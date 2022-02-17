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
import os

def format_list_indices(idx):
    if len(idx) == 1:
        return str(idx[0])
    s = ""
    for i, n in enumerate(idx):
        if i == 0:
            s = str(n)
        elif n == idx[i-1]: # same number as the one before
            pass
        elif i == len(idx) - 1:
            if n - 1 == idx[-2]: #at the end, at least 2 idx subsequent order
                s = '{}..{}'.format(s, n)
            else:
                s = '{},{}'.format(s, n)
        elif n - 1 == idx[i - 1] and n + 1 == idx[i + 1]: # in the middle of a sequence
            # 0, [1, 2, 3], 4, 10, 11 --> '0'
            pass  # do nothing
        elif n - 1 == idx[i - 1] and n + 1 != idx[i + 1]:
            # 0, 1, 2, [3, 4, 10], 11 --> '0..4'
            s = '{}..{}'.format(s, n)
        elif n - 1 != idx[i - 1]:
            # 0, 1, 2, 3, [4, 10, 11], 14, 16 --> '0..4,10' -->'0..4,10..11'
            s = '{},{}'.format(s, n)
    return s

def translate_indices(s):
    if not s:
        return []
    sections = s.split(',')
    indices = []
    for section in sections:
        idx = section.split('..') # should be left with indeces (int)
        if len(idx) == 1:
            indices.append(int(idx[0]))
        else:
            for i in range(int(idx[0]),int(idx[1])):
                indices.append(int(i))
    return indices

def translate_indices_bool(s, max_num):
    if not s:
        return [False]*max_num
    bool_list = [False]*max_num
    indices = translate_indices(s)

    for i in indices:
        if i < max_num:
            bool_list[i] = True
    return bool_list
def is_indices(s):
    # check formatting
    if not s:
        return True
    temp = s.replace('..', ',').split(',')
    # check every number is int
    for t in temp:
        try:
            int(t)
        except:
            return False
    try:
        translate_indices(s)
    except:
        return False
    return True


def format_save_filename(filename: str, overwrite=True, suffix_num: int = 0):
    # reformat file name to avoid errors
    # filename should contain the extension
    if suffix_num > 0:
        fname = f'{os.path.splitext(filename)[0]}({suffix_num}){os.path.splitext(filename)[1]}'
    else:
        fname = filename
    if not overwrite:
        if os.path.exists(fname):
            return format_save_filename(filename, overwrite, suffix_num+1)
        else:
            return fname
    return fname
