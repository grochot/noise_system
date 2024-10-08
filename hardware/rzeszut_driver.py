


from time import sleep, time
import numpy as np
import re
import serial
import time
import sys


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RzeszutField():

    def __init__(self, resourceName):
        self.resource = resourceName
        self.serial_port= serial.Serial(
            port=self.resource,    # Zmień na odpowiedni port COM na swoim systemie
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

    def version(self):
        self.write("V?;")
        text = self.read()
        return text

    def get_field(self):
        self.write("FCC?;")
        sleep(0.3)
        text = self.read()
        result = text.split(';')
        return result
       

    def get_field_xy(self):
        self.write("FXY?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_field_xz(self):
        self.write("FXZ?;")
        text = self.read()
        result = text.split(';')
        return result
        
    
    def get_field_yz(self):
        self.write("FYZ?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_field_all(self):
        self.write("FTT?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_angle_yz(self):
        self.write("FPX?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_angle_xz(self):
        self.write("FPY?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_angle_xy(self):
        self.write("FPZ?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def get_sample_number(self): 
        self.write("AV?;")
        text = self.read()
        result = text.split(';')
        return result
    
    def set_sample_number(self, number=str): 
        message = "AVS;"+ number +";"
        self.write(message)
       
    def set_voltage(self, channel = int, voltage = float): 
        message = "WV;"+str(channel)+";"+str(voltage) + ";" 
        self.write(message)    


    def set_pid(self, channel = int, p = float, i = float, d = float, mean = int, step = float, i_max = float, rezerwa = float, preskaler = int): 
        message = "PID;"+str(channel)+";"+str(p)+";"+str(d)+";"+str(i)+";"+str(mean)+";"+str(step)+";"+str(i_max)+";"+str(rezerwa)+";"+str(preskaler)+";"
        self.write(message)
    

    def get_pid(self, channel = int): 
        message = "WPG;"+str(channel)+";"
        self.write(message)
        text = self.read()
        result = text.split(';')
        return result
    
    def get_pid_status(self, channel = int): 
        
        message = "WPC;"+str(channel)+";"
        self.write(message)
        text = self.read()
        result = text.split(';')
        return result

    def set_pid_on(self, channel = int): 
        message = "WPS;"+str(channel)+";"
        self.write(message)

    def set_pid_off(self, channel = int): 
        message = "WPL;"+str(channel)+';'
        self.write(message)
    
    def set_pid_value(self, channel = int, value = float): 
        message = "WPV;"+str(channel)+";"+str(value)+";"
        self.write(message)
    
    #funkcje koncowe:
    
    def set_field_value(self, angleXY=0, value=0): 
        self.set_pid_on(1)
        self.set_pid_on(2)
        radian = np.radians(angleXY)
        v_x = value * np.cos(radian)
        v_y = value * np.sin(radian)
        self.set_pid_value(1,v_x)
        sleep(0.3)
        self.set_pid_value(2,v_y)
    
    def shutdown(self): 
        self.set_pid_off(1)
        self.set_pid_off(2)
        self.set_voltage(1,0)
        self.set_voltage(2,0)

        self.serial_port.close()
    




    
    # Funkcje pomocnicze:
    def crc8calc(self, incoming):
        msg = bytearray(incoming.encode(encoding="ascii"))
        check = 0
        for i in msg:
            check = self.AddToCRC(i, check)

        crc8_ready =  '{:03d}'.format(check).encode('ascii')
        return crc8_ready

    def AddToCRC(self,b, crc):
        if (b < 0):
            b += 256
        for i in range(8):
            odd = ((b^crc) & 1) == 1
            crc >>= 1
            b >>= 1
            if (odd):
                crc ^= 0x8C # this means crc ^= 140
        return crc
    # Funkcja do wysyłania danych z sumą kontrolną
    def write(self,data):
        # Konwersja danych do ASCII
        data_ascii = data.encode('ascii')

        # Obliczanie CRC8
        crc8 = self.crc8calc(data)

        # Tworzenie ramki danych
        frame = data_ascii  + crc8 + b'\r\n'
        print(frame)
        
        # Wysłanie danych

        self.serial_port.write(frame)


    def read(self):
        # Odbieranie danych do znaku nowej linii
        data = self.serial_port.read(100).decode()
      
        
        # Parsowanie danych
        if data:
            frame_data, crc_str = data.rsplit(';', 1)
         
            return str(frame_data)


if __name__ == '__main__':
    rzeszut = RzeszutField("COM6")
    #print(rzeszut.version())
    #print(rzeszut.get_field())
    #print(rzeszut.get_field())
    #print(rzeszut.get_field_xy())
    #print(rzeszut.get_field_xz())
    # print(rzeszut.get_field_yz())
    #print(rzeszut.get_field_all())
    # print(rzeszut.get_angle_yz())
    # print(rzeszut.get_angle_xz())
    #print(rzeszut.get_angle_xy())
    #print(rzeszut.get_sample_number())
    #print(rzeszut.set_sample_number('001'))
    print(rzeszut.set_voltage(1, 0))
    # print(rzeszut.set_pid(1, 1, 1, 1, 1, 1, 1, 1, 1))
    #print(rzeszut.get_pid(2))
    #print(rzeszut.get_pid_status(1))
    #print(rzeszut.set_pid_on(1))
    print(rzeszut.set_pid_off(1))
    #print(rzeszut.set_pid_value(1, 0))
    # print(rzeszut.crc8calc("FCC"))











