import numpy as np 
from scipy.optimize import curve_fit

def func(x, a, b, c):
    return (1/(a*x+b))+c

def vbiascalibration(vbias_list, vs_list):
    popt, pcov = curve_fit(func, vbias_list, vs_list)
    return popt

def calculationbias(vin, a,b,c):
    return (1-float(vin)*b+c*b)/(float(vin)*a-c*a)

# wynik = calculationbias(0.1, -1439.5638741955333, 235.0248602114991, 246.80517253562815)
# print(wynik)