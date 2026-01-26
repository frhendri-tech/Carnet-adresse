from contact import Contact
import json
import os
import re

class AddressBook:
    """Classe gérant un carnet d'adresses avec sauvegarde dans un fichier JSON"""
    
    def __init__(self, fichier="contacts.json"):
        """
        Initialise un carnet d'adresses
        
        Args:
            fichier (str): Nom du fichier de sauvegarde
        """
        self.contacts = []
        self.fichier = fichier
        self.charger_contacts()
    
    def valider_email(self, email):
        """
        Valide le format d'un email
        
        Args:
            email (str): Email à valider
            
        Returns:
            bool: True si valide, False sinon
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def valider_telephone(self, telephone):
        """
        Valide le format d'un numéro de téléphone
        
        Args:
            telephone (str): Téléphone à valider
            
        Returns:
            bool: True si valide, False sinon
        """
        # Accepte différents formats: +212612345678, 0612345678, 06-12-34-56-78, etc.
        pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
        return re.match(pattern, telephone) is not None
    
    def contact_existe(self, nom, prenom):
        """
        Vérifie si un contact existe déjà
        
        Args:
            nom (str): Nom du contact
            prenom (str): Prénom du contact
            
        Returns:
            bool: True si existe, False sinon
        """
        for contact in self.contacts:
            if contact.nom.lower() == nom.lower() and contact.prenom.lower() == prenom.lower():
                return True
        return False
    
    def ajouter_contact(self, nom, prenom, email, telephone):
        """
        Ajoute un nouveau contact au carnet avec validation
        
        Args:
            nom (str): Nom du contact
            prenom (str): Prénom du contact
            email (str): Email du contact
            telephone (str): Téléphone du contact
            
        Returns:
            bool: True si ajouté, False sinon
        """
        # Vérifier les doublons
        if self.contact_existe(nom, prenom):
            print(f"✗ Erreur : Le contact '{nom} {prenom}' existe déjà !")
            return False
        
        # Valider l'email
        if not self.valider_email(email):
            print(f"✗ Erreur : L'email '{email}' n'est pas valide !")
            return False
        
        # Valider le téléphone
        if not self.valider_telephone(telephone):
            print(f"✗ Erreur : Le téléphone '{telephone}' n'est pas valide !")
            return False
        
        # Ajouter le contact
        nouveau_contact = Contact(nom, prenom, email, telephone)
        self.contacts.append(nouveau_contact)
        self.sauvegarder_contacts()
        print(f"✓ Contact '{nom} {prenom}' ajouté avec succès!")
        return True
    
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
            self.sauvegarder_contacts()
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
            # Valider le nouvel email si fourni
            if nouveau_email and not self.valider_email(nouveau_email):
                print(f"✗ Erreur : L'email '{nouveau_email}' n'est pas valide !")
                return False
            
            # Valider le nouveau téléphone si fourni
            if nouveau_telephone and not self.valider_telephone(nouveau_telephone):
                print(f"✗ Erreur : Le téléphone '{nouveau_telephone}' n'est pas valide !")
                return False
            
            # Appliquer les modifications
            if nouveau_nom:
                contact.nom = nouveau_nom
            if nouveau_prenom:
                contact.prenom = nouveau_prenom
            if nouveau_email:
                contact.email = nouveau_email
            if nouveau_telephone:
                contact.telephone = nouveau_telephone
            
            self.sauvegarder_contacts()
            print(f"✓ Contact modifié avec succès!")
            return True
        else:
            print(f"✗ Contact introuvable.")
            return False
    
    def nombre_contacts(self):
        """Retourne le nombre total de contacts"""
        return len(self.contacts)
    
    def sauvegarder_contacts(self):
        """Sauvegarde tous les contacts dans le fichier JSON"""
        try:
            data = [contact.to_dict() for contact in self.contacts]
            with open(self.fichier, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde : {e}")
    
    def charger_contacts(self):
        """Charge les contacts depuis le fichier JSON"""
        if os.path.exists(self.fichier):
            try:
                with open(self.fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.contacts = []
                    for item in data:
                        contact = Contact(
                            item['nom'],
                            item['prenom'],
                            item['email'],
                            item['telephone']
                        )
                        self.contacts.append(contact)
                print(f"✓ {len(self.contacts)} contact(s) chargé(s) depuis '{self.fichier}'")
            except Exception as e:
                print(f"✗ Erreur lors du chargement : {e}")
                self.contacts = []
        else:
            print(f"ℹ️  Aucun fichier de contacts trouvé. Un nouveau sera créé.")