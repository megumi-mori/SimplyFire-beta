from pyabf import abf
import os.path
import numpy as np
class Trace():
    def __init__(self, filename):
        self.filename = filename
        self._open_file(filename)

    def _open_file(self, filename):
        self.filetype = os.path.splitext(self.filename)[1]
        if self.filetype == ".abf":
            data = abf.ABF(filename)
            self.sampling_rate = data.dataRate
            self.sampling_rate_sigdig = len(str(self.sampling_rate)) - 1
            self.x_interval = 1 / self.sampling_rate

            self.channel_count = data.channelCount
            self.channel_names = data.adcNames
            self.channel_units = data.adcUnits
            self.x_unit = data.sweepUnitsX

            self.sweep_count = data.sweepCount
            self.x_data = [0]*self.sweep_count
            self.y_data = [[0] * self.sweep_count] * self.channel_count

            for i in range(self.channel_count):
                data.setSweep(channel=i, sweepNumber=0)
                for j in range(self.sweep_count):
                    data.setSweep(sweepNumber=j)
                    if i == 0:
                        self.x_data[j] = np.array(data.sweepX, 'f8')
                    self.y_data[i][j] = np.array(data.sweepY, 'f8')



