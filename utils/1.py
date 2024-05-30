import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from utils.gui import *
from utils.data_process import data_process
import json

def collect_data(connected_device_info, device_config, user_id, text_box):
    all_data = {}
    error_cases = {}
    repeats = 1
    print(json.dumps(device_config, indent=4))

    for i in range(3):
        for j in range(2):
            for run in range(repeats):
                Device_test_count = 0

                port_list = []
                arduino_list = []
                discontinued = []

                Version = {}
                DAC = {}
                Current = {}
                Adj_Int = {}
                Device_id = {}

                # Device calibration loop
                for idx, arduino in enumerate(connected_device_info.connected_device_list):
                    quick_check_flag = 0
                    port = arduino.port

                    Device_test_count += 1

                    device_id = next((key for key in device_config.keys() if key.split('-')[1] == port), None)

                    if device_id is not None:
                        if device_config[device_id]:
                            if run == 4 :
                                text = device_config[device_id].pop(0)
                            else : 
                                text = device_config[device_id][0]
                            wavelength = text.split("_")[0]
                            level = text.split("_")[1]
                        else:
                            print_to_text_box('Done for the Day', text_box)
                            break
                        duration = '1'
                    else:
                        print(f"No device configuration found for port {port}. Skipping...")
                        continue

                    line = ""

                    while True:
                        try:
                            line = connected_device_info.read_data(arduino)
                        except serial.SerialException as e:
                            print(f"Error reading data from {device_id} ------ {port}")
                            print_to_text_box(f"Error reading data from {device_id} ------ {port}", text_box)
                            quick_check_flag = 1
                            break

                        print(f"{port} : {run + 1} :: {line}")

                        command = ''

                        if line == "":
                            connected_device_info.write_data(arduino, "r")

                        elif 'Version' in line:
                            Version[port] = line.split(' : ')[1].strip()

                        elif 'Device ID.' in line:
                            Device_id[port] = line.split(' : ')[1].strip()

                        elif 'Adjusted Intensity' in line:
                            Adj_Int[port] = int(line.split(' : ')[1].strip())

                        elif 'Current drawn' in line:
                            Current[port] = float(line.split(' : ')[1].split(' ')[0].strip())

                        elif 'Adjusted DAC Value' in line:
                            DAC[port] = int(line.split(' : ')[1].strip())

                        elif 'Mobile ID' in line:
                            command = user_id

                        elif 'level' in line:
                            command = level

                        elif 'Wavelength' in line:
                            command = wavelength

                        elif 'Duration' in line:
                            command = duration

                        elif 'Press Enter' in line:
                            connected_device_info.write_data(arduino, "r")
                            break

                        elif 'DAC has saturated ' in line or 'Fault' in line or 'Runaway' in line or 'Done' in line or 'Charge the device' in line:
                            connected_device_info.write_data(arduino, '%')
                            quick_check_flag = 1
                            print_to_text_box(f'{device_id} Failed During Calibration :: {line} :: {wavelength} :: {level}', text_box)
                            all_device_single_run_Intensity_data = {f'{Device_id[port]}_{wavelength}_{level}_{run + 1}': []}
                            all_device_single_run_current_data = {f'{Device_id[port]}_{wavelength}_{level}_{run + 1}': []}
                            
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Version[port])
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(wavelength)
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append("N/A")
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append('N/A')
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append('N/A')
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(line)

                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Version[port])
                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(wavelength)
                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append('N/A')
                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append('N/A')
                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append('N/A')
                            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(line)
                            print(all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'])
                            print(all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'])
                            break

                        else:
                            continue
                        connected_device_info.write_data(arduino, command)

                    if not quick_check_flag:
                        port_list.append(port)
                        arduino_list.append(arduino)
                    else:
                        if port in Device_id:
                            discontinued.append(Device_id[port])

                all_device_single_run_Intensity_data = {f'{Device_id[port]}_{wavelength}_{level}_{run + 1}': [] for port in port_list}
                all_device_single_run_current_data = {f'{Device_id[port]}_{wavelength}_{level}_{run + 1}': [] for port in port_list}

                # Calibration data append here
                for port in port_list:
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Version[port])
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(wavelength)
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(DAC[port])
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Current[port])
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Adj_Int[port])

                    all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Version[port])
                    all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(wavelength)
                    all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(DAC[port])
                    all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Current[port])
                    all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(Adj_Int[port])

                # Data generation here
                while arduino_list:
                    for arduino, port in zip(arduino_list, port_list):
                        try:
                            value = connected_device_info.read_data(arduino).split(' ')[0]
                        except serial.SerialException as e:
                            print(f"Error reading data from {device_id} ------ {port}")
                            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append("Connection Loss")
                            arduino_list.remove(arduino)
                            port_list.remove(port)
                            continue
                        
                        if '...' in value:
                            continue
                        
                        all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(value.split(',')[0])
                        all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'].append(value)
                        print(f"{port} : {run + 1} :: {value}")

                        if 'DAC' in value or 'Fault' in value or 'Runaway' in value or 'Done' in value:
                            if 'Done' in value:
                                all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'][-1] = user_id
                                all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_{level}_{run + 1}'][-1] = user_id
                            print_to_text_box(f'{device_id} Failed During Data Generation :: {value} :: {wavelength} :: {level}', text_box)
                            connected_device_info.write_data(arduino, '%')
                            arduino_list.remove(arduino)
                            port_list.remove(port)

                # Data processing
                flattened_intensity_data = [list(value) for value in all_device_single_run_Intensity_data.values()]
                print(flattened_intensity_data)
                flattened_current_data = [list(value) for value in all_device_single_run_current_data.values()]

                if flattened_intensity_data:
                    max_row_length = max(len(data) for data in flattened_intensity_data)
                else:
                    print("Error: No data available for processing.")
                    continue

                for data in flattened_current_data:
                    data.extend([0] * (max_row_length - len(data)))

                columns = list(all_device_single_run_Intensity_data.keys())
                num_columns = len(columns)
                num_rows = max_row_length

                df = pd.DataFrame(flattened_intensity_data).T
                cdf = pd.DataFrame(flattened_current_data).T

                df.columns = columns
                cdf.columns = columns

                final = data_process(df)
                final.to_csv('data/main.csv', index=False)
