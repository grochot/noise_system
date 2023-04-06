class GenerateHeader(): 
    
    
    def set_parameters(self, filename, columns, a,b,c,d,e,f,g,h,i,j,k,l,m):
        self.PROCEDURE = '#Procedure: <__main__.NoiseProcedure>'
        self.DATA = "#Data:"
        self.PARAMETERS = """#Parameters:
#	Bias Field Voltage: {0} V
#	Bias Voltage: {1} V
#	Channel A Coupling Type: {2}
#	Channel A Range: {3} 
#	Divide number: {4} mV
#	HMC8043 adress: {5}
#	Field_sensor: {6}
#	Mode: Mean + Raw
#	Number of times: {7}
#	Period of Time: {8} s
#	Sample Name: {9}
#	Sampling frequency: {10} Hz
#	Treshold: {11} mV
#	SIM928 adress: {12}""".format(a,b,c,d,e,f,g,h,i,j,k,l,m)

        f = open('{}'.format(filename), 'w')

        f.write(self.PROCEDURE + '\n')
        f.write(self.PARAMETERS + '\n')
        f.write(self.DATA + '\n')
        f.writelines(columns)
        f.write('\n')
        f.close()

    def write_data(self, filename2, data):
        f = open('{}'.format(filename2), 'a')
        f.writelines(data)
        f.write('\n')
        f.close()


