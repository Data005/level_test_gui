import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading

def run_auto_script(output_text):
    def execute_script():
        try:
            output_text.delete(1.0, tk.END)
            process = subprocess.run(["python", "auto.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output_text.insert(tk.END, process.stdout)
        except Exception as e:
            output_text.insert(tk.END, f"Error occurred: {e}\n")

    # Start the script in a separate thread
    threading.Thread(target=execute_script, daemon=True).start()

def submit_user_input(user_input, output_text, input_entry):
    output_text.insert(tk.END, f"User Input: {user_input}\n")
    input_entry.delete(0, tk.END)  # Clear the input entry after submitting

def setup_home_page():
    root = tk.Tk()
    root.title("Home Page")

    label = tk.Label(root, text="Welcome to Home Page")
    label.pack()

    # Text widget to display the script output
    output_text = ScrolledText(root, width=80, height=20)
    output_text.pack()

    # Entry widget for user input
    input_entry = tk.Entry(root, width=40)
    input_entry.pack()

    # Button to run the auto.py script
    run_script_button = tk.Button(root, text="Run Script", command=lambda: run_auto_script(output_text))
    run_script_button.pack()

    # Button to submit user input
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_user_input(input_entry.get(), output_text, input_entry))
    submit_button.pack()

    # Logout button to close current window and restart the app
    logout_button = tk.Button(root, text="Logout", command=root.destroy)
    logout_button.pack()

    root.mainloop()

# Entry point to set up the home page
if __name__ == "__main__":
    setup_home_page()
