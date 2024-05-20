import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from gui import *
from data_process import data_process

def collect_data(connected_device_info, device_config, user_id, text_box):
    all_data = {}
    error_cases = {}
    repeats = 5

    for run in range(repeats):
        loop_run = 0

        port_list = []
        arduino_list = []
        # discontinued = []

        Version = {}
        DAC = {}
        Current = {}
        Adj_Int = {}
        Device_id = {}

        for idx, arduino in enumerate(connected_device_info.connected_device_list):

            quick_check_flag = 0
            port = arduino.port

            loop_run += 1
            print(f'Loop run : {loop_run} :: port : {port}')

            device_id = next((key for key in device_config.keys() if key.split('_')[1] == port), None)

            # Add a check to ensure device_id is not None
            if device_id is not None:
                level = device_config[device_id][0]
                wavelength = device_config[device_id][1]
                duration = device_config[device_id][2]
                user_id = "shobhit"
            else:
                print(f"No device configuration found for port {port}. Skipping...")
                continue

            level = device_config[device_id][0]
            wavelength = device_config[device_id][1]
            duration = device_config[device_id][2]
            user_id = "shobhit"

            line = ""
            while True:
                try:
                    line = connected_device_info.read_data(arduino)
                except serial.SerialException as e:
                    print(f"Error reading data from {port}: {e}")
                    quick_check_flag = 1
                    break

                print(f"{port} : {run + 1} :: {line}")

                if line == "":
                    connected_device_info.write_data(arduino, "r")

                if 'Version' in line:
                    Version[port] = line.split(' : ')[1].strip()
                    print(f"-------------------------------------------------{Version[port]}")
                if 'Device ID.' in line:
                    Device_id[port] = line.split(' : ')[1].strip()
                    print(f"-------------------------------------------------{Device_id[port]}")
                if 'Adjusted Intensity' in line:
                    Adj_Int[port] = int(line.split(' : ')[1].strip())
                    print(f"--------------------------------------------------{Adj_Int[port]}")
                if 'Current drawn' in line:
                    Current[port] = float(line.split(' : ')[1].split(' ')[0].strip())
                    print(f"-------------------------------------------------{Current[port]}")
                if 'Adjusted DAC Value' in line:
                    DAC[port] = int(line.split(' : ')[1].strip())
                    print(f"-------------------------------------------------{DAC[port]}")

                if 'Mobile ID' in line:
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
                elif 'DAC has saturated ' in line or 'Fault' in line or 'Runaway' in line or 'Done' in line:
                    connected_device_info.write_data(arduino, '%')
                    quick_check_flag = 1
                    break
                else:
                    continue

                connected_device_info.write_data(arduino, command)

            if not quick_check_flag:
                port_list.append(port)
                arduino_list.append(arduino)
            # else:
                # discontinued.append(Device_id[port])

        # print(f"Rejected Device List: {discontinued}")

        all_device_single_run_Intensity_data = {f'{Device_id[port]}_{wavelength}_L{level}_{run+1}': [] for port in port_list}
        all_device_single_run_current_data = {f'{Device_id[port]}_{wavelength}_L{level}_{run+1}': [] for port in port_list}

        for port in port_list:
            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Version[port])
            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(wavelength)
            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(DAC[port])
            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Current[port])
            all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Adj_Int[port])

            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Version[port])
            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(wavelength)
            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(DAC[port])
            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Current[port])
            all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(Adj_Int[port])

        while arduino_list:
            for arduino, port in zip(arduino_list, port_list):
                try:
                    value = connected_device_info.read_data(arduino).split(' ')[0]
                except serial.SerialException as e:
                    print(f"Error reading data from {port}: {e}")
                    arduino_list.remove(arduino)
                    port_list.remove(port)
                    continue

                all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(value.split(',')[0])
                all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(value)
                print(f"{port} : {run + 1} :: {value}")

                if 'Done' in value:
                    all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'][-1] = user_id
                    connected_device_info.write_data(arduino, '%')
                    port_list.remove(port)
                    arduino_list.remove(arduino)

                if 'DAC' in value or 'Fault' in value or 'Runaway' in value:
                    connected_device_info.write_data(arduino, '%')
                    arduino_list.remove(arduino)
                    port_list.remove(port)


       # Your existing code to flatten the data
        flattened_intensity_data = [list(value) for value in all_device_single_run_Intensity_data.values()]
        flattened_current_data = [list(value) for value in all_device_single_run_current_data.values()]

        # Determine the maximum length of rows among all columns
        max_row_length = max(len(data) for data in flattened_intensity_data)

        # Pad shorter rows with zeros to match the length of the longest row
        for data in flattened_intensity_data:
            data.extend([0] * (max_row_length - len(data)))

        for data in flattened_current_data:
            data.extend([0] * (max_row_length - len(data)))

        # Rest of your code remains unchanged
        print("Flattened data:")
        for i, data in enumerate(flattened_intensity_data):
            print(f"Column {i}: {data}, Length: {len(data)}")

        columns = list(all_device_single_run_Intensity_data.keys())

        print("Columns:", columns)

        num_columns = len(columns)
        num_rows = max_row_length

        df = pd.DataFrame(flattened_intensity_data).T
        cdf = pd.DataFrame(flattened_current_data).T

        df.columns = columns
        cdf.columns = columns

        final = data_process(df)
        final.to_csv('data/main.csv', index=False)
