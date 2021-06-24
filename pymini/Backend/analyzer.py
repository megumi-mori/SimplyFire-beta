# specific maths for event detection
# most likely won't require a class

def search_index(x, l, rate):
    print("{} : {}".format(x, l[0]))
    est = int((x - l[0]) * rate)
    if est >= len(l):
        return len(l)  # out of bounds
    elif l[est] == x:
        return est
    elif l[est] > x:  # overshot
        while est >= 0:
            if l[est] < x:
                return est + 1
            est -= 1
    elif l[est] < x:  # need to go higher
        while est < len(l):
            if l[est] > x:
                return est
            est += 1
    return est  # out of bounds