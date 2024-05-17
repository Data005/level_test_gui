import serial
import os
import pandas as pd
import statistics as sts
import time
import datetime





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


# def data_process(df):



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

        Trend_mean = {}
        Trend_stdev = {}
        Trend_CV = {}
        Trend_Range = {}

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

        all_device_single_run_data = {f'{Device_id[port]}_{wavelength}_{level}_{run+1}':[] for port in port_list}
        for port in port_list:
            all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(Version[port])
            all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(wavelength)
            all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(DAC[port])
            all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(Current[port])
            all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(Adj_Int[port])


        while arduino_list:
            for arduino, port in zip(arduino_list, port_list):
                value = connected_device_info.read_data(arduino).split(' ')[0]
                all_device_single_run_data[f'{Device_id[port]}_{wavelength}_{level}_{run+1}'].append(value)
                print(f"{port} : {run + 1} :: {value}")
                # Check for specific conditions in the value received
                if 'DAC' in value or 'Fault' in value or 'Runaway' in value or 'Done' in value:
                    connected_device_info.write_data(arduino, '%')
                    arduino_list.remove(arduino)

                    port_list.remove(port)

        import json
        print(json.dumps(all_device_single_run_data, indent = 4))
        
        flattened_data = [list(value) for value in all_device_single_run_data.values()]

        # Create DataFrame without 'Key' column
        columns = [f'Value_{i}' for i in range(len(flattened_data[0]))]
        df = pd.DataFrame(flattened_data, columns=columns)

        # Transpose DataFrame
        df_transposed = df.T.reset_index()

        # Rename the index column to 'Key'
        df_transposed = df_transposed.rename(columns={'index': 'Key'})

        # Save transposed DataFrame to CSV
        df_transposed.to_csv(f'sheet_run{run + 1}_transposed.csv', index=False, header=False)

        print(df_transposed)

    return 0,0


def main():
    pc_name = os.getcwd().split('\\')[2].upper() + "_PC"
    print(pc_name)

    print("**Note: Use all devices of only one wavelength at a time")
    print("**Note: Fully charge the devices to run L5")
    print("**Note: Count all active ports in device manager, which should be equal to the number of devices connected.")
    print("**Note: Make sure that Bluetooth in the PC/Laptop is turned off")

    time_dur = 1
    repeats = 1
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
                all_data, error_cases = collect_data(connected_device_info, wavelength, level, repeats, time_dur, pc_name)
                # processed_data = process_data(all_data)
                # save_data(processed_data, error_cases, output_dir, pc_name, wavelength, level,"10110")
                time.sleep(delay)
    finally:
        connected_device_info.close_connections()
        print("Files can be found in this location: ", output_dir)


if __name__ == "__main__":
    main()
