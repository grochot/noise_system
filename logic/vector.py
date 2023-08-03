import numpy as np
class Vector():
	def __init__(self, vec):
		self.vec = vec 

	def generate_vector(self):
		ranges = self.vec.split(',')
		numbers = []
		start = int(ranges[0])
		step = int(ranges[1])
		stop = int(ranges[2])
		numbers = list(np.arange(start, stop, step))
		w = 1
		if len(ranges) > 3:
			for i in range(2, len(ranges)-2,2):
				start = int(ranges[i])
				step = int(ranges[i + 1])
				stop = int(ranges[i + 2])
				if w < len(range(2, len(ranges)-2,2)) :
					numbers= numbers + list(np.arange(start, stop, step))
				else:
					numbers= numbers + list(np.arange(start, stop+step, step))
				w = w + 1
		return numbers



