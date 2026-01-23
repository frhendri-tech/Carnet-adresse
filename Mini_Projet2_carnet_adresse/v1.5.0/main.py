import tkinter as tk
from login_window import LoginWindow

def lancer_app():
    login_root.destroy()
    root = tk.Tk()
    from gui import AddressBookGUI
    AddressBookGUI(root)
    root.mainloop()

login_root = tk.Tk()
LoginWindow(login_root)
login_root.mainloop()
