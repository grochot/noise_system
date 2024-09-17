# import nidaqmx
# with nidaqmx.Task() as task:
# 	task.ai_channels.add_ai_voltage_chan("6124/ai1")
# 	print(task.read())

import numpy as np 


tt = list(np.linspace(22,23,4))
dd = list(np.linspace(22,2233,78))

tt.append(dd)
print(tt)


