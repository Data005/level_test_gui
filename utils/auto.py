import os
import serial
import serial.tools.list_ports as sp
from tkinter import *
from gui import create_buttons_with_checkboxes, print_to_text_box
from data_process import data_process
from collect_data import collect_data
from calibration import *
import json

class ArduinoController:
    def __init__(self, port_list):
        self.connected_device_list = [
            serial.Serial(port=port, baudrate=115200, timeout=2) for port in port_list
        ]

    def write_data(self, arduino, command):
        arduino.write(bytes(command, 'utf-8'))

    def read_data(self, arduino):
        return arduino.readline().decode('utf-8')

    def close_connections(self):
        for arduino in self.connected_device_list:
            arduino.close()

def setup_serial_ports():
    ports = sp.comports()
    port_list = [str(single_port).split('-')[0].strip() for single_port in ports]
    print(port_list)
    return port_list

def main():
    def update_text_box():
        text_box.config(state=NORMAL)
        text_box.delete(1.0, END)
        json_device_config = json.dumps(device_config, indent=4)
        text_box.insert(END, f"Device Config: {json_device_config}\n")
        text_box.config(state=DISABLED)

    def on_submit():
        for button in button_list:
            device_config[button][0] = [wl for wl in device_config[button][0] if wl not in rm_wavelength_list]
            device_config[button][1] = [level for level in device_config[button][1] if level not in rm_level_list]

        for button in button_list:
            for wavelength in device_config[button][0]:
                for level in device_config[button][1]:
                    device_config[button][2].append(f"{wavelength}_{level}")

        update_text_box()

    pc_name = os.getcwd().split('\\')[2].upper() + "_PC"
    print(pc_name)

    port_list = setup_serial_ports()
    connected_device_info = ArduinoController(port_list)

    root = Tk()
    root.title("Device Stability Testing")
    root.geometry("810x490")

    f1 = Frame(root, bg="gray", width=300, height=490)
    f1.pack(side=RIGHT, fill=BOTH, expand=True)

    text_box = Text(root, bg="black", fg="white", state=DISABLED)
    text_box.pack(anchor='nw', padx=10, pady=10, expand=True)

    button_list = get_device_and_port_id(connected_device_info)
    device_config = {button: [[], [], []] for button in button_list}

    for button in button_list:
        if "VB" in button:
            device_config[button] = [["528", "620"], ["L1", "L5"],[]]
        elif "DUO" in button:
            device_config[button] = [["528", "620", "367"], ["L1", "L5"],[]]

    update_text_box()

    rm_wavelength_list, rm_level_list = create_buttons_with_checkboxes(f1, device_config, text_box, button_list, update_text_box)

    submit_button = Button(root, text="Submit", command=on_submit)
    submit_button.pack(side=BOTTOM, padx=10, pady=5)

    def collect_data_wrapper():
        collect_data(connected_device_info, device_config, pc_name, text_box)

    def filter_and_save_excel_wrapper():
        filter_and_save_excel()  # Ensure this function is defined elsewhere

    collect_data_button = Button(root, text="Collect Data", command=collect_data_wrapper)
    collect_data_button.pack(side=BOTTOM, padx=10, pady=5)

    filter_excel_button = Button(root, text="Filter and Save Excel", command=filter_and_save_excel_wrapper)
    filter_excel_button.pack(side=BOTTOM, padx=10, pady=5)

    root.mainloop()

    connected_device_info.close_connections()

if __name__ == "__main__":
    main()
