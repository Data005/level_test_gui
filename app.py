import tkinter as tk
from tkinter import PhotoImage
import pages.login_page as login_page


def show_login_page(root):
    login_page.setup_login_page(root)

def show_home_page(root):
    home_page.setup_home_page(root)

def main():
    root = tk.Tk()
    root.title("Device Stability Testing")
    root.resizable(False, False)
    root.geometry("810x490")

    # Load background image
    image_path = "data/img.png"
    bg_image = PhotoImage(file=image_path)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

    show_login_page(root)

    root.mainloop()

if __name__ == "__main__":
    main()
