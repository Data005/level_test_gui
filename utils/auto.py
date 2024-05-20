import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from tkinter import *
from tkinter import ttk
from data_process import data_process
from collect_data import collect_data
from gui import *
from calibration import *


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

    port_list = setup_serial_ports()
    connected_device_info = ArduinoController(port_list)


    root = Tk()
    root.title("Device Stability Testing")
    root.geometry("810x490")


    f1 = Frame(root, bg="gray", width=500, height=490)
    f1.pack(side=RIGHT, fill=Y)
        
    text_box = Text(root, bg="black", fg="white", height=200, state=DISABLED)
    text_box.pack(expand=True, fill="x", padx=10, pady=10)
    
    button_list = get_device_and_port_id(connected_device_info)
    level_options = ['1', '5']
    wavelength_options = ['528', '620', '367']
    duration_options = ['1', '5', '15']


    device_config = create_buttons_with_dropdowns(f1, button_list, level_options, wavelength_options, duration_options, text_box, root)
    # calibration(connected_device_info, root)

    root.mainloop()
    

    output_dir = "data"
    collect_data(connected_device_info, device_config, pc_name, text_box)
                

    connected_device_info.close_connections()
    print("Files can be found in this location: ", output_dir)



if __name__ == "__main__":
    main()
