import serial
import time
import os
import pandas as pd
import numpy as np
import serial.tools.list_ports as sp
import statistics as sts
import time
import datetime
date_obj = datetime.date.today()
date = str(date_obj.day) + '_' + str(date_obj.month) + '_' + str(date_obj.year)
cwd = os.getcwd()
pc_name = cwd.split('\\')[2].upper()+"_PC"
print(pc_name)
print("**Note Use all devices of only one wavelength at a time")
print("**Note Full charge the devices to run L5")
print("**Note Count all active ports in device manager, that should be equal to no. of devices connected.")
print("**Note Make sure that bluetooth in the PC/Laptop is turned off")
print("hello")
# user = int(input("Enter 1 for PC, 2 for Laptop : "))

#*******************************************************************************************************************************

# Inputs to the automation code

time_dur = 15
repeats = 5
delay = 10
level_list = [1, 5]

# Constants
charge_limit = 3.4            # Restict user from performing test if charge is below 3.5 for 5 runs


# Input to be taken from user (Also restrict user from entering invald entries)
t = 0
while t < 1:
    try:
        wv_type = int(input("Enter 1 for dual device, 2 for 367 device, 3 for 405 device : "))
        if wv_type not in [1, 2, 3]:
            raise Exception
    except:
        print('Invalid wavelength! Please try again!')
    else:
        t += 1

# Wavelength selection section
if wv_type == 1:
    wavelength_list = [528, 620]
elif wv_type == 2:
    wavelength_list = [367]
else:
    wavelength_list = [405]
    
    
# Listing all available ports
ports = sp.comports()
port_list = []
[port_list.append(str(single_port).split('-')[0].strip()) for single_port in ports]
print(port_list)

#*******************************************************************************************************************************
# Creating dynamic variabes for selecting the arduino function
arduino_variables = []
for count in range(len(port_list)):
    arduino_variables.append('Arduino_{}'.format(count+1))
    globals()[arduino_variables[count]] = serial.Serial(port=port_list[count], baudrate=115200, timeout=2)

#*******************************************************************************************************************************
for wavelength in wavelength_list:
    for level in level_list:
        # Creating empty dictionaries of Runs and Ports to store data
        all_data = dict()

        for num in range(len(port_list)):
            run_dict = dict()
            errors_dict = dict()  
            for run in range(repeats):
                run_dict.update({"Run_{}".format(run+1) : []})

 
            # ******** For adding "Error cases" ********* 
            # 1. Adding "DAC sat case"
            errors_dict.update({"DAC sat cases" : []})

            # 2. Adding "Device fault case"
            errors_dict.update({"Device fault cases" : []})

            # 3. Adding "Thermal Runaway 1"
            errors_dict.update({"Thermal Runaway 1 cases" : []})

            # 4. Adding "Thermal Runaway 2"
            errors_dict.update({"Thermal Runaway 2 cases" : []})

            # 5. Adding "Thermal Runaway 3"
            errors_dict.update({"Thermal Runaway 3 cases" : []}) 

            # 6. Charge the device"
            errors_dict.update({"Charge the device cases" : []}) 

            run_dict.update({'Error cases' : errors_dict})
            all_data.update({port_list[num] : run_dict})

        #*******************************************************************************************************************************

        # ********* Creating a function that reads and writes to arduino **********
        def loop_run(arduino, port, run_no):
            dac_sat_flag = 0            # Initiating dac saturation flag
            device_fault_flag = 0       # Initiating device saturation flag
            thermal1_fault_flag = 0     # Initiating thermal runaway 1 flag
            thermal2_fault_flag = 0     # Initiating thermal runaway 2 flag
            thermal3_fault_flag = 0     # Initiating thermal runaway 3 flag
            charge_fault_flag = 0       # Initiating charging fault
            end_operation_flag = 0      # Initiating completion flag

            def write(x):
                arduino.write(bytes(x, 'utf-8'))
                data = arduino.readline()
                return data

            file_data = []
            for i in range(1):
                # Read
                value = arduino.readline()
                decoded_value = str(value, 'utf-8')
                print(port + ' : ' + 'Run ' + str(run_no) + ' :: ', end="")
                print(decoded_value, end ="")
                file_data.append(decoded_value)
                if decoded_value == str():
                    value = arduino.write(bytes('r', 'utf-8'))
                    continue

                # Write
                if "For change Device ID press 'C' and 'R' For Run Code" in decoded_value:
                    value = write(str('R'))
                    decoded_value = str(value, 'utf-8')
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Mobile ID' in decoded_value:
                    value = write(str(pc_name))
                    decoded_value = str(value, 'utf-8')
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Enter the level' in decoded_value:
                    value = write(str(level))
                    decoded_value = str(value, 'utf-8')
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Enter Wavelength' in decoded_value:
                    value = write(str(wavelength))
                    decoded_value = str(value, 'utf-8')
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Enter Test Duration' in decoded_value:
                    value = write(str(time_dur))
                    decoded_value = str(value,'utf-8')
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Enter P to proceed' in decoded_value or "Done." in decoded_value:
                    end_operation_flag = 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                    break
                if 'DAC has saturated' in decoded_value:
                    dac_sat_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Device Fault' in decoded_value:
                    device_fault_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Thermal Runaway 1' in decoded_value:
                    thermal1_fault_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Thermal Runaway 2' in decoded_value:
                    thermal2_fault_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                    time.delay(3)
                if 'Thermal Runaway 3' in decoded_value:
                    thermal3_fault_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)
                if 'Charge the device' in decoded_value:
                    charge_fault_flag += 1
                    # Reset code
                    value = write('%')
                    decoded_value = str(value,'utf-8')
                    print(port + ' :: ', end="")
                    print(decoded_value, end = "")
                    file_data.append(decoded_value)

            return file_data, dac_sat_flag, device_fault_flag, thermal1_fault_flag, thermal2_fault_flag, thermal3_fault_flag, charge_fault_flag, end_operation_flag

        #******************************************************************************************************************************* 

        # Loop runs of the same level

        for run in range(repeats):
            if run == 0:
                device_IDS = [""]*len(port_list)
            end_operation = [0]*len(port_list) #------ Creating [0, 0, 0] for 3 devices(ports). 0 indicates not completed
            dac_sat_end = [0]*len(port_list)
            device_fault_end = [0]*len(port_list)
            thermal1_fault_end = [0]*len(port_list)
            thermal2_fault_end = [0]*len(port_list)
            thermal3_fault_end = [0]*len(port_list)
            charge_fault_end = [0]*len(port_list)

            while end_operation != [1]*len(port_list):

                for port_num in range(len(port_list)):

                    # All error cases attached
                    dac_sat_cases = sum(all_data[port_list[port_num]]['Error cases']['DAC sat cases'])
                    device_fault_cases = sum(all_data[port_list[port_num]]['Error cases']['Device fault cases'])
                    thermal1_fault_cases = sum(all_data[port_list[port_num]]['Error cases']['Thermal Runaway 1 cases'])
                    thermal2_fault_cases = sum(all_data[port_list[port_num]]['Error cases']['Thermal Runaway 2 cases'])
                    thermal3_fault_cases = sum(all_data[port_list[port_num]]['Error cases']['Thermal Runaway 3 cases'])
                    charge_fault_cases = sum(all_data[port_list[port_num]]['Error cases']['Charge the device cases'])
                    
                    if end_operation[port_num] == 0 and  dac_sat_cases <= 3 and device_fault_cases <= 3 and thermal1_fault_cases <= 1 and thermal2_fault_cases <= 1 and thermal3_fault_cases <= 1 and charge_fault_cases <= 1:
                        dac_sat_flag = 0
                        device_fault_flag = 0
                        thermal1_fault_flag = 0
                        thermal2_fault_flag = 0
                        thermal3_fault_flag = 0
                        charge_fault_flag = 0

                        data, dac_sat_flag, device_fault_flag, thermal1_fault_flag, thermal2_fault_flag, thermal3_fault_flag, charge_fault_flag, end_operation_flag = loop_run(globals()[arduino_variables[port_num]], port_list[port_num],run+1)
                        print()

                        if "DEVICE ID :" in data[0] or "Device ID" in data[0]:
                            device_IDS[port_num] = data[0].split(':')[-1].strip()

                        all_data[port_list[port_num]]['Run_{}'.format(run+1)].extend(data)
                        if end_operation_flag == 1:
                            end_operation[port_num] = 1
                            all_data[port_list[port_num]]['Error cases']['DAC sat cases'].append(dac_sat_flag)
                            all_data[port_list[port_num]]['Error cases']['Device fault cases'].append(device_fault_flag)
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 1 cases'].append(device_fault_flag)
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 2 cases'].append(device_fault_flag)
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 3 cases'].append(device_fault_flag)
                            all_data[port_list[port_num]]['Error cases']['Charge the device cases'].append(device_fault_flag)
                        if dac_sat_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['DAC sat cases'].append(dac_sat_flag)
                            dac_sat_end[port_num]+=1
                        if device_fault_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['Device fault cases'].append(device_fault_flag)
                            device_fault_end[port_num]+=1
                        if thermal1_fault_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 1 cases'].append(thermal1_fault_flag)
                            thermal1_fault_end[port_num]+=1
                        if thermal2_fault_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 2 cases'].append(thermal2_fault_flag)
                            thermal2_fault_end[port_num]+=1
                        if thermal3_fault_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['Thermal Runaway 3 cases'].append(thermal3_fault_flag)
                            thermal3_fault_end[port_num]+=1
                        if charge_fault_flag == 1:
                            all_data[port_list[port_num]]['Error cases']['Charge the device cases'].append(charge_fault_flag)
                            charge_fault_end[port_num]+=1

                        if dac_sat_end[port_num] == 3 or device_fault_end[port_num] == 3 or thermal1_fault_end[port_num] == 1 or thermal2_fault_end[port_num] == 1 or thermal3_fault_end[port_num] == 1 or charge_fault_end[port_num] == 1:
                            end_operation[port_num] = 1
                            
                    else:
                        end_operation[port_num] = 1 



            time.sleep(delay)
        #*******************************************************************************************************************************    
        # Data Cleaning function
        def func_clean(file_data):
            data = [k.strip() for k in file_data]
            rem_index = []
            for k in range(len(data)):
                if len(data[k]) == 0:
                    rem_index.append(k)

            rem_index.reverse()
            for count in range(len(rem_index)):
                data.pop(rem_index[count])

            # data
            count = 0
            for ind in range(len(data)):
                if data[ind][-1] == ':':
                    count += 1

            for ind in range(len(data)-count):
                if data[ind][-1] == ':':
                    data[ind] = ' '.join([data[ind],data[ind+1]])
                    data.pop(ind+1)

            # cleaned data
            dac_sat_id = -1
            for c in range(len(data)):
                if "DAC has saturated" in data[c]:
                    dac_sat_id = c
            data = data[dac_sat_id+1:]

            device_fault_id = -1
            for d in range(len(data)):
                if "Device fault" in data[d]:
                    device_fault_id = d
            data = data[device_fault_id+1:]

            thermal1_fault_id = -1
            for d in range(len(data)):
                if "Thermal Runaway 1" in data[d]:
                    thermal1_fault_id = d
            data = data[thermal1_fault_id+1:]

            thermal2_fault_id = -1
            for d in range(len(data)):
                if "Thermal Runaway 2" in data[d]:
                    thermal2_fault_id = d
            data = data[thermal2_fault_id+1:]

            thermal3_fault_id = -1
            for d in range(len(data)):
                if "Thermal Runaway 3" in data[d]:
                    thermal3_fault_id = d
            data = data[thermal3_fault_id+1:]

            charge_fault_id = -1
            for d in range(len(data)):
                if "Charge the device" in data[d]:
                    charge_fault_id = d
            data = data[charge_fault_id+1:]

            return data

        # Data Cleaning Code
        for com in port_list:
            for level_no in range(repeats):
                all_data[com]['Run_{}'.format(level_no+1)] = func_clean(all_data[com]['Run_{}'.format(level_no+1)])

        coms = [k for k in all_data.keys()]
        for iter in range(len(coms)):
            all_data[device_IDS[iter]] = all_data[coms[iter]]
            del all_data[coms[iter]] 

        import json
        print(json.dumps(all_data, indent = 4))

        # Store and calculate data in dataframe
        df_calc = pd.DataFrame()
        df_data = pd.DataFrame()

        for device in device_IDS:
            df = pd.DataFrame()

            MEAN = []
            SD = []
            CV = []
            RANGE = []
            tuples_list = []
            for run in range(repeats):
                run_id = 'Run_{}'.format(run+1)
                tuples_list.append((device, run_id))
                start = []
                end = []

                # Data extract
                if all_data[device][run_id] != []:                                   # Extract data only if non-empty
                    for i in range(len(all_data[device][run_id])):
                        if 'Press Enter to start' in all_data[device][run_id][i]:
                            if '...' in all_data[device][run_id][i+1]:
                                start.append(i+1)
                            else:
                                start.append(i)
                        if 'Done.' in all_data[device][run_id][i]:
                            end.append(i)

                    run_data = all_data[device][run_id][start[0]+1:end[0]]
                    run_data = [int(k.split(',')[0]) for k in run_data]

                    df[run_id] = run_data

                    # Calculation
                    mean_run = sts.mean(run_data)
                    std_run = sts.stdev(run_data)
                    cv = std_run*100/mean_run
                    range_run = max(run_data)-min(run_data)

                    MEAN.append(round(mean_run,4))
                    SD.append(round(std_run,4))
                    CV.append(round(cv,4))
                    RANGE.append(range_run)

                else:                                                                # Do this when data is empty
                    run_data = all_data[device][run_id]
                    df[run_id] = [np.nan]*1363

                    # Calculation
                    mean_run = 0
                    std_run = 0
                    cv = 0
                    range_run = 0

                    MEAN.append(mean_run)
                    SD.append(std_run)
                    CV.append(cv)
                    RANGE.append(range_run)

            column_names = pd.MultiIndex.from_tuples(tuples_list)
            df.columns = column_names

            df_data = pd.concat([df_data, df], axis = 1)

            df_calc_single = pd.DataFrame({'MEAN':MEAN, 'SD':SD, 'CV':CV, 'RANGE':RANGE})
            df_calc_single = df_calc_single.transpose()
            df_calc_single.columns = column_names
            df_calc = pd.concat([df_calc, df_calc_single], axis = 1)

        df_all = pd.concat([df_calc, df_data])

        df_all

        df_dac_sat_cases = pd.DataFrame(columns = device_IDS)
    
        for dev in device_IDS:
            df_dac_sat_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['DAC sat cases'])
            df_dac_sat_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['DAC sat cases']
        print(df_dac_sat_cases)

        df_device_fault_cases = pd.DataFrame(columns = device_IDS)
        for dev in device_IDS:
            df_device_fault_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['Device fault cases'])
            df_device_fault_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['Device fault cases']
        print(df_device_fault_cases)

        df_thermal1_fault_cases = pd.DataFrame(columns = device_IDS)
        for dev in device_IDS:
            df_thermal1_fault_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['Thermal Runaway 1 cases'])
            df_thermal1_fault_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['Thermal Runaway 1 cases']
        print(df_thermal1_fault_cases)

        df_thermal2_fault_cases = pd.DataFrame(columns = device_IDS)
        for dev in device_IDS:
            df_thermal2_fault_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['Thermal Runaway 2 cases'])
            df_thermal2_fault_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['Thermal Runaway 2 cases']
        print(df_thermal2_fault_cases)

        df_thermal3_fault_cases = pd.DataFrame(columns = device_IDS)
        for dev in device_IDS:
            df_thermal3_fault_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['Thermal Runaway 3 cases'])
            df_thermal3_fault_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['Thermal Runaway 3 cases']
        print(df_thermal3_fault_cases)

        df_charge_fault_cases = pd.DataFrame(columns = device_IDS)
        for dev in device_IDS:
            df_charge_fault_cases[dev] = [np.nan]*15
            size = len(all_data[dev]['Error cases']['Charge the device cases'])
            df_charge_fault_cases.loc[:size-1, dev] = all_data[dev]['Error cases']['Charge the device cases']
        print(df_charge_fault_cases)
    

        #********************************************************************************************************************************
        # Data saving code
        # For storing data in local storage
        if 'AUTO_DATA' not in os.listdir(cwd):
            directory = "AUTO_DATA"
            file_path = os.path.join(cwd, directory) 
            os.mkdir(file_path)
        else:
            directory = "AUTO_DATA"
            file_path = os.path.join(cwd, directory) 

        # Store the data in excel
        with pd.ExcelWriter(file_path+"\\" + date + "_" + str(wavelength) + '_L' + str(level) + "_" + "_".join(device_IDS) +'.xlsx') as writer:
            df_all.to_excel(writer, sheet_name = "Data")
            df_dac_sat_cases.to_excel(writer, sheet_name = "DAC sat cases")
            df_device_fault_cases.to_excel(writer, sheet_name = "Device fault cases")
            df_thermal1_fault_cases.to_excel(writer, sheet_name = "Thermal Runaway 1 cases")
            df_thermal2_fault_cases.to_excel(writer, sheet_name = "Thermal Runaway 2 cases")
            df_thermal3_fault_cases.to_excel(writer, sheet_name = "Thermal Runaway 3 cases")
            df_charge_fault_cases.to_excel(writer, sheet_name = "Charge the device cases")


        # To convert data to files in a specific folder
        for dev in device_IDS:

            directory = str(wavelength)
            new_file_path_wv = os.path.join(file_path, directory) 
            
            if not os.path.exists(new_file_path_wv):
                os.mkdir(new_file_path_wv)

            directory = "L"+str(level)
            new_file_path_level = os.path.join(new_file_path_wv, directory) 

            if not os.path.exists(new_file_path_level):
                os.mkdir(new_file_path_level)

            directory = dev
            new_file_path = os.path.join(new_file_path_level, directory) 

            if not os.path.exists(new_file_path):
                os.mkdir(new_file_path)

            for run in range(repeats):
                run_id = 'Run_' + str(run+1)
                file_name = dev + '_' + str(wavelength) +'_' + 'L' + str(level) + '_' + str(run+1) +'.txt'
                raw_file_path = new_file_path + "\\" + file_name
                if os.path.exists(raw_file_path):
                    os.remove(raw_file_path)
                f = open(raw_file_path, "x")
                for line in range(len(all_data[dev][run_id])):
                    f.write(all_data[dev][run_id][line])
                    f.write('\n')

                f.close()
                
print("Files can be found in this location", file_path)



