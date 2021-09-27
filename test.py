from PyMini.Backend.analyzer2 import Analyzer
import numpy as np
import matplotlib.pyplot as plt
from time import time

al = Analyzer()
al.open_file('D:\megum\Documents\GitHub\PyMini-GHD\\test_recordings\\19911002-2.abf')

#### overlay #####
print('testing overlay')
al.set_plot_mode('continuous')

# test plotting function
# al.plot(channels=[0, 1], xlim=(0, 0.25))
# al.plot(plot_mode='overlay')

# test minimum calculation
# print('testing min_sweep calculation')
# print(al.calculate_min_sweeps(plot_mode='overlay', channels=[0,1], xlim=(0,1)))
# print(al.calculate_max_sweeps(plot_mode='overlay', channels=[0,1], xlim=(0, 0.2)))

# test append calculation
# al.append_average_sweeps(channels=[1])
# al.plot(channels=[1])

# test filtering
# al.filter_sweeps(filter='boxcar', params={'width':11}, channels=[0, 1])
# al.plot(channels=[0,1], xlim=(0.025, 0.075))
# al.plot(channels=[0, 1], xlim=(0, 0.25))

#test closest
# al.find_closest_sweep_to_point((0.1, -20), xlim=(0, 0.25), ylim=(-25, 5), channels=[1], radius=0.08)

#test replace y_value
# al.recording.replace_y_data(mode='overlay', sweeps=[0,5,7], channels=[0, 1], new_data=np.zeros((2, 3, al.recording.sweep_points)))
# al.plot(channels=[0, 1])
# al.recording.replace_y_data(mode='continuous', sweeps=[0,5,7], channels=[0, 1], new_data=np.zeros((2, 1, al.recording.sweep_points*3)))
# al.plot(channels=[0, 1])

# test baseline subtract
# al.subtract_baseline(plot_mode='overlay', channels=[1], xlim=(0.0212, 0.0213))
# al.plot(plot_mode='overlay', channels=[1])

# test mini finding
# t0 = time()
# xs = al.recording.get_xs(mode='continuous', channel=1)
# ys = al.recording.get_ys(mode='continuous', channel=1)
# print(time() - t0)
# t0 = time()
# plt.plot(xs, ys)
# mini_idx = al.find_mini_manual(xs=xs, ys=ys, point=(0.46, 0.0), radius=0.1, direction = -1, lag=50)
# # mini_idx = al.find_mini_manual(xs=xs, ys=ys, point=(2.03, 0.0), radius=0.01, direction = -1, lag=50)
# # mini_idx = al.find_mini_manual(xs=xs, ys=ys, point=(0.03, 0.0), radius=0.01, direction = -1, lag=50)
# # print(time() - t0)
#
# for i in al.mini_df.index:
#     plt.scatter(al.mini_df.iloc[i]['peak_coord_x'],
#                 al.mini_df.iloc[i]['peak_coord_y'])
#     plt.scatter(al.mini_df.iloc[i]['start_coord_x'],
#                 al.mini_df.iloc[i]['start_coord_y'])
#     plt.scatter(al.mini_df.iloc[i]['decay_coord_x'],
#                 al.mini_df.iloc[i]['decay_coord_y'])
#     plt.scatter(al.mini_df.iloc[i]['halfwidth_start_coord_x'],
#                 al.mini_df.iloc[i]['halfwidth_start_coord_y'])
#     plt.scatter(al.mini_df.iloc[i]['halfwidth_end_coord_x'],
#                 al.mini_df.iloc[i]['halfwidth_end_coord_y'])
# plt.show()
# plt.plot(al.recording.get_xs(mode='continuous', channel=1, xlim=(0.02, 0.04)),
#          al.recording.get_ys(mode='continuous', channel=1, xlim=(0.02, 0.04)),
#          color='red')
# print(mini_idx)
# plt.show()

xs = al.recording.get_xs(mode='continuous', channel=1)#, xlim=(0, 0.1))
ys = al.recording.get_ys(mode='continuous', channel=1)#, xlim=(0, 0.1))
# t0=time()
# hits = al.find_mini_2(xs, ys, direction = -1)
# al.find_mini_2(xs, ys, lag = 200, delta_x=70, direction=-1)
# print(time()-t0)
# hits = al.find_mini_3(xs, ys, direction=-1)


# scatter_x = [xs[int(idx)] for idx in al.mini_df.peak_idx[:]]
# scatter_y = [ys[int(idx)] for idx in al.mini_df.peak_idx[:]]
#
# baseline_x = [xs[int(idx)] for idx in al.mini_df.base_idx[:]]
# baseline_y = [ys[int(idx)] for idx in al.mini_df.base_idx[:]]
# scatter_y = [ys[h] for h in hits]

y_avg = [0]*len(ys)
lag = 1000
delta_x = 70
idx = 0
y_avg[idx + lag + delta_x] = np.mean(ys[idx:idx+lag])
while idx < len(ys) - (lag + delta_x + 1):
    y_avg[idx + lag + delta_x + 1] = (y_avg[idx + lag + delta_x] * lag + ys[idx + lag] - ys[idx])/lag
    idx += 1

hits, peaks, ys_avg = al.mark_greater_than_baseline(xs, ys, lag=lag, delta_x=delta_x, min_amp=0.3, direction=-1)

plt.plot(xs, ys)
plt.plot(xs, y_avg)
plt.plot(xs, ys_avg, color = 'purple')

y_avg_min_amp = [i - 0.3 for i in y_avg]
plt.plot(xs, y_avg_min_amp)

scatter_x = [x for i, x in enumerate(xs) if hits[i] == 1]
scatter_y = [y for i, y in enumerate(ys) if hits[i] == 1]

plt.scatter(scatter_x, scatter_y, c='yellow')

peaks_x = [xs[i] for i in peaks]
peaks_y = [ys[i] for i in peaks]
plt.scatter(peaks_x, peaks_y, c='red')
# plt.scatter(baseline_x, baseline_y, c='red', marker='x')
plt.xlim((40.15, 40.19))
plt.show()
