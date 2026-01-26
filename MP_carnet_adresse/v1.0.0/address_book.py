from contact import Contact

class AddressBook:
    """Classe gérant un carnet d'adresses"""
    
    def __init__(self):
        """Initialise un carnet d'adresses vide"""
        self.contacts = []
    
    def ajouter_contact(self, nom, prenom, email, telephone):
        """
        Ajoute un nouveau contact au carnet
        
        Args:
            nom (str): Nom du contact
            prenom (str): Prénom du contact
            email (str): Email du contact
            telephone (str): Téléphone du contact
        """
        nouveau_contact = Contact(nom, prenom, email, telephone)
        self.contacts.append(nouveau_contact)
        print(f"✓ Contact '{nom} {prenom}' ajouté avec succès!")
    
    def afficher_contacts(self):
        """Affiche tous les contacts du carnet"""
        if not self.contacts:
            print("\n📭 Le carnet d'adresses est vide.\n")
            return
        
        print("\n" + "="*60)
        print("📇 LISTE DES CONTACTS")
        print("="*60)
        
        # Trier les contacts par nom puis prénom
        contacts_tries = sorted(self.contacts, key=lambda c: (c.nom.lower(), c.prenom.lower()))
        
        for i, contact in enumerate(contacts_tries, 1):
            print(f"{i}. {contact}")
        
        print("="*60 + "\n")
    
    def rechercher_contact(self, nom, prenom=None):
        """
        Recherche un contact par son nom et prénom
        
        Args:
            nom (str): Nom du contact à rechercher
            prenom (str): Prénom du contact (optionnel)
            
        Returns:
            Contact: Le contact trouvé ou None
        """
        for contact in self.contacts:
            if prenom:
                if contact.nom.lower() == nom.lower() and contact.prenom.lower() == prenom.lower():
                    return contact
            else:
                if contact.nom.lower() == nom.lower():
                    return contact
        return None
    
    def supprimer_contact(self, nom, prenom=None):
        """
        Supprime un contact du carnet
        
        Args:
            nom (str): Nom du contact à supprimer
            prenom (str): Prénom du contact (optionnel)
            
        Returns:
            bool: True si supprimé, False sinon
        """
        contact = self.rechercher_contact(nom, prenom)
        if contact:
            self.contacts.remove(contact)
            print(f"✓ Contact '{contact.get_nom_complet()}' supprimé avec succès!")
            return True
        else:
            print(f"✗ Contact introuvable.")
            return False
    
    def modifier_contact(self, nom, prenom=None, nouveau_nom=None, nouveau_prenom=None, nouveau_email=None, nouveau_telephone=None):
        """
        Modifie les informations d'un contact
        
        Args:
            nom (str): Nom du contact à modifier
            prenom (str): Prénom du contact
            nouveau_nom (str): Nouveau nom (optionnel)
            nouveau_prenom (str): Nouveau prénom (optionnel)
            nouveau_email (str): Nouvel email (optionnel)
            nouveau_telephone (str): Nouveau téléphone (optionnel)
            
        Returns:
            bool: True si modifié, False sinon
        """
        contact = self.rechercher_contact(nom, prenom)
        if contact:
            if nouveau_nom:
                contact.nom = nouveau_nom
            if nouveau_prenom:
                contact.prenom = nouveau_prenom
            if nouveau_email:
                contact.email = nouveau_email
            if nouveau_telephone:
                contact.telephone = nouveau_telephone
            print(f"✓ Contact modifié avec succès!")
            return True
        else:
            print(f"✗ Contact introuvable.")
            return False
    
    def nombre_contacts(self):
        """Retourne le nombre total de contacts"""
        return len(self.contacts)