import tkinter as tk
from login_window import LoginWindow

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


import login_window
print(dir(login_window))
