# import numpy as np
# import numpy.fft as fft
# import matplotlib.pyplot as plt

# import numpy as np
# import matplotlib.pyplot as plt

# start_tm, end_tm = 0, 2
# signal1 = 12  # frequency of the wave
# smpl_freq = 32 * signal1  # sampling frequency with oversampling factor=32
# smpl_intv = 1 / smpl_freq  # intervals time points are sampled
# tm = np.arange(start_tm, end_tm, smpl_intv)
# ampl1 = 1*np.sin(2 * np.pi * signal1 * tm)  # generate sine wave

# fig, axes = plt.subplots(2, 1, figsize=(14, 6))
# plt.subplots_adjust(hspace=.5)
# axes[0].set_title(f'Wave with a frequency of {signal1} Hz')
# axes[0].plot(tm, ampl1)
# axes[0].set_xlabel('Time')
# axes[0].set_ylabel('Amplitude')
# ft_ = np.fft.fft(ampl1) / len(ampl1)  # Normalize amplitude and apply the FFT
# ft_ = ft_[range(int(len(ampl1)/2))]   # Exclude sampling frequency
# tp_cnt = len(ampl1)
# val_ = np.arange(int(tp_cnt / 2))
# tm_period_ = tp_cnt / smpl_freq
# freq_ = val_ / tm_period_
# axes[1].set_title('Fourier transform depicting the frequency components')
# axes[1].plot(freq_, abs(ft_))
# axes[1].set_xlabel('Frequency')
# axes[1].set_ylabel('Amplitude')
# #annot_max(freq_, abs(ft_), ax=axes[1])
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt

# t0 = 0
# t1 = 1
# n_samples = 10000

# xs = np.linspace(t0, t1, n_samples)
# ys = 7 * np.sin(15 * 2 * np.pi * xs) 

# plt.subplot(2, 1, 1)
# plt.plot(xs, ys)

# np_fft = np.fft.fft(ys)
# amplitudes = 2 / n_samples * np.abs(np_fft) 
# frequencies = np.fft.fftfreq(n_samples) * n_samples * 1 / (t1 - t0)

# plt.subplot(2, 1, 2)
# plt.semilogx(frequencies[:len(frequencies) // 2], amplitudes[:len(np_fft) // 2])

# plt.show()