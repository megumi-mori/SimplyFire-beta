from pyabf import abf
import os.path
import numpy as np
import time
import pymini

class Trace():
    def __init__(self, filename):
        self.filename = filename
        self._open_file(filename)
        self.channel = 0

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

            total = self.sweep_count * (self.channel_count + 1)
            progress = 0
            pymini.pb.initiate()
            for i in range(self.channel_count):
                data.setSweep(channel=i, sweepNumber=0)
                for j in range(self.sweep_count):
                    data.setSweep(sweepNumber=j)
                    if i == 0:
                        self.x_data[j] = np.array(data.sweepX, 'f8')
                        progress += 1
                        pymini.pb.progress((progress/total * 100))
                    self.y_data[i][j] = np.array(data.sweepY, 'f8')
                    progress += 1
                    pymini.pb.progress((progress/total * 100))
            pymini.pb.clear()


            # implemenation to store sweep data as vstacks in np.array:
            # start = time.perf_counter()
            # self.x_data = np.array([])
            # self.y_data = [np.array([])] * self.channel_count
            #
            # for i in range(self.channel_count):
            #     data.setSweep(channel=i, sweepNumber=0)
            #     for j in range(self.sweep_count):
            #         data.setSweep(sweepNumber=j)
            #         try:
            #             if i==0:
            #                 self.x_data = np.vstack((self.x_data, np.array(data.sweepX, 'f8')))
            #             self.y_data[i] = np.vstack((self.y_data[i], np.array(data.sweepY, 'f8')))
            #         except:
            #             if i==0:
            #                 self.x_data=np.array(data.sweepX, 'f8')
            #             self.y_data[i] = np.array(data.sweepY, 'f8')
            # end = time.perf_counter()
            # print(start - end)
            # print(self.y_data[0])


    def set_channel(self, num):
        self.channel = num

    def get_ys(self, mode='continuous', sweep=0):
        """
        """
        if mode == 'continuous':
            ys = np.array([])
            for i in range(self.sweep_count):
                ys = np.concatenate((ys, self.y_data[self.channel][i]))
            return ys

            # code implementation for vstack of arrays to represent total data:
            # start = time.perf_counter()
            # d = self.y_data[self.channel].flatten()
            # end = time.perf_counter()
            # print(end - start)
            # return d
        else:
            return self.y_data[self.channel][sweep]

    def get_xs(self, mode='continuous', sweep=0):
        if mode == 'continuous':
            xs = np.array(self.x_data[0])
            for i in range(1, self.sweep_count):
                try:
                    xs = np.concatenate((xs, self.x_data[i] + xs[-1] + self.x_interval))
                except:
                    pass
            return xs
        else:
            return self.x_data[sweep]




