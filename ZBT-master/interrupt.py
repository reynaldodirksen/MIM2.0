from libs.micronas import USBProgrammer
from time import sleep
import libs.databaseFunctions as databaseFunctions


micronas = USBProgrammer('/dev/ttyUSB0')


while(1):
    if micronas.read_id() != "0000 0000":
        Voltage0 = micronas.read_voltage_out()
        voltage_difference = 0
        biggest_pos_difference = 0
        biggest_neg_difference = 0
        sleep(1)
        factor = ""
        while micronas.read_id != "0000 0000":
            Voltage = micronas.read_voltage_out()
            voltage_difference = Voltage-Voltage0
            if voltage_difference >= 0:
                if voltage_difference > biggest_pos_difference:
                    biggest_pos_difference = voltage_difference
            elif voltage_difference < 0:
                if voltage_difference < biggest_neg_difference:
                    biggest__neg_difference = voltage_difference
            if abs(biggest_neg_difference) > biggest_pos_difference:
                print(biggest_neg_difference)
            else:
                print(biggest_pos_difference)
            
            
            
            
                
                
        
