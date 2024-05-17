import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from data_process import data_process
from collect_data import collect_data

class ArduinoController: 
    def __init__(self, port_list):
        self.connected_device_list = []
        for port in port_list:
            self.connected_device_list.append(serial.Serial(port=port, baudrate=115200, timeout=2))

    def write_data(self, arduino, command) : arduino.write(bytes(command, 'utf-8'))
        
    def read_data(self, arduino) : return arduino.readline().decode('utf-8')

    def close_connections(self): 
        for arduino in self.connected_device_list:
            arduino.close()


def setup_serial_ports():
    import serial.tools.list_ports as sp
    ports = sp.comports()
    lst = [str(single_port).split('-')[0].strip() for single_port in ports]
    print(lst)
    return lst


def read_user_input(prompt, valid_options):
    while True:
        try:
            user_input = int(input(prompt))
            if user_input not in valid_options:
                raise ValueError
            return user_input
        except ValueError:
            print('Invalid input! Please try again.')


def main():
    pc_name = os.getcwd().split('\\')[2].upper() + "_PC"
    print(pc_name)

    print("**Note: Use all devices of only one wavelength at a time")
    print("**Note: Fully charge the devices to run L5")
    print("**Note: Count all active ports in device manager, which should be equal to the number of devices connected.")
    print("**Note: Make sure that Bluetooth in the PC/Laptop is turned off")

    time_dur = 1
    repeats = 2
    delay = 10
    level_list = [1]

    valid_wavelengths = [1, 2, 3]
    wv_type = read_user_input("Enter 1 for dual device, 2 for 367 device, 3 for 405 device : ", valid_wavelengths)

    if wv_type == 1:
        wavelength_list = [528, 620]
    elif wv_type == 2:
        wavelength_list = [367]
    else:
        wavelength_list = [405]

    port_list = setup_serial_ports()
    connected_device_info = ArduinoController(port_list)
    output_dir = "data"
    try:
        loop = 1
        for wavelength in wavelength_list:
            for level in level_list:
                print(f'loop no {loop}----------------------------------------')
                loop+=1
                collect_data(connected_device_info, wavelength, level, repeats, time_dur, pc_name)
                
                time.sleep(delay)
    finally:
        connected_device_info.close_connections()
        print("Files can be found in this location: ", output_dir)


if __name__ == "__main__":
    main()
