from tkinter import *
from tkinter import *

def create_buttons_with_checkboxes(frame, device_config, text_box, connected_devices, update_text_box):
    wavelength_vars = {}
    level_vars = {}

    rm_wavelength_list = []
    rm_level_list = []

    def on_checkbox_toggle(var, config_key):
        if var.get() == 0:  # If checkbox is unchecked
            print_to_text_box(f"{config_key} removed", text_box)
            if "L" in config_key:
                rm_level_list.append(config_key)
            else:
                rm_wavelength_list.append(config_key)
        else:  # If checkbox is checked
            print_to_text_box(f"{config_key} added", text_box)
            if "L" in config_key:
                rm_level_list.remove(config_key)
            else:
                rm_wavelength_list.remove(config_key)
        update_text_box()  # Update the text box with the current device_config

    def clear_all_selections():
        for var in wavelength_vars.values():
            var.set(0)
        for var in level_vars.values():
            var.set(0)
        print_to_text_box("All selections cleared", text_box)
        update_text_box()  # Update the text box with the current device_config

    def select_all_selections():
        for var in wavelength_vars.values():
            var.set(1)
        for var in level_vars.values():
            var.set(1)
        rm_wavelength_list.clear()
        rm_level_list.clear()
        print_to_text_box("All selected", text_box)
        update_text_box()  # Update the text box with the current device_config

    # Display connected devices
    row = 0
    Label(frame, text="Connected Devices:", bg="gray", fg="white").grid(row=row, column=0, padx=10, pady=5, sticky=W)
    row += 1
    for device in connected_devices:
        Label(frame, text=device, bg="gray", fg="white").grid(row=row, column=0, padx=10, pady=5, sticky=W)
        row += 1

    # Wavelengths
    Label(frame, text="Wavelengths", bg="gray", fg="white").grid(row=0, column=1, padx=10, pady=5, sticky=W)
    row = 1
    for wavelength in ["528", "620", "367", "405"]:
        var = IntVar(value=1)  # Set default value to checked (1)
        wavelength_vars[wavelength] = var
        Checkbutton(frame, text=wavelength, variable=var, command=lambda v=var, k=wavelength: on_checkbox_toggle(v, k)).grid(row=row, column=1, padx=20, sticky=W)
        row += 1

    # Levels
    Label(frame, text="Levels", bg="gray", fg="white").grid(row=0, column=2, padx=10, pady=5, sticky=W)
    row = 1
    for level in ["L1", "L5"]:
        var = IntVar(value=1)  # Set default value to checked (1)
        level_vars[level] = var
        Checkbutton(frame, text=level, variable=var, command=lambda v=var, k=level: on_checkbox_toggle(v, k)).grid(row=row, column=2, padx=20, sticky=W)
        row += 1

    # Adding empty space before buttons
    row += 1

    # Add clear and reset buttons at the bottom
    clear_button = Button(frame, text="Clear All", command=clear_all_selections)
    clear_button.grid(row=row+50, column=1, padx=10, pady=10, sticky=S)

    reset_button = Button(frame, text="Select All", command=select_all_selections)
    reset_button.grid(row=row+50, column=2, padx=10, pady=10, sticky=S)
    print(rm_wavelength_list)
    print(rm_level_list)
    return rm_wavelength_list, rm_level_list

def print_to_text_box(text, text_box):
    text_box.config(state=NORMAL)
    text_box.insert(END, str(text) + "\n")
    text_box.config(state=DISABLED)
    text_box.see(END)
