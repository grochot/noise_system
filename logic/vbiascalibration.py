import numpy as np 
from scipy.optimize import curve_fit

def func(x, a, b, c):
    return (1/(a*x+b))+c

def vbiascalibration(vbias_list, vs_list):
    popt, pcov = curve_fit(func, vbias_list, vs_list)
    return popt

def calculationbias(vin, parameters):
    return (1/(parameters[0]*(vin-parameters[2])))-(parameters[1]/parameters[0])

