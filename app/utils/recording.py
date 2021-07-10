from pyabf import abf
import os.path
import numpy as np
import gc

## DEBUGGING
import tracemalloc

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
            self.x_data = [[] for _ in range(self.sweep_count)]
            self.y_data = [[[] for _ in range(self.sweep_count)] for _ in range(self.channel_count)]

            total = self.sweep_count * (self.channel_count + 1)
            progress = 0
            # pymini.pb.initiate()
            for i in range(self.channel_count):
                data.setSweep(channel=i, sweepNumber=0)
                self.channel_labels[i] = data.sweepLabelY
                for j in range(self.sweep_count):
                    data.setSweep(channel=i, sweepNumber=j)
                    if i == 0:
                        self.x_data[j] = np.array(data.sweepX, 'f8')
                        progress += 1
                        # pymini.pb.progress((progress/total * 100))
                    self.y_data[i][j] = np.array(data.sweepY, 'f8')
                    progress += 1
                    # pymini.pb.progress((progress/total * 100))
            # pymini.pb.clear()


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

    def save_ydata(self, filename, channels=None, progress_bar = None):
        if not channels:
            channels = [i for i in range(self.channel_count)]
        task_length = len(channels) * self.sweep_count
        task_progress = 1
        with open(filename, 'w') as f:
            for j in channels:
                f.write('Channel,{},Sweeps,{}\n'.format(j, self.sweep_count))
                for i in range(self.sweep_count):
                    if progress_bar is not None:
                        progress_bar['value'] = task_progress/task_length*100
                        progress_bar.update()
                    f.write(','.join([str(d) for d in self.y_data[j][i].tolist()]))
                    f.write('\n')
        gc.collect()
        return None

    def load_ydata(self, filename):
        with open(filename, 'r') as f:
            l = f.readline()
            while l:
                if l.split(',')[0] == 'Channel':
                    j = int(l.split(',')[1])
                    if l.split(',')[2] == 'Sweeps':
                        sweep_length = int(l.split(',')[3])
                    else:
                        sweep_length = self.sweep_count
                    for i in range(sweep_length):
                        self.y_data[j][i] = np.fromstring(f.readline(), dtype=float, sep=',')
                l = f.readline()
        gc.collect()
        return None

    def set_ydata(self, channel=None, sweep=0, data=None):
        if channel is None:
            channel = self.channel
        if data is None:
            return None
        self.y_data[channel][sweep] = np.array(data)

    def delete_sweep(self, num):
        for c in range(self.channel_count):
            self.y_data[c].pop(num)
        self.x_data.pop(num)
        self.sweep_count = len(self.x_data)


    def delete_last_sweep(self):
        for c in range(self.channel_count):
            self.y_data[c].pop()

        temp = self.x_data.pop()
        del temp
        if self.sweep_count == self.original_sweep_count:
            print('Cannot delete original data')
            return None
        self.sweep_count = len(self.x_data)
        self.added_sweep_count -= 1


    def set_channel(self, num):
        if num >= self.channel_count:

            raise Exception('specified channel does not exist')
        else:
            self.channel = num
            self.y_label = self.channel_labels[num]
            self.y_unit = self.channel_units[num]

    def add_sweep(self, channel=0, data=None):
        if data is None:
            return None
        self.y_data[channel].append(np.array(data))
        self.sweep_count = max(map(len, self.y_data))
        self.added_sweep_count = self.sweep_count - self.original_sweep_count
        if len(self.x_data) != len(self.y_data[channel]):
            self.x_data.append(np.array([self.x_interval * i for i in range(len(self.y_data[channel][-1]))]))


    def get_ys(self, mode='continuous', sweep=0, sweeps=None, channel=None):
        """
        mode: continuous, concatenate, or None
        """
        if channel == None:
            channel = self.channel
        if mode == 'continuous':
            ys = np.array([])
            for i in range(self.sweep_count):
                ys = np.concatenate((ys, self.y_data[channel][i]))
            return ys

            # code implementation for vstack of arrays to represent total data:
            # start = time.perf_counter()
            # d = self.y_data[self.channel].flatten()
            # end = time.perf_counter()
            # print(end - start)
            # return d
        elif mode == 'concatenate' and sweeps:
            ys = np.array([])
            for i in sweeps:
                ys = np.concatenate((ys, self.y_data[channel][i]))
            return ys
        else:
            return self.y_data[channel][sweep]

    def get_xs(self, mode='continuous', sweep=0, sweeps=None):
        """
               mode: continuous, concatenate, or None
               """
        if mode == 'continuous':
            xs = np.array(self.x_data[0])
            for i in range(1, self.sweep_count):
                try:
                    xs = np.concatenate((xs, self.x_data[i] + xs[-1] + self.x_interval))
                except:
                    pass
            # self.x_data_c = xs
            return xs
        elif mode == 'concatenate' and sweeps:
            xs = np.array(self.x_data[0])
            for i in sweeps[1:]:
                try:
                    xs = np.concatenate((xs, self.x_data[i] + xs[-1] + self.x_interval))
                except:
                    pass
            return xs
        else:
            return self.x_data[sweep]

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







