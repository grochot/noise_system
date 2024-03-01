import numpy as np
class Vector():
	def __init__(self):
		pass

	def generate_vector(self, vec):
		ranges = vec.split(',')
		numbers = []
		if len(ranges) == 3:
			start = float(ranges[0])
			stop = float(ranges[2])
			step = float(ranges[1]) if start < stop else -1*float(ranges[1])
			numbers = list(np.arange(start, stop+step, step))
		w = 1
		if len(ranges) > 3:
			start = float(ranges[0])
			stop = float(ranges[2])
			step = float(ranges[1]) if start < stop else -1*float(ranges[1])
			numbers = list(np.arange(start, stop, step))
			for i in range(2, len(ranges)-2,2):
				start = float(ranges[i])
				stop = float(ranges[i + 2])
				step = float(ranges[i+1]) if start < stop else -1*float(ranges[i+1])

				if w < len(range(2, len(ranges)-2,2)) :
					numbers= numbers + list(np.arange(start, stop, step))
				else:
					numbers= numbers + list(np.arange(start, stop+step, step))
				w = w + 1
		return numbers


# test = Vector()

# vector = "2,1,10,3,1,2,20,3,1"

# print(test.generate_vector(vector))