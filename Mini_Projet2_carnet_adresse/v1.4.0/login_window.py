import tkinter as tk
from tkinter import messagebox
from auth import verifier_login
from gui import AddressBookGUI

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Connexion Admin")
        self.root.geometry("300x200")

        tk.Label(root, text="Connexion Administrateur", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(root, text="Nom d'utilisateur").pack()
        self.entry_user = tk.Entry(root)
        self.entry_user.pack()

        tk.Label(root, text="Mot de passe").pack()
        self.entry_pass = tk.Entry(root, show="*")
        self.entry_pass.pack()

        tk.Button(root, text="Se connecter", command=self.login).pack(pady=10)

    def login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()

        if verifier_login(user, pwd):
            messagebox.showinfo("Succès", "Connexion réussie")
            self.root.destroy()

            root_app = tk.Tk()
            AddressBookGUI(root_app)
            root_app.mainloop()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
