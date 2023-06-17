import numpy as np
class ComputeDiff:
    def __init__(self):
        pass

    def diff(self, y, x):
        return np.diff(y) / np.diff(x)
    
    def diffIV(self,y):
        dif = []
        length = len(y)
        for i in range(1,length-1):
            dif.append(y[i+1]-y[i-1])
        return dif
        


