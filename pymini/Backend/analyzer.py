# specific maths for event detection
# most likely won't require a class
from utils import recording
from config import config

### this module does all the calculations for event detection and modeling
### this module should be able to function on its own


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

def open_trace(filename, channel=0):
    global trace
    trace = recording.Trace(filename, channel=channel)

def find_single_event(
        x,
        xlim=None,
        ylim=None,
        dir=1,
        lag=config.detector_points_baseline,
        points_search=config.detector_points_search,
        max_points_baseline=config.detector_max_points_baseline,
        max_points_decay=config.detector_max_points_decay,
        min_amp=config.detector_min_amp,
        min_decay=config.detector_min_decay,
        min_hw=config.detector_min_hw,
        min_rise=config.detector_min_rise):
    d = {}


    return d
    pass

