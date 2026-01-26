import tkinter as tk
from tkinter import messagebox, simpledialog
from address_book import AddressBook

class CarnetAdressesGUI:
    """Interface graphique pour le carnet d'adresses"""
    
    def __init__(self, root):
        """
        Initialise l'interface graphique
        
        Args:
            root: Fenêtre principale Tkinter
        """
        self.root = root
        self.root.title("📱 Carnet d'Adresses")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialiser le carnet d'adresses
        self.carnet = AddressBook()
        
        # Créer l'interface
        self.creer_interface()
        
        # Charger les contacts initiaux
        self.actualiser_liste()
    
    def creer_interface(self):
        """Crée tous les éléments de l'interface"""
        
        # ==================== ZONE SUPÉRIEURE ====================
        frame_superieur = tk.Frame(self.root, bg="#2c3e50", height=80)
        frame_superieur.pack(fill=tk.X, padx=10, pady=10)
        frame_superieur.pack_propagate(False)
        
        # Titre
        label_titre = tk.Label(
            frame_superieur,
            text="📱 CARNET D'ADRESSES",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        label_titre.pack(pady=20)
        
        # ==================== ZONE MÉDIANE ====================
        frame_median = tk.Frame(self.root, bg="#ecf0f1")
        frame_median.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Label pour la liste
        label_liste = tk.Label(
            frame_median,
            text="📋 Liste des contacts (par ordre alphabétique)",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        label_liste.pack(pady=(10, 5))
        
        # Frame pour la Listbox et la Scrollbar
        frame_listbox = tk.Frame(frame_median, bg="#ecf0f1")
        frame_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox pour afficher les contacts
        self.listbox_contacts = tk.Listbox(
            frame_listbox,
            font=("Courier New", 11),
            bg="white",
            fg="#2c3e50",
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.listbox_contacts.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_contacts.yview)
        
        # Compteur de contacts
        self.label_compteur = tk.Label(
            frame_median,
            text="Total : 0 contact(s)",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        self.label_compteur.pack(pady=5)
        
        # ==================== ZONE INFÉRIEURE ====================
        frame_inferieur = tk.Frame(self.root, bg="#ecf0f1", height=120)
        frame_inferieur.pack(fill=tk.X, padx=10, pady=10)
        frame_inferieur.pack_propagate(False)
        
        # Label pour les boutons
        label_actions = tk.Label(
            frame_inferieur,
            text="⚙️ Actions",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        label_actions.pack(pady=(5, 10))
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(frame_inferieur, bg="#ecf0f1")
        frame_boutons.pack()
        
        # Bouton Ajouter
        btn_ajouter = tk.Button(
            frame_boutons,
            text="➕ Ajouter",
            command=self.ajouter_contact,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_ajouter.grid(row=0, column=0, padx=5, pady=5)
        
        # Bouton Afficher
        btn_afficher = tk.Button(
            frame_boutons,
            text="👁️ Afficher",
            command=self.afficher_contact,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_afficher.grid(row=0, column=1, padx=5, pady=5)
        
        # Bouton Modifier
        btn_modifier = tk.Button(
            frame_boutons,
            text="✏️ Modifier",
            command=self.modifier_contact,
            bg="#f39c12",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_modifier.grid(row=0, column=2, padx=5, pady=5)
        
        # Bouton Supprimer
        btn_supprimer = tk.Button(
            frame_boutons,
            text="🗑️ Supprimer",
            command=self.supprimer_contact,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_supprimer.grid(row=0, column=3, padx=5, pady=5)
        
        # Bouton Quitter
        btn_quitter = tk.Button(
            frame_boutons,
            text="❌ Quitter",
            command=self.quitter,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_quitter.grid(row=0, column=4, padx=5, pady=5)
    
    def actualiser_liste(self):
        """Actualise la liste des contacts affichés"""
        # Vider la listbox
        self.listbox_contacts.delete(0, tk.END)
        
        # Trier les contacts par ordre alphabétique
        contacts_tries = sorted(
            self.carnet.contacts,
            key=lambda c: (c.nom.lower(), c.prenom.lower())
        )
        
        # Ajouter les contacts à la listbox
        for contact in contacts_tries:
            texte = f"{contact.nom} {contact.prenom:<15} | {contact.email:<30} | {contact.telephone}"
            self.listbox_contacts.insert(tk.END, texte)
        
        # Mettre à jour le compteur
        self.label_compteur.config(text=f"Total : {self.carnet.nombre_contacts()} contact(s)")
    
    def ajouter_contact(self):
        """Ouvre une fenêtre pour ajouter un contact"""
        # Créer une fenêtre de dialogue
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Ajouter un contact")
        dialog.geometry("400x300")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text="Nouveau Contact",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Frame pour les champs
        frame_champs = tk.Frame(dialog, bg="#ecf0f1")
        frame_champs.pack(pady=10, padx=20)
        
        # Champs de saisie
        tk.Label(frame_champs, text="Nom :", font=("Arial", 10), bg="#ecf0f1").grid(row=0, column=0, sticky="w", pady=5)
        entry_nom = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_nom.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Prénom :", font=("Arial", 10), bg="#ecf0f1").grid(row=1, column=0, sticky="w", pady=5)
        entry_prenom = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_prenom.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Email :", font=("Arial", 10), bg="#ecf0f1").grid(row=2, column=0, sticky="w", pady=5)
        entry_email = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_email.grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Téléphone :", font=("Arial", 10), bg="#ecf0f1").grid(row=3, column=0, sticky="w", pady=5)
        entry_telephone = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_telephone.grid(row=3, column=1, pady=5, padx=5)
        
        # Focus sur le premier champ
        entry_nom.focus()
        
        def valider():
            nom = entry_nom.get().strip()
            prenom = entry_prenom.get().strip()
            email = entry_email.get().strip()
            telephone = entry_telephone.get().strip()
            
            if not (nom and prenom and email and telephone):
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires !")
                return
            
            if self.carnet.ajouter_contact(nom, prenom, email, telephone):
                self.actualiser_liste()
                dialog.destroy()
                messagebox.showinfo("Succès", f"Contact '{nom} {prenom}' ajouté avec succès !")
        
        # Boutons
        frame_boutons = tk.Frame(dialog, bg="#ecf0f1")
        frame_boutons.pack(pady=20)
        
        tk.Button(
            frame_boutons,
            text="✓ Valider",
            command=valider,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            frame_boutons,
            text="✗ Annuler",
            command=dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        ).grid(row=0, column=1, padx=5)
    
    def afficher_contact(self):
        """Affiche les détails du contact sélectionné"""
        selection = self.listbox_contacts.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contact !")
            return
        
        # Récupérer le contact sélectionné
        index = selection[0]
        contacts_tries = sorted(
            self.carnet.contacts,
            key=lambda c: (c.nom.lower(), c.prenom.lower())
        )
        contact = contacts_tries[index]
        
        # Afficher les détails
        details = f"""
📋 DÉTAILS DU CONTACT

Nom complet : {contact.get_nom_complet()}
Email       : {contact.email}
Téléphone   : {contact.telephone}
        """
        
        messagebox.showinfo("Détails du contact", details)
    
    def modifier_contact(self):
        """Modifie le contact sélectionné"""
        selection = self.listbox_contacts.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contact à modifier !")
            return
        
        # Récupérer le contact sélectionné
        index = selection[0]
        contacts_tries = sorted(
            self.carnet.contacts,
            key=lambda c: (c.nom.lower(), c.prenom.lower())
        )
        contact = contacts_tries[index]
        
        # Créer une fenêtre de dialogue
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Modifier un contact")
        dialog.geometry("400x300")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Titre
        tk.Label(
            dialog,
            text=f"Modifier : {contact.get_nom_complet()}",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=10)
        
        # Frame pour les champs
        frame_champs = tk.Frame(dialog, bg="#ecf0f1")
        frame_champs.pack(pady=10, padx=20)
        
        # Champs de saisie pré-remplis
        tk.Label(frame_champs, text="Nom :", font=("Arial", 10), bg="#ecf0f1").grid(row=0, column=0, sticky="w", pady=5)
        entry_nom = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_nom.insert(0, contact.nom)
        entry_nom.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Prénom :", font=("Arial", 10), bg="#ecf0f1").grid(row=1, column=0, sticky="w", pady=5)
        entry_prenom = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_prenom.insert(0, contact.prenom)
        entry_prenom.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Email :", font=("Arial", 10), bg="#ecf0f1").grid(row=2, column=0, sticky="w", pady=5)
        entry_email = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_email.insert(0, contact.email)
        entry_email.grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Téléphone :", font=("Arial", 10), bg="#ecf0f1").grid(row=3, column=0, sticky="w", pady=5)
        entry_telephone = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_telephone.insert(0, contact.telephone)
        entry_telephone.grid(row=3, column=1, pady=5, padx=5)
        
        def valider():
            nouveau_nom = entry_nom.get().strip()
            nouveau_prenom = entry_prenom.get().strip()
            nouveau_email = entry_email.get().strip()
            nouveau_telephone = entry_telephone.get().strip()
            
            if self.carnet.modifier_contact(
                contact.nom,
                contact.prenom,
                nouveau_nom if nouveau_nom != contact.nom else None,
                nouveau_prenom if nouveau_prenom != contact.prenom else None,
                nouveau_email if nouveau_email != contact.email else None,
                nouveau_telephone if nouveau_telephone != contact.telephone else None
            ):
                self.actualiser_liste()
                dialog.destroy()
                messagebox.showinfo("Succès", "Contact modifié avec succès !")
        
        # Boutons
        frame_boutons = tk.Frame(dialog, bg="#ecf0f1")
        frame_boutons.pack(pady=20)
        
        tk.Button(
            frame_boutons,
            text="✓ Valider",
            command=valider,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        ).grid(row=0, column=0, padx=5)
        
        tk.Button(
            frame_boutons,
            text="✗ Annuler",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12
        ).grid(row=0, column=1, padx=5)
    
    def supprimer_contact(self):
        """Supprime le contact sélectionné"""
        selection = self.listbox_contacts.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contact à supprimer !")
            return
        
        # Récupérer le contact sélectionné
        index = selection[0]
        contacts_tries = sorted(
            self.carnet.contacts,
            key=lambda c: (c.nom.lower(), c.prenom.lower())
        )
        contact = contacts_tries[index]
        
        # Demander confirmation
        reponse = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le contact :\n\n{contact.get_nom_complet()} ?",
            icon="warning"
        )
        
        if reponse:
            if self.carnet.supprimer_contact(contact.nom, contact.prenom):
                self.actualiser_liste()
                messagebox.showinfo("Succès", "Contact supprimé avec succès !")
    
    def quitter(self):
        """Ferme l'application"""
        reponse = messagebox.askyesno(
            "Quitter",
            "Êtes-vous sûr de vouloir quitter l'application ?",
            icon="question"
        )
        
        if reponse:
            self.root.quit()


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = CarnetAdressesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()