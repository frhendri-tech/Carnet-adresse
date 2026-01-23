import tkinter as tk
from tkinter import ttk, messagebox
from address_book import AddressBook


class AddressBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Carnet d'adresses")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.carnet = AddressBook()

        # =====================
        # TITRE
        # =====================
        frame_title = ttk.Frame(root, padding=10)
        frame_title.pack()

        ttk.Label(
            frame_title,
            text="📒 Carnet d'adresses",
            font=("Segoe UI", 18, "bold")
        ).pack()

        # =====================
        # LISTE DES CONTACTS
        # =====================
        frame_list = ttk.Frame(root, padding=10)
        frame_list.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            frame_list,
            width=70,
            height=12,
            font=("Segoe UI", 10)
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            frame_list,
            orient="vertical",
            command=self.listbox.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=scrollbar.set)

        # =====================
        # BOUTONS
        # =====================
        frame_buttons = ttk.Frame(root, padding=10)
        frame_buttons.pack()

        ttk.Button(frame_buttons, text="👁 Afficher", width=15,
                   command=self.afficher_contact).grid(row=0, column=0, padx=5)

        ttk.Button(frame_buttons, text="➕ Ajouter", width=15,
                   command=self.ajouter_contact).grid(row=0, column=1, padx=5)

        ttk.Button(frame_buttons, text="✏️ Modifier", width=15,
                   command=self.modifier_contact).grid(row=0, column=2, padx=5)

        ttk.Button(frame_buttons, text="🗑 Supprimer", width=15,
                   command=self.supprimer_contact).grid(row=0, column=3, padx=5)

        ttk.Button(frame_buttons, text="🔄 Rafraîchir", width=15,
                   command=self.afficher_contacts).grid(row=1, column=1, columnspan=2, pady=5)

        self.afficher_contacts()

    # =====================
    # MÉTHODES
    # =====================
    def afficher_contacts(self):
        self.listbox.delete(0, tk.END)
        for c in self.carnet.lister_contacts():
            self.listbox.insert(
                tk.END,
                f"{c.nom} {c.prenom} | {c.email} | {c.telephone}"
            )

    def afficher_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un contact")
            return

        contact = self.listbox.get(selection[0])
        messagebox.showinfo("Détails du contact", contact)

    def ajouter_contact(self):
        fenetre = tk.Toplevel(self.root)
        fenetre.title("Ajouter un contact")
        fenetre.geometry("330x280")
        fenetre.resizable(False, False)

        frame = ttk.Frame(fenetre, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Prénom").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="Téléphone").grid(row=3, column=0, sticky="w")

        entry_nom = ttk.Entry(frame, width=30)
        entry_prenom = ttk.Entry(frame, width=30)
        entry_email = ttk.Entry(frame, width=30)
        entry_tel = ttk.Entry(frame, width=30)

        entry_nom.grid(row=0, column=1, pady=5)
        entry_prenom.grid(row=1, column=1, pady=5)
        entry_email.grid(row=2, column=1, pady=5)
        entry_tel.grid(row=3, column=1, pady=5)

        def valider():
            nom = entry_nom.get().strip().upper()
            prenom = entry_prenom.get().strip().upper()
            email = entry_email.get().strip()
            tel = entry_tel.get().strip()

            if not nom or not prenom or not email or not tel:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
                return

            if "@" not in email or "." not in email:
                messagebox.showerror(
                    "Email invalide",
                    "L'email doit contenir '@' et '.'"
                )
                return

            if not tel.isdigit() or len(tel) != 10:
                messagebox.showerror(
                    "Téléphone invalide",
                    "Le numéro doit contenir exactement 10 chiffres"
                )
                return

            self.carnet.ajouter_contact(nom, prenom, email, tel)
            self.afficher_contacts()
            fenetre.destroy()

        ttk.Button(frame, text="✅ Valider", command=valider)\
            .grid(row=4, columnspan=2, pady=10)

    def modifier_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un contact")
            return

        ligne = self.listbox.get(selection[0])
        nom_prenom, email, tel = [x.strip() for x in ligne.split("|")]
        nom, prenom = nom_prenom.split(" ", 1)

        fenetre = tk.Toplevel(self.root)
        fenetre.title("Modifier le contact")
        fenetre.geometry("330x240")
        fenetre.resizable(False, False)

        frame = ttk.Frame(fenetre, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Prénom").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text="Téléphone").grid(row=2, column=0, sticky="w")

        entry_nom = ttk.Entry(frame, width=30)
        entry_prenom = ttk.Entry(frame, width=30)
        entry_tel = ttk.Entry(frame, width=30)

        entry_nom.insert(0, nom)
        entry_prenom.insert(0, prenom)
        entry_tel.insert(0, tel)

        entry_nom.grid(row=0, column=1, pady=5)
        entry_prenom.grid(row=1, column=1, pady=5)
        entry_tel.grid(row=2, column=1, pady=5)

        def valider():
            new_nom = entry_nom.get().strip().upper()
            new_prenom = entry_prenom.get().strip().upper()
            new_tel = entry_tel.get().strip()

            if not new_tel.isdigit() or len(new_tel) != 10:
                messagebox.showerror(
                    "Téléphone invalide",
                    "Le numéro doit contenir exactement 10 chiffres"
                )
                return

            self.carnet.modifier_contact(email, new_nom, new_prenom, new_tel)
            self.afficher_contacts()
            fenetre.destroy()

        ttk.Button(frame, text="💾 Enregistrer", command=valider)\
            .grid(row=3, columnspan=2, pady=10)

    def supprimer_contact(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un contact")
            return

        contact = self.listbox.get(selection[0])
        email = contact.split("|")[1].strip()

        confirm = messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer ce contact ?"
        )

        if confirm:
            self.carnet.supprimer_contact(email)
            self.afficher_contacts()
