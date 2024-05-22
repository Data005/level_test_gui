import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime
from openpyxl import load_workbook, Workbook

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


def filter_and_save_excel(src_file = 'data/main.csv', snk_file = 'data/output.xlsx'):
    df = pd.read_csv(src_file, header=0)

    try:
        workbook = load_workbook(snk_file)
    except Exception as e:
        print(f"Error loading workbook: {e}")
        # Create a new workbook if the existing file is not valid
        workbook = Workbook()
        workbook.save(snk_file)
        workbook = load_workbook(snk_file)

    for col in df.columns:
        if "L1" in col:
            sheet_name = "L1"
        elif "L3" in col:
            sheet_name = "L3"
        elif "L5" in col:
            sheet_name = "L5"
        elif "L6" in col:
            sheet_name = "L6"
        elif "L7" in col:
            sheet_name = "L7"
        else:
            print(f"Incorrect Column Name: {col}")
            sheet_name = "Other"
            continue

        if sheet_name not in workbook.sheetnames:
            workbook.create_sheet(sheet_name)
        sheet = workbook[sheet_name]
        last_col = sheet.max_column

        # Add the list to the last column
        sheet.cell(1, column=last_col + 1, value=col)
        for i in range(len(df[col])):
            value = df[col][i]
            # Check if the value can be converted to a number
            if pd.api.types.is_numeric_dtype(df[col]) or isinstance(value, (int, float)):
                value = float(value)
            else:
                try:
                    # Try to convert to a float
                    value = float(value)
                except ValueError:
                    # If conversion fails, keep as string
                    pass
            sheet.cell(row=i + 2, column=last_col + 1, value=value)
            print(f"sheet: {sheet_name} --------- Column: {col} --------- value: {value} --------- Row: {i + 2}")

    # Sort columns in each sheet by their header names
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        headers = [(sheet.cell(1, col).value, col) for col in range(1, sheet.max_column + 1)]
        headers_sorted = sorted(headers, key=lambda x: (x[0] is None, x[0]))

        # Create a new sorted DataFrame for the sheet
        sorted_data = []
        for header, col in headers_sorted:
            if header is not None:
                col_data = [sheet.cell(row, col).value for row in range(2, sheet.max_row + 1)]  # Skip the header row
                sorted_data.append((header, col_data))

        # Clear existing data in the sheet except the header row
        sheet.delete_rows(2, sheet.max_row)
        # Delete the last column before rewriting data
        sheet.delete_cols(sheet.max_column)

        # Write the sorted data back to the sheet
        for col_index, (header, col_data) in enumerate(sorted_data, start=1):
            sheet.cell(row=1, column=col_index, value=header)  # Write the header
            for row_index, value in enumerate(col_data, start=1):
                sheet.cell(row=row_index + 1, column=col_index, value=value)  # Add 1 to skip the header row

    workbook.save(snk_file)

