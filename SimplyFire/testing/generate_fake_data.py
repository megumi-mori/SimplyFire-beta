import numpy as np
import random
import pyabf
import matplotlib.pyplot as plt

def generate_plot(total_time=5,
				  sampling_rate=10000,
				  amp=0.7,
				  amp_variability=0, #%
				  rise_t=0.003,
				  rise_variability=0, #%
				  decay_t=0.005,
				  decay_variability=0, #%
				  mean_interval=1000,
				  noise_amp=0.05,
				  noise_freq=10,
				  plot=False,
				  save=True,
				  filename=None):
	points = total_time*sampling_rate
	ideal_data = np.zeros(points)
	noise = np.zeros(points)

	max_mini_len = ((rise_variability+1)*rise_t + (decay_variability+1)*decay_t*10)*sampling_rate
	pos = int(random.gammavariate(3, mean_interval / 3))
	##pos = int(random.expovariate(1/mean_interval))
	while pos < points - max_mini_len:
		rise = (random.random()*rise_variability+1)*rise_t
		decay = (random.random()*decay_variability+1)*decay_t
		amp = random.random()*amp_variability*amp+amp

		mini_x=np.arange(0, (rise+decay*10), 1/sampling_rate)
		#linear rise, exponential decay
		# mini_y = np.zeros(len(mini_x))
		# mini_y[0:int(rise*sampling_rate)] = [amp/rise*x for x in mini_x[0:int(rise*sampling_rate)]] #linear
		# mini_y[int(rise*sampling_rate):] = [amp*(np.exp(-(x-rise)/decay)) for x in mini_x[int(rise*sampling_rate):]]

		#exponential
		mini_y = np.array([amp * (1 - np.exp(-t / rise)) * np.exp(-t / decay) for t in mini_x])

		#calculate theoretical
		max_idx = np.where(mini_y == max(mini_y))[0][0]
		amp_actual = mini_y[max_idx]
		rise_actual = mini_x[max_idx]
		halfwidth_actual = np.where(mini_y>0.5*amp_actual)
		halfwidth_actual = mini_x[halfwidth_actual[0][-1]]-mini_x[halfwidth_actual[0][0]]
		decay_actual = mini_x[np.where(mini_y>np.exp(-1)*amp_actual)[0][-1]]-mini_x[max_idx]

		print(f'amp: {amp_actual}, rise: {rise_actual}, hw: {halfwidth_actual}, decay:{decay_actual}')

		ideal_data[pos:pos + len(mini_y)] += mini_y
		pos += int(random.gammavariate(3, mean_interval / 3))

	xvals = np.arange(0, total_time, 1/sampling_rate)
	## Correlation length, relevant for correlated noise only
	i=0
	noise_len=0
	while i < points:
		if noise_len == 0:
			noise_len = int(random.random()*noise_freq)
			noise[i] = random.gauss(0,noise_amp)
		else:
			noise[i] = noise[i-1]
			noise_len -= 1
		i+= 1
	yvals = ideal_data+noise
	if plot:
		plt.plot(xvals, yvals)
		plt.show()

	if save and filename:
		yvals = np.reshape(yvals, (1, points))
		pyabf.abfWriter.writeABF1(yvals, filename, sampling_rate, units='nA')
	pass
# num_traces = 1
# total_time = 5
# freq = 10000
# rise_tau = 5
# decay_tau = 50
# mini_amp = 15
# mean_interval = 1000
# noise_amp = 0.05
#
# points = total_time*freq + 1
# mini_len = 10*decay_tau
#
# xvals = np.linspace(0,total_time,points)
# ideal_data = np.zeros(points)
# noise = np.zeros(points)
#
# mini = np.array([mini_amp*(1 - np.exp(-t/rise_tau))*np.exp(-t/decay_tau) for t in range(mini_len)])
#
# pos = int(random.gammavariate(3,mean_interval/3))
# ##pos = int(random.expovariate(1/mean_interval))
# while pos < points - mini_len:
# 	ideal_data[pos:pos+mini_len] += mini
# 	pos += int(random.gammavariate(3,mean_interval/3))
# 	##pos += int(random.expovariate(1/mean_interval))
#
# noise_val = 0
# ## Correlation length, relevant for correlated noise only
# noise_len = 10
# for i in range(points):
# 	## Uncorrelated noise
# 	noise[i] = random.gauss(0,noise_amp)
# 	## Random walk noise
# 	##noise_val = noise[i] = noise_val + noise_amp*random.gauss(0,1)
# 	## Correlated noise
# 	##noise[i:min(i+noise_len,points)] += random.gauss(0,noise_amp/np.sqrt(noise_len))
#
# yvals = ideal_data + noise
#
# plt.plot(xvals,yvals)
# plt.show()
