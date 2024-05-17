import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from data_process import data_process

def collect_data(connected_device_info, wavelength, level, repeats, time_dur, pc_name):
    all_data = {}
    error_cases = {}
    for run in range(repeats):
        
        
        loop_run = 0

        port_list = []
        arduino_list = []
        discontinued = []

        Version = {}
        DAC = {}
        Current = {}
        Adj_Int = {}
        Device_id = {}


        for idx, arduino in enumerate(connected_device_info.connected_device_list):
            
            quick_check_flag = 0
            port = arduino.port
            
            loop_run +=1
            print(f'Loop run : {loop_run} :: port : {port}')
        
            input_list ={
                'ID' : 'ID',
                'level' : '1',
                'Wavelength': '528',
                'Duration': '1'
                }

            line = ""
            while True:
                line = connected_device_info.read_data(arduino)
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


                if 'Mobile ID' in line :
                    command = input_list['ID']
                elif 'level' in line:
                    command = input_list['level']
                elif 'Wavelength' in line:
                    command = input_list['Wavelength']
                elif 'Duration' in line: 
                    command = input_list['Duration']
                elif 'Press Enter' in line:
                    connected_device_info.write_data(arduino, "r")
                    break
                elif 'DAC has saturated ' in line or 'Fault' in line or 'Runaway' in line or 'Done' in line:
                    # discontinued[Device_id[port]] = connected_device_info.read_data(arduino)
                    connected_device_info.write_data(arduino, '%')
                    quick_check_flag = 1
                    break
                else : continue

                connected_device_info.write_data(arduino, command)

            if not quick_check_flag:
                port_list.append(port)
                arduino_list.append(arduino)
            else:
                discontinued.append(Device_id[port])


        print(f"Rejected Device List: {discontinued}")

        all_device_single_run_Intensity_data = {f'{Device_id[port]}_{wavelength}_L{level}_{run+1}':[] for port in port_list}
        all_device_single_run_current_data = {f'{Device_id[port]}_{wavelength}_L{level}_{run+1}':[] for port in port_list}

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
                value = connected_device_info.read_data(arduino).split(' ')[0]
                all_device_single_run_Intensity_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(value.split(',')[0])
                all_device_single_run_current_data[f'{Device_id[port]}_{wavelength}_L{level}_{run+1}'].append(value)
                print(f"{port} : {run + 1} :: {value}")
                # Check for specific conditions in the value received
                if 'DAC' in value or 'Fault' in value or 'Runaway' in value or 'Done' in value:
                    connected_device_info.write_data(arduino, '%')
                    arduino_list.remove(arduino)

                    port_list.remove(port)

        import json
        print(json.dumps(all_device_single_run_Intensity_data, indent = 4))
        
        flattened_intensity_data = [list(value) for value in all_device_single_run_Intensity_data.values()]
        flattened_current_data = [list(value) for value in all_device_single_run_current_data.values()]

        # Check the structure
        print("Flattened data:")
        for i, data in enumerate(flattened_intensity_data):
            print(f"Column {i}: {data}, Length: {len(data)}")

        # Extracting the column names
        columns = list(all_device_single_run_Intensity_data.keys())

        # Check column names
        print("Columns:", columns)

        num_columns = len(columns)
        num_rows = len(flattened_intensity_data[0]) if flattened_intensity_data else 0
        for col_data in flattened_intensity_data:
            if len(col_data) != num_rows:
                raise ValueError(f"Column data length mismatch. Expected {num_rows}, but got {len(col_data)}")

        df = pd.DataFrame(flattened_intensity_data).T  # Transpose to match columns
        cdf = pd.DataFrame(flattened_current_data).T  # Transpose to match columns

        df.columns = columns
        cdf.columns = columns
        
        final = data_process(df)
        final.to_csv('data/main.csv')