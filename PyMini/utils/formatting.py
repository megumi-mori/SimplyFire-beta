

def format_list_indices(idx):
    if len(idx) == 1:
        return str(idx[0])
    s = ""
    for i, n in enumerate(idx):
        if i == 0:
            s = str(n)
        elif i == len(idx) - 1:
            if n - 1 == idx[-2]:
                s = '{}..{}'.format(s, n)
            else:
                s = '{},{}'.format(s, n)
        elif n - 1 == idx[i - 1] and n + 1 == idx[i + 1]:
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
