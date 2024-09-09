import numpy as np
class Vector():
	def __init__(self):
		pass

	def generate_vector(self, vec, Hr = 0.0):
		ranges = vec.split(',')
		if 'Hr' in ranges:
			numbers = []
			if len(ranges) == 3:
				start = float(ranges[0])
				stop = Hr
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
					stop = float(ranges[i + 2]) if ranges[i+2] != 'Hr' else Hr
					step = float(ranges[i+1]) if start < stop else -1*float(ranges[i+1])

					if w < len(range(2, len(ranges)-2,2)) :
						numbers= numbers + list(np.arange(start, stop, step))
					else:
						numbers= numbers + list(np.arange(start, Hr, step))
					w = w + 1
			return numbers



		else:
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


if __name__ == "__main__":
	test = Vector()

	vector = "0,1,10,2,Hr"

	print(list(test.generate_vector(vector, 0)))