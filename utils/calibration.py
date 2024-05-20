import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime

def get_device_data(device_id):
    file_path = 'data/calibration_data.xlsx'
    
    df = pd.read_excel(file_path)

    filtered_df = df[df['device id'] == device_id]

    if filtered_df.empty:
        return []

    data_list = filtered_df[['batch no', 'lot no', 'wavelength', 'level', 'calibration issue']].values.tolist()

    return data_list


def calibration(connected_device_info):
    file_path = 'data/calibration_data.xlsx'
    df = pd.read_excel(file_path)

    device_status = {}
    
    port_list = []
    arduino_list = []
    # discontinued = []

    Version = {}
    DAC = {}
    Current = {}
    Adj_Int = {}
    Device_id = {}

    loop_run = 0  # Initialize loop_run
    run = 0  # Initialize run

    for idx, arduino in enumerate(connected_device_info.connected_device_list):
        quick_check_flag = 0
        port = arduino.port
        
        loop_run += 1
        print(f'Loop run : {loop_run} :: port : {port}')
    
        input_list = {
            'ID': 'ID',
            'level': '1',
            'Wavelength': '528',+
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

            if 'Mobile ID' in line:
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
                device_status[Device_id[port]] = line
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
        #     discontinued.append(Device_id[port])

    for device_id in Device_id.values():
        issue = device_status.get(device_id, 'NO Issue')
        if issue != 'NO Issue':
            df.loc[df['device id'] == device_id, 'calibration issue'] = issue
        else:
            device_data = get_device_data(device_id)
            if not device_data:
                continue

            batch_no, lot_no, wavelength, level, _ = device_data[0]

            df.loc[(df['device id'] == device_id) & (df['batch no'] == batch_no) & (df['lot no'] == lot_no) & (df['wavelength'] == wavelength) & (df['level'] == level), 'calibration issue'] = 'NO Issue'
    
    # Save the updated DataFrame back to the Excel file
    df.to_excel(file_path, index=False)
    print("save ho gya")


def get_device_and_port_id(connected_device_info):
    device_port = []
    
    for idx, arduino in enumerate(connected_device_info.connected_device_list):
        while True:
            line = connected_device_info.read_data(arduino)
            # print(line)
            if 'Device ID.' in line:
                Device_id = line.split(' : ')[1].strip()
                device_port.append(f"{Device_id}_{arduino.port}")
                
                connected_device_info.write_data(arduino, '%')
                connected_device_info.read_data(arduino)
                break
            connected_device_info.write_data(arduino, "r")
    return device_port