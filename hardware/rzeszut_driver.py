

# from pymeasure.instruments import Instrument
# from time import sleep, time
# from pymeasure.instruments.validators import truncated_range, strict_discrete_set
# import serial
# import numpy as np
# import re


# import logging
# log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler())


# class RzeszutField(Instrument):

#     def __init__(self, resourceName):
#         self.resource = resourceName
#         self.address = self.resource
#         self.serial_port = serial.Serial(self.address, 115200, timeout=1)

#     def version(self):
#         self.serial_port.write(b"V?")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text

#     def get_field(self):
#         self.serial_port.write(b"FCC")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text

#     def get_field_xy(self):
#         self.serial_port.write(b"FXY")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_field_xz(self):
#         self.serial_port.write(b"FXZ")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_field_yz(self):
#         self.serial_port.write(b"FYZ")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_field_all(self):
#         self.serial_port.write(b"FTT")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_angle_yz(self):
#         self.serial_port.write(b"FPX")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_angle_xz(self):
#         self.serial_port.write(b"FPY")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_angle_xy(self):
#         self.serial_port.write(b"FPZ")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_sample_number(self): 
#         self.serial_port.write(b"AV?")
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def set_sample_number(self, number=int): 
#         message = "AVS;"+str(number)
#         self.serial_port.write(message.encode())
       
#     def set_voltage(self, channel = int, voltage = float): 
#         message = "WV;"+str(channel)+";"+str(voltage)
#         self.serial_port.write(message.encode())    


#     def set_pid(self, channel = int, p = float, i = float, d = float, mean = int, step = float, i_max = float, rezerwa = float, preskaler = int): 
#         message = "PID;"+str(channel)+";"+str(p)+";"+str(d)+";"+str(i)+";"+str(mean)+";"+str(step)+";"+str(i_max)+";"+str(rezerwa)+";"+str(preskaler)
#         self.serial_port.write(message.encode())
    

#     def get_pid(self, channel = int): 
        
#         message = "WPG;"+str(channel) 
#         self.serial_port.write(message.encode())
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text
    
#     def get_pid_status(self, channel = int): 
        
#         message = "WPC;"+str(channel) 
#         self.serial_port.write(message.encode())
#         sleep(0.3)
#         text = ""
#         text += str(self.serial_port.readline())
#         self.serial_port.read()
#         return text

#     def set_pid_on(self, channel = int): 
#         message = "WPS;"+str(channel)
#         self.serial_port.write(message.encode())

#     def set_pid_off(self, channel = int): 
#         message = "WPL;"+str(channel)
#         self.serial_port.write(message.encode())
    
#     def sef_pid_value(self, channel = int, value = float): 
#         message = "WPV;"+str(channel)+";"+str(value)
#         self.serial_port.write(message.encode())
    
    
    
    
#     # def read_field(self): 
#     #     self.address = self.resource
#     #     serial_port = serial.Serial(self.address, 115200, timeout=1)
#     #     serial_port.write(b"READ_SINGLE")
#     #     sleep(0.5)
#     #     text = ""
#     #     text += str(serial_port.readline())
#     #     serial_port.read()
#     #     text = text.replace("b'", "")
#     #     text = text.replace("'", "")
#     #     pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
#     #     result = re.match(pattern, text)
#     #     #print(np.sqrt(float(result["x"])**2+float(result["y"])**2+float(result["z"])**2))
#     #     return float(result["x"]) ,float(result["y"]) ,float(result["z"])

#     # def read_field_init(self):
#     #     self.address = self.resource
#     #     serial_port = serial.Serial(self.address, 115200, timeout=1)
#     #     serial_port.write(b"READ_SINGLE")
#     #     sleep(0.5)
#     #     text = ""
#     #     text += str(serial_port.readline())
#     #     serial_port.read()
#     #     text = text.replace("b'", "")
#     #     text = text.replace("'", "")
#     #     pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
#     #     result = re.match(pattern, text)
#     #     print(np.sqrt(float(result["x"])**2+float(result["y"])**2+float(result["z"])**2))
#     #     return float(result["x"]) ,float(result["y"]) ,float(result["z"])
############################################
# This is for CRC-8 Maxim/Dallas Algorithm
# Improved with less variable and functions
# Supports both Python3.x and Python2.x
# Has append and check functions
# When standalone, can read from either arguments or stdin
# Writes to stdout cleaner
# http://gist.github.com/eaydin
############################################

def crc8calc(incoming):
    msg = bytearray(incoming.encode(encoding="ascii"))
    check = 0
    for i in msg:
        check = AddToCRC(i, check)

    crc8_ready =  '{:03d}'.format(check).encode('ascii')
    return crc8_ready

def AddToCRC(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b^crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C # this means crc ^= 140
    return crc



# if __name__ == "__main__":
    
#     test = RzeszutField('COM6')

#     print(test.version())

#     # test.read_field()
#     # test.read_field()
#     # test.read_field()
#     # test.read_field()
#     # test.read_field()


import serial
import time
import sys



# Konfiguracja portu UART
ser = serial.Serial(
    port='COM3',    # Zmień na odpowiedni port COM na swoim systemie
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Funkcja do wysyłania danych z sumą kontrolną
def send_data(data):
    # Konwersja danych do ASCII
    data_ascii = data.encode('ascii')

    # Obliczanie CRC8
    crc8 = crc8calc(data)

    # Tworzenie ramki danych
    frame = data_ascii  + crc8 + b'\r\n'
    
    # Wysłanie danych

    ser.write(frame)

# Funkcja do odbierania danych
def receive_data():
            # Odbieranie danych do znaku nowej linii
            data = ser.readline().decode()
            
            # # Parsowanie danych
            # if data:
                
            #         frame_data, crc_str = data.rsplit(';', 1)
            #         received_crc = int(crc_str[:3])

            #         # Sprawdzenie CRC8
            #         # calculated_crc = calculate_crc8(frame_data.encode('ascii'))
            #         # if received_crc == calculated_crc:
            #         print(f'Odebrano poprawne dane: {frame_data}')
                #     else:
                #         print('Błąd sumy kontrolnej')
                # except ValueError:
                #     print('Nieprawidłowy format danych')
            return data

# Przykład użycia
if __name__ == "__main__":
    # Wysyłanie przykładowych danych
    send_data("V?;")


    # Odbieranie danych
   
    receive_data()
    ser.close()