import numpy as np
class ComputeDiff:
    def __init__(self):
        pass

    def diffs(self, x,y):
        dy = np.diff(y)
        dx = np.diff(x)
        res = [i / j for i, j in zip(dy, dx)]
        return res
    
    def diffIV(self,x):
        
        dif = np.diff(x)
        return dif
    
    def SlopeDiff(self,x,y): 
        res = []
        for i in range(1,len(x-1)):
            res.append((y[i+1]-y[i-1])/x[i+1]-x[i-1])
        return res

    def NormalizedDiff(self, x): 
        max_l = max(x)
        min_l = min(x)
        res = []
        for i in range(1,len(x-1)):
            res.append(x[i-1]-x[i+1]/(max_l-min_l))
        return res
    
    def HdIS(self,x,R):
        res =[]
        for i in range(len(x)): 
            res.append(x[i]*R[i])
        return res




        


