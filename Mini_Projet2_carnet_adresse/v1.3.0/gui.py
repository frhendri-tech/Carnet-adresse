import tkinter as tk
from tkinter import messagebox
from address_book import AddressBook

class AddressBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Carnet d'adresses")
        self.root.geometry("500x400")

        self.carnet = AddressBook()

        # ------------------------
        # FRAME HAUT
        # ------------------------
        frame_top = tk.Frame(root)
        frame_top.pack(pady=10)

        titre = tk.Label(frame_top, text="📒 Carnet d'adresses", font=("Arial", 16, "bold"))
        titre.pack()

        # ------------------------
        # FRAME MILIEU
        # ------------------------
        frame_middle = tk.Frame(root)
        frame_middle.pack(pady=10)

        self.listbox = tk.Listbox(frame_middle, width=60)
        self.listbox.pack()

        # ------------------------
        # FRAME BAS
        # ------------------------
        frame_bottom = tk.Frame(root)
        frame_bottom.pack(pady=10)

        tk.Button(frame_bottom, text="Ajouter", command=self.ajouter_contact).grid(row=0, column=0, padx=5)
        tk.Button(frame_bottom, text="Supprimer", command=self.supprimer_contact).grid(row=0, column=1, padx=5)
        tk.Button(frame_bottom, text="Rafraîchir", command=self.afficher_contacts).grid(row=0, column=2, padx=5)

        self.afficher_contacts()

    # ------------------------
    # Méthodes
    # ------------------------
    def afficher_contacts(self):
        self.listbox.delete(0, tk.END)
        for c in sorted(self.carnet.contacts, key=lambda x: x.nom.lower()):
            self.listbox.insert(tk.END, f"{c.nom} | {c.email} | {c.telephone}")

    def ajouter_contact(self):
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter un contact")

        tk.Label(fenetre, text="Nom").grid(row=0, column=0)
        tk.Label(fenetre, text="Email").grid(row=1, column=0)
        tk.Label(fenetre, text="Téléphone").grid(row=2, column=0)

        entry_nom = tk.Entry(fenetre)
        entry_email = tk.Entry(fenetre)
        entry_tel = tk.Entry(fenetre)

        entry_nom.grid(row=0, column=1)
        entry_email.grid(row=1, column=1)
        entry_tel.grid(row=2, column=1)

        def valider():
            nom = entry_nom.get()
            email = entry_email.get()
            tel = entry_tel.get()

            if not nom or not email or not tel:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
                return

            self.carnet.ajouter_contact(nom, email, tel)
            self.afficher_contacts()
            fenetre.destroy()

        tk.Button(fenetre, text="Valider", command=valider).grid(row=3, columnspan=2, pady=5)

    def supprimer_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un contact")
            return

        contact = self.listbox.get(selection[0])
        email = contact.split("|")[1].strip()

        self.carnet.supprimer_contact(email)
        self.afficher_contacts()
