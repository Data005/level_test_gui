from tkinter import *
from tkinter import ttk

def print_to_text_box(text,text_box):
    text_box.config(state=NORMAL)
    text_box.insert(END, str(text) + "\n")
    text_box.config(state=DISABLED)
    text_box.see(END)

def on_selection_change(event, device_name, level_combobox, wavelength_combobox, duration_combobox):
    device_data[device_name] = [
        level_combobox.get(),
        wavelength_combobox.get(),
        duration_combobox.get()
    ]

def create_buttons_with_dropdowns(frame, button_list, level_options, wavelength_options, duration_options,text_box,root):
    global device_data
    device_data = {}  # Dictionary to store device data
    
    def print_device_data():
        print_to_text_box(device_data,text_box)
    
    for row, device_name in enumerate(button_list):
        Button(frame, text=device_name, width=15, height=2).grid(row=row, column=0, padx=10, pady=10)
        
        level_combobox = ttk.Combobox(frame, values=level_options, width=8, height=2)
        level_combobox.grid(row=row, column=1, padx=2, pady=10)
        
        wavelength_combobox = ttk.Combobox(frame, values=wavelength_options, width=8, height=2)
        wavelength_combobox.grid(row=row, column=2, padx=2, pady=10)
        
        duration_combobox = ttk.Combobox(frame, values=duration_options, width=8, height=2)
        duration_combobox.grid(row=row, column=3, padx=2, pady=10)
        
        # Bind the event to the lambda function
        level_combobox.bind('<<ComboboxSelected>>', lambda event, device_name=device_name, level_combobox=level_combobox, wavelength_combobox=wavelength_combobox, duration_combobox=duration_combobox: on_selection_change(event, device_name, level_combobox, wavelength_combobox, duration_combobox))
        wavelength_combobox.bind('<<ComboboxSelected>>', lambda event, device_name=device_name, level_combobox=level_combobox, wavelength_combobox=wavelength_combobox, duration_combobox=duration_combobox: on_selection_change(event, device_name, level_combobox, wavelength_combobox, duration_combobox))
        duration_combobox.bind('<<ComboboxSelected>>', lambda event, device_name=device_name, level_combobox=level_combobox, wavelength_combobox=wavelength_combobox, duration_combobox=duration_combobox: on_selection_change(event, device_name, level_combobox, wavelength_combobox, duration_combobox))
    

    # Add a button to print device data
    print_button = Button(frame, text="Print Device Data", command=print_device_data)
    print_button.grid(row=len(button_list), columnspan=4, pady=10)
    return device_data

