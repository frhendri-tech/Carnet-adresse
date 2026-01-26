from contact import Contact
import sqlite3
import re

class AddressBook:
    """Classe gérant un carnet d'adresses avec base de données SQLite"""
    
    def __init__(self, db_name="carnet_adresses.db"):
        """
        Initialise un carnet d'adresses
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.contacts = []
        self.creer_table_contacts()
        self.charger_contacts()
    
    def creer_connexion(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_name)
    
    def creer_table_contacts(self):
        """Crée la table contacts si elle n'existe pas"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT NOT NULL,
                telephone TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nom, prenom)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table contacts initialisée")
    
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
        pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
        return re.match(pattern, telephone) is not None
    
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
        # Valider l'email
        if not self.valider_email(email):
            print(f"✗ Erreur : L'email '{email}' n'est pas valide !")
            return False
        
        # Valider le téléphone
        if not self.valider_telephone(telephone):
            print(f"✗ Erreur : Le téléphone '{telephone}' n'est pas valide !")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO contacts (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)",
                (nom, prenom, email, telephone)
            )
            conn.commit()
            print(f"✓ Contact '{nom} {prenom}' ajouté avec succès!")
            
            # Recharger les contacts
            self.charger_contacts()
            return True
        except sqlite3.IntegrityError:
            print(f"✗ Erreur : Le contact '{nom} {prenom}' existe déjà !")
            return False
        finally:
            conn.close()
    
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
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        if prenom:
            cursor.execute(
                "DELETE FROM contacts WHERE nom = ? AND prenom = ?",
                (nom, prenom)
            )
        else:
            cursor.execute(
                "DELETE FROM contacts WHERE nom = ?",
                (nom,)
            )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            print(f"✓ Contact supprimé avec succès!")
            
            # Recharger les contacts
            self.charger_contacts()
            return True
        else:
            conn.close()
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
        # Valider le nouvel email si fourni
        if nouveau_email and not self.valider_email(nouveau_email):
            print(f"✗ Erreur : L'email '{nouveau_email}' n'est pas valide !")
            return False
        
        # Valider le nouveau téléphone si fourni
        if nouveau_telephone and not self.valider_telephone(nouveau_telephone):
            print(f"✗ Erreur : Le téléphone '{nouveau_telephone}' n'est pas valide !")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        # Construire la requête de mise à jour
        updates = []
        params = []
        
        if nouveau_nom:
            updates.append("nom = ?")
            params.append(nouveau_nom)
        if nouveau_prenom:
            updates.append("prenom = ?")
            params.append(nouveau_prenom)
        if nouveau_email:
            updates.append("email = ?")
            params.append(nouveau_email)
        if nouveau_telephone:
            updates.append("telephone = ?")
            params.append(nouveau_telephone)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        
        # Ajouter les conditions WHERE
        params.append(nom)
        if prenom:
            params.append(prenom)
            where_clause = "WHERE nom = ? AND prenom = ?"
        else:
            where_clause = "WHERE nom = ?"
        
        query = f"UPDATE contacts SET {', '.join(updates)} {where_clause}"
        
        try:
            cursor.execute(query, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✓ Contact modifié avec succès!")
                
                # Recharger les contacts
                self.charger_contacts()
                return True
            else:
                conn.close()
                print(f"✗ Contact introuvable.")
                return False
        except sqlite3.IntegrityError:
            conn.close()
            print(f"✗ Erreur : Un contact avec ce nom existe déjà !")
            return False
    
    def nombre_contacts(self):
        """Retourne le nombre total de contacts"""
        return len(self.contacts)
    
    def charger_contacts(self):
        """Charge les contacts depuis la base de données"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nom, prenom, email, telephone FROM contacts ORDER BY nom, prenom")
        rows = cursor.fetchall()
        
        self.contacts = []
        for row in rows:
            contact = Contact(row[0], row[1], row[2], row[3])
            self.contacts.append(contact)
        
        conn.close()
        print(f"✓ {len(self.contacts)} contact(s) chargé(s) depuis la base de données")
    
    def exporter_vers_csv(self, fichier_csv="contacts_export.csv"):
        """
        Exporte tous les contacts vers un fichier CSV
        
        Args:
            fichier_csv (str): Nom du fichier CSV
            
        Returns:
            bool: True si exporté, False sinon
        """
        try:
            import csv
            
            with open(fichier_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone'])
                
                for contact in self.contacts:
                    writer.writerow([contact.nom, contact.prenom, contact.email, contact.telephone])
            
            print(f"✓ {len(self.contacts)} contact(s) exporté(s) vers '{fichier_csv}'")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de l'exportation : {e}")
            return False
    
    def importer_depuis_csv(self, fichier_csv):
        """
        Importe des contacts depuis un fichier CSV
        
        Args:
            fichier_csv (str): Nom du fichier CSV
            
        Returns:
            int: Nombre de contacts importés
        """
        try:
            import csv
            count = 0
            
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if self.ajouter_contact(
                        row['Nom'].strip(),
                        row['Prénom'].strip(),
                        row['Email'].strip(),
                        row['Téléphone'].strip()
                    ):
                        count += 1
            
            print(f"✓ {count} contact(s) importé(s) depuis '{fichier_csv}'")
            return count
        except Exception as e:
            print(f"✗ Erreur lors de l'importation : {e}")
            return 0