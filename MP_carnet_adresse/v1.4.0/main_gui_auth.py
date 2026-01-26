import tkinter as tk
from tkinter import messagebox
from address_book import AddressBook
from authentification import Authentification

class FenetreConnexion:
    """Fenêtre de connexion pour les administrateurs"""
    
    def __init__(self, root, auth, callback_success):
        """
        Initialise la fenêtre de connexion
        
        Args:
            root: Fenêtre principale
            auth: Instance de la classe Authentification
            callback_success: Fonction à appeler en cas de connexion réussie
        """
        self.root = root
        self.auth = auth
        self.callback_success = callback_success
        self.admin_connecte = None
        
        self.creer_interface()
    
    def creer_interface(self):
        """Crée l'interface de connexion"""
        # Configuration de la fenêtre
        self.root.title("🔐 Connexion - Carnet d'Adresses")
        self.root.geometry("450x400")
        self.root.configure(bg="#34495e")
        self.root.resizable(False, False)
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame_principal = tk.Frame(self.root, bg="#34495e")
        frame_principal.pack(expand=True)
        
        # Logo / Titre
        label_titre = tk.Label(
            frame_principal,
            text="🔐",
            font=("Arial", 60),
            bg="#34495e",
            fg="white"
        )
        label_titre.pack(pady=20)
        
        label_sous_titre = tk.Label(
            frame_principal,
            text="CONNEXION ADMINISTRATEUR",
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="white"
        )
        label_sous_titre.pack(pady=10)
        
        # Frame pour les champs
        frame_champs = tk.Frame(frame_principal, bg="#34495e")
        frame_champs.pack(pady=20)
        
        # Nom d'utilisateur
        tk.Label(
            frame_champs,
            text="👤 Nom d'utilisateur",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.entry_username = tk.Entry(
            frame_champs,
            font=("Arial", 11),
            width=25,
            bg="white",
            fg="#2c3e50"
        )
        self.entry_username.grid(row=1, column=0, pady=5)
        self.entry_username.focus()
        
        # Mot de passe
        tk.Label(
            frame_champs,
            text="🔑 Mot de passe",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).grid(row=2, column=0, sticky="w", pady=(15, 5))
        
        self.entry_password = tk.Entry(
            frame_champs,
            font=("Arial", 11),
            width=25,
            show="●",
            bg="white",
            fg="#2c3e50"
        )
        self.entry_password.grid(row=3, column=0, pady=5)
        
        # Bouton de connexion
        btn_connexion = tk.Button(
            frame_principal,
            text="🚀 SE CONNECTER",
            command=self.se_connecter,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            cursor="hand2",
            relief=tk.FLAT
        )
        btn_connexion.pack(pady=20)
        
        # Lien pour créer un compte
        btn_creer_compte = tk.Button(
            frame_principal,
            text="➕ Créer un nouveau compte admin",
            command=self.creer_nouveau_compte,
            bg="#34495e",
            fg="#3498db",
            font=("Arial", 9, "underline"),
            border=0,
            cursor="hand2",
            activebackground="#34495e",
            activeforeground="#2980b9"
        )
        btn_creer_compte.pack(pady=5)
        
        # Bind Enter key
        self.entry_password.bind('<Return>', lambda e: self.se_connecter())
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
    
    def se_connecter(self):
        """Gère la connexion"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs !")
            return
        
        if self.auth.verifier_connexion(username, password):
            self.admin_connecte = username
            messagebox.showinfo("Succès", f"Bienvenue {username} ! 🎉")
            self.callback_success(username)
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects !")
            self.entry_password.delete(0, tk.END)
            self.entry_password.focus()
    
    def creer_nouveau_compte(self):
        """Ouvre une fenêtre pour créer un nouveau compte"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Créer un compte admin")
        dialog.geometry("400x350")
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
            text="Créer un nouveau compte",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=20)
        
        # Frame pour les champs
        frame_champs = tk.Frame(dialog, bg="#ecf0f1")
        frame_champs.pack(pady=10, padx=20)
        
        tk.Label(frame_champs, text="Nom d'utilisateur :", font=("Arial", 10), bg="#ecf0f1").grid(row=0, column=0, sticky="w", pady=5)
        entry_new_username = tk.Entry(frame_champs, font=("Arial", 10), width=30)
        entry_new_username.grid(row=0, column=1, pady=5, padx=5)
        entry_new_username.focus()
        
        tk.Label(frame_champs, text="Mot de passe :", font=("Arial", 10), bg="#ecf0f1").grid(row=1, column=0, sticky="w", pady=5)
        entry_new_password = tk.Entry(frame_champs, font=("Arial", 10), width=30, show="●")
        entry_new_password.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_champs, text="Confirmer mot de passe :", font=("Arial", 10), bg="#ecf0f1").grid(row=2, column=0, sticky="w", pady=5)
        entry_confirm_password = tk.Entry(frame_champs, font=("Arial", 10), width=30, show="●")
        entry_confirm_password.grid(row=2, column=1, pady=5, padx=5)
        
        # Note
        tk.Label(
            dialog,
            text="Le mot de passe doit contenir au moins 6 caractères",
            font=("Arial", 9, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack(pady=10)
        
        def valider():
            username = entry_new_username.get().strip()
            password = entry_new_password.get().strip()
            confirm = entry_confirm_password.get().strip()
            
            if not username or not password or not confirm:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires !")
                return
            
            if password != confirm:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas !")
                return
            
            if self.auth.creer_admin(username, password):
                dialog.destroy()
                messagebox.showinfo("Succès", f"Compte '{username}' créé avec succès !")
        
        # Boutons
        frame_boutons = tk.Frame(dialog, bg="#ecf0f1")
        frame_boutons.pack(pady=20)
        
        tk.Button(
            frame_boutons,
            text="✓ Créer",
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


class CarnetAdressesGUI:
    """Interface graphique pour le carnet d'adresses (identique à Partie 3)"""
    
    def __init__(self, root, admin_connecte):
        """
        Initialise l'interface graphique
        
        Args:
            root: Fenêtre principale Tkinter
            admin_connecte: Nom de l'admin connecté
        """
        self.root = root
        self.admin_connecte = admin_connecte
        self.root.title(f"📱 Carnet d'Adresses - Connecté : {admin_connecte}")
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
        
        # Titre avec info admin
        label_titre = tk.Label(
            frame_superieur,
            text=f"📱 CARNET D'ADRESSES\nConnecté en tant que : {self.admin_connecte}",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        label_titre.pack(pady=15)
        
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
        
        # Bouton Déconnexion
        btn_deconnexion = tk.Button(
            frame_boutons,
            text="🚪 Déconnexion",
            command=self.deconnexion,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11, "bold"),
            width=12,
            height=2,
            cursor="hand2"
        )
        btn_deconnexion.grid(row=0, column=4, padx=5, pady=5)
    
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
        
        tk.Label(dialog, text="Nouveau Contact", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        
        frame_champs = tk.Frame(dialog, bg="#ecf0f1")
        frame_champs.pack(pady=10, padx=20)
        
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
        
        frame_boutons = tk.Frame(dialog, bg="#ecf0f1")
        frame_boutons.pack(pady=20)
        
        tk.Button(frame_boutons, text="✓ Valider", command=valider, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12).grid(row=0, column=0, padx=5)
        tk.Button(frame_boutons, text="✗ Annuler", command=dialog.destroy, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=12).grid(row=0, column=1, padx=5)
    
    def afficher_contact(self):
        """Affiche les détails du contact sélectionné"""
        selection = self.listbox_contacts.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contact !")
            return
        
        index = selection[0]
        contacts_tries = sorted(self.carnet.contacts, key=lambda c: (c.nom.lower(), c.prenom.lower()))
        contact = contacts_tries[index]
        
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
        
        index = selection[0]
        contacts_tries = sorted(self.carnet.contacts, key=lambda c: (c.nom.lower(), c.prenom.lower()))
        contact = contacts_tries[index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Modifier un contact")
        dialog.geometry("400x300")
        dialog.configure(bg="#ecf0f1")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text=f"Modifier : {contact.get_nom_complet()}", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        
        frame_champs = tk.Frame(dialog, bg="#ecf0f1")
        frame_champs.pack(pady=10, padx=20)
        
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
                contact.nom, contact.prenom,
                nouveau_nom if nouveau_nom != contact.nom else None,
                nouveau_prenom if nouveau_prenom != contact.prenom else None,
                nouveau_email if nouveau_email != contact.email else None,
                nouveau_telephone if nouveau_telephone != contact.telephone else None
            ):
                self.actualiser_liste()
                dialog.destroy()
                messagebox.showinfo("Succès", "Contact modifié avec succès !")
        
        frame_boutons = tk.Frame(dialog, bg="#ecf0f1")
        frame_boutons.pack(pady=20)
        
        tk.Button(frame_boutons, text="✓ Valider", command=valider, bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=12).grid(row=0, column=0, padx=5)
        tk.Button(frame_boutons, text="✗ Annuler", command=dialog.destroy, bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), width=12).grid(row=0, column=1, padx=5)
    
    def supprimer_contact(self):
        """Supprime le contact sélectionné"""
        selection = self.listbox_contacts.curselection()
        
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un contact à supprimer !")
            return
        
        index = selection[0]
        contacts_tries = sorted(self.carnet.contacts, key=lambda c: (c.nom.lower(), c.prenom.lower()))
        contact = contacts_tries[index]
        
        reponse = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer le contact :\n\n{contact.get_nom_complet()} ?", icon="warning")
        
        if reponse:
            if self.carnet.supprimer_contact(contact.nom, contact.prenom):
                self.actualiser_liste()
                messagebox.showinfo("Succès", "Contact supprimé avec succès !")
    
    def deconnexion(self):
        """Déconnexion et retour à l'écran de connexion"""
        reponse = messagebox.askyesno("Déconnexion", "Êtes-vous sûr de vouloir vous déconnecter ?", icon="question")
        
        if reponse:
            self.root.destroy()
            main()


def main():
    """Fonction principale avec système de connexion"""
    auth = Authentification()
    
    root = tk.Tk()
    
    def ouvrir_application(admin_connecte):
        """Ouvre l'application après connexion réussie"""
        root.destroy()
        
        # Créer une nouvelle fenêtre pour l'application
        app_root = tk.Tk()
        app = CarnetAdressesGUI(app_root, admin_connecte)
        app_root.mainloop()
    
    # Afficher la fenêtre de connexion
    fenetre_connexion = FenetreConnexion(root, auth, ouvrir_application)
    root.mainloop()


if __name__ == "__main__":
    main()