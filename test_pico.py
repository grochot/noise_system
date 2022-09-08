from hardware.picoscope4626 import PicoScope
period_time = 1 
sampling_interval = 0.01
no_samples = int(period_time/((sampling_interval)))
if no_samples % 2 == 1:
    no_samples = no_samples + 1

oscilloscope = PicoScope()
oscilloscope.setChannelA("DC", "1V" )
oscilloscope.setTrigger()

oscilloscope.set_number_samples(no_samples)
oscilloscope.set_timebase(int(sampling_interval*10000000)-1)
oscilloscope.run_block_capture()
oscilloscope.check_data_collection()
oscilloscope.create_buffers()
oscilloscope.set_buffer_location()
oscilloscope.getValuesfromScope()
tmp_time_list = oscilloscope.create_time()
tmp_voltage_list = oscilloscope.convert_to_mV("1V")


print(tmp_time_list, tmp_voltage_list)
# import pyvisa 
# from time import sleep
# from pyvisa.constants import StopBits, Parity
# from pyvisa import constants
# rm = pyvisa.ResourceManager("@py") 
# print(rm.list_resources()) 
# inst = rm.open_resource('ASRL/dev/ttyS0::INSTR',baud_rate=9600, data_bits=8, flow_control=constants.VI_ASRL_FLOW_RTS_CTS, parity = Parity.none, stop_bits=StopBits.one)  

# #inst = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
# inst.timeout = 25000

# # # sleep(2)
# inst.write('*IDN?')
# # inst.write('*RST')
# sleep(2)
# #inst.write('VOLT 4')
# # sleep(2)
# # inst.write('OPON 1')
# # sleep(2)
# # inst.write("VOLT?")
# # sleep(2)
# print(inst.read())
# # sleep(2)
# # #print(inst.read())

# # print(inst.query('*IDN?'))
# # inst.close()
