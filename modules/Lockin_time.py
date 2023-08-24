import sys
sys.path.append('..')

from hardware.zurich import Zurich

from time import sleep
import numpy as np
class LockinTime():
    def __init__(self, server=""):
        self.lockin = Zurich(server)

    def init(self, av:int = 1, input_sel: int = 1, rate: float = 0, length:float = 16348 ):
        self.lockin.scope_init(av, input_sel, rate, length)
        


   
    def get_wave(self):
        value = self.lockin.get_wave()
        time = self.lockin.to_timestamp(value)

        return time, value[0][0]['wave'][0]


# ########################### Test ###########################3
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# loc = LockinTime('192.168.66.202')

# loc.init(1,1,0,16348)

# data = loc.get_wave()

# import matplotlib.pyplot as plt
# plt.plot(data[0], data[1])
# plt.show()