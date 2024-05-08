import tkinter as tk
import pages.home_page as home_page

def verify_login(username, password):
    # Dummy verification logic, replace with your actual authentication process
    return username == "admin" and password == "password"

def login_button_clicked(root, username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()
    
    if verify_login(username, password):
        root.destroy()  # Close current window
        home_page.setup_home_page()

def setup_login_page(root):
    # username_label = tk.Label(root, text="Username:")
    # username_label.place(relx=0.5, rely=0.36, anchor=tk.CENTER)
    
    username_entry = tk.Entry(root)
    username_entry.place(relx=0.73, rely=0.36, anchor=tk.CENTER)

    # password_label = tk.Label(root, text="Password:")
    # password_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    password_entry = tk.Entry(root, show="*")
    password_entry.place(relx=0.73, rely=0.5, anchor=tk.CENTER)

    login_button = tk.Button(root, text="Login", command=lambda: login_button_clicked(root, username_entry, password_entry))
    login_button.place(relx=0.73, rely=0.595, anchor=tk.CENTER)