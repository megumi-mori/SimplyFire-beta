from SimplyFire.Backend.analyzer2 import Analyzer
import numpy as np
import matplotlib.pyplot as plt
from time import time

al = Analyzer()
al.open_file('D:\megum\Documents\GitHub\PyMini-GHD\\test_recordings\\19911002-2.abf')

#### overlay #####
print('testing overlay')
al.set_plot_mode('continuous')

xs = al.recording.get_xs(mode='continuous', channel=1)#, xlim=(0, 20))
ys = al.recording.get_ys(mode='continuous', channel=1)#, xlim=(0, 20))

t0=time()
al.find_mini_auto(xs=xs, ys=ys, min_amp=0.3, lag=100, direction = -1)
print(time()- t0)
print(al.mini_df)
plt.plot(xs, ys)

try:
    scatter_x = [xs[int(idx)] for idx in al.mini_df.peak_idx[:]]
    scatter_y = [ys[int(idx)] for idx in al.mini_df.peak_idx[:]]
    plt.scatter(scatter_x, scatter_y, c='red')
except:
    pass
plt.show()

# al.find_mini_auto(xs=xs, ys=ys, min_amp=0.2, lag=100, direction = -1)
#
# print(al.mini_df)
#
# plt.plot(xs, ys)
# try:
#     scatter_x = [xs[int(idx)] for idx in al.mini_df.peak_idx[:]]
#     scatter_y = [ys[int(idx)] for idx in al.mini_df.peak_idx[:]]
#     plt.scatter(scatter_x, scatter_y, c='red')
# except:
#     pass
# plt.show()
