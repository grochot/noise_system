import numpy as np 
from scipy.optimize import curve_fit

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def vbiascalibration(vbias_list, vs_list):
    popt, pcov = curve_fit(func, vbias_list, vs_list)
    return popt

def calculationbias(v_in, parameters):
    return func(v_in, *parameters)


