from pyabf import abf
import os.path
import numpy as np
import gc

## DEBUGGING
import tracemalloc
from datetime import datetime
class Trace():
    def __init__(self, filename, channel=0):
        self.filename = filename
        self._open_file(filename)
        self.channel = 0
        self.set_channel(channel)
        self.added_sweep_count = 0

    def _open_file(self, filename):
        self.filetype = os.path.splitext(self.filename)[1]
        _, self.fname = os.path.split(self.filename)
        if self.filetype == ".abf":
            data = abf.ABF(filename)
            self.data = data
            self.sampling_rate = data.dataRate
            self.sampling_rate_sigdig = len(str(self.sampling_rate)) - 1
            self.x_interval = 1 / self.sampling_rate

            self.channel_count = data.channelCount
            self.channel_names = data.adcNames
            self.channel_units = data.adcUnits
            self.channel_labels = [""] * self.channel_count
            self.x_unit = data.sweepUnitsX
            self.x_label = data.sweepLabelX # in the form of Label (Units)

            self.sweep_count = data.sweepCount
            self.original_sweep_count = self.sweep_count
            self.added_sweep_count = 0
            # self.x_data = [[] for _ in range(self.sweep_count)]
            # self.y_data = [[[] for _ in range(self.sweep_count)] for _ in range(self.channel_count)]

            self.sweep_points = data.sweepPointCount

            self.y_data = np.reshape(data.data, (self.channel_count, self.sweep_count, self.sweep_points))
            self.x_data = np.repeat(np.reshape(data.sweepX, (1,self.sweep_points)), self.sweep_count, axis=0)
            for c in range(self.channel_count):
                data.setSweep(0, c)
                self.channel_labels[c] = data.sweepLabelY

    def save_ydata(self, filename, channels=None, sweeps=None):
        if not channels:
            channels = [i for i in range(self.channel_count)]
        if not sweeps:
            sweeps = range(self.sweep_count)
        with open(filename, 'w') as f:
            for c in channels:
                for i in sweeps:
                    f.write(','.join([str(d) for d in self.y_data[c][i].tolist()]))
                    f.write('\n')
        return None

    def load_ydata(self, filename, channels=None, sweeps=None):
        if not channels:
            channels = range(self.channel_count)
        if not sweeps:
            sweeps = range(self.sweep_count)
        with open(filename, 'r') as f:
            for c in channels:
                for i in sweeps:
                    self.y_data[c, i] = np.fromstring(f.readline(), dtype=float, sep=',')
        return None

    def set_ydata(self, channels=None, sweeps=0, data=None, mode='continuous'):
        if channels is None:
            channels = [self.channel]
        if sweeps is None:
            sweeps = [i for i in range(self.sweep_count)]
        if data is None:
            return None
        if mode == 'continuous':
            data = np.reshape(data, (len(channels), len(sweeps), self.sweep_points))
        for i,c in enumerate(channels):
            self.y_data[c, sweeps] = data[i, sweeps]
        # self.y_data[(channels, sweeps)] = data[:, :]


    def delete_sweep(self, num):
        for c in range(self.channel_count):
            self.y_data[c].pop(num)
        self.x_data.pop(num)
        self.sweep_count = len(self.x_data)


    def delete_last_sweep(self):
        if self.sweep_count == self.original_sweep_count:
            print('Cannot delete original data')
            return None
        self.y_data = self.y_data[:, :-1, :]
        self.x_data = self.x_data[:-1, :]
        self.sweep_count = len(self.x_data)
        self.added_sweep_count -= 1


    def set_channel(self, num):
        if num >= self.channel_count:

            raise Exception('specified channel does not exist')
        else:
            self.channel = num
            self.y_label = self.channel_labels[num]
            self.y_unit = self.channel_units[num]

    def append_sweep(self, data, channel=0):
        if len(data) == len(self.y_data):
            self.y_data = np.append(self.y_data, data, axis=1)
        else:
            temp_data = np.empty((self.channel_count, 1, self.sweep_points))
            temp_data[:] = np.nan
            temp_data[channel, 0] = np.array(data, 'f8')
            self.y_data = np.append(self.y_data, temp_data, axis=1)
        self.x_data = np.append(self.x_data, np.reshape(self.x_data[-1], (1,self.sweep_points)), axis=0)

        self.sweep_count = len(self.x_data)
        print(self.sweep_count)
        self.added_sweep_count = self.sweep_count - self.original_sweep_count

    def get_y_data(self, mode='continuous', sweeps=None, channels=None):
        """
        returns a slice of the y_data
        mode: string
            'continuous', 'overlay'
        sweeps: list of int
        """
        if channels == None:
            channels = [self.channel]
        if sweeps == None:
            if mode == 'continuous':
                sweeps = [i for i in range(self.sweep_count)]
            elif mode == 'overlay':
                sweeps = [0]
        if mode == 'continuous':
            return np.reshape(self.y_data[(channels, sweeps)], (len(channels), 1, len(sweeps)*self.sweep_points))
        return self.y_data[channels][:, sweeps]

    def get_x_data(self, mode='continuous', sweeps=None):
        """
        returns a slice of the x_data
        mode: string
            'continuous', 'overlay'
        sweeps: list of int
        """
        if sweeps is None:
            sweeps = range(self.sweep_count)
        if mode == 'continuous':
            offset = (self.x_data[sweeps][:, -1]+self.x_interval)*np.arange(0, len(sweeps))
            offset = np.reshape(offset, (len(sweeps), 1))
            return np.reshape(self.x_data[sweeps] + offset, (1, len(sweeps)*self.sweep_points))
        return self.x_data[sweeps]

    def get_xs(self, mode='continuous', sweep=None):
        """
        returns numpy array representing the x-values in the recording.
        mode: string
            continuous, concatenate, or None
            if continuous, all sweeps are included
        sweep: int
        """
        if mode == 'continuous':
            return self.get_x_data(mode='continuous').flatten()
        return self.get_x_data(mode='overlay', sweeps=[sweep]).flatten()

    def get_ys(self, mode='continuous', sweep=None, channel=None):
        """
        returns a numpy array representing the y-values of the recording.
        mode: string
            'continuous', 'overlay', or None
            if 'continuous', all sweeps are represented
        sweep: int
        channel: int
            if empty, the current channel in the object is used
        """
        if channel == None:
            channel = self.channel
        if mode == 'continuous':
            return self.get_y_data(mode='continuous', channels=[channel]).flatten()
        return self.get_y_data(mode=mode, channels=[channel], sweeps=[sweep]).flatten()


    def average(self, sweeps=None, channels=None):
        if channels is None:
            channels = [self.channel]
        if sweeps is None:
            sweeps = [range(0, self.sweep_count)]
        return np.mean(self.y_data[channels][sweeps], axis=1)


    def forget(self):
        self.y_data = None
        self.x_data = None

    def find_index(self, x, sweep=None, mode='continuous'):
        """
        Used to estimate the index of the x value in the dataset.
        Use only if there is a chance that x may not be an exact match in the data
        :param x: x that may not be in the actual data
        :return:
        """
        if mode == 'continuous':
            return self._search_index(x, self.x_data_c, self.sampling_rate)

        if mode == 'sweep':
            if sweep is None:
                return -1 #cannot determine which sweep
            return self._search_index(x, self.x_data[self.channel][sweep], self.sampling_rate)

    def _search_index(self, x, l, rate):
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







