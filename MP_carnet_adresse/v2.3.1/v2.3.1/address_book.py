from contact import Contact
import sqlite3
import re

class AddressBook:
    """Classe gérant un carnet d'adresses avec base de données SQLite et validation stricte"""
    
    def __init__(self, db_name="carnet_adresses.db"):
        """
        Initialise un carnet d'adresses
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.contacts = []
        self.creer_table_contacts()
        self.migrer_schema_si_necessaire()
        self.charger_contacts()
    
    def migrer_schema_si_necessaire(self):
        """
        Migre le schéma de la base de données si nécessaire.
        Convertit l'ancien schéma (avec contrainte UNIQUE sur nom+prenom)
        vers le nouveau schéma (avec contraintes UNIQUE sur email et téléphone).
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            # Vérifier si la table contacts existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
            if not cursor.fetchone():
                conn.close()
                return
            
            # Vérifier le schéma actuel en regardant la définition complète de la table
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contacts'")
            table_sql = cursor.fetchone()[0]
            
            # Vérifier si c'est l'ancien schéma avec UNIQUE(nom, prenom)
            if 'UNIQUE(nom, prenom)' in table_sql or 'UNIQUE (nom, prenom)' in table_sql:
                print("🔄 Migration du schéma de base de données détectée (ancien schéma avec UNIQUE sur nom+prenom)")
                self._recreate_table_with_new_schema(conn, cursor)
            elif 'email TEXT NOT NULL UNIQUE' not in table_sql:
                # Le nouveau schéma doit avoir email UNIQUE
                print("🔄 Migration du schéma de base de données nécessaire (ajout des contraintes UNIQUE)")
                self._recreate_table_with_new_schema(conn, cursor)
                    
        except Exception as e:
            print(f"⚠️ Avertissement lors de la migration: {e}")
        finally:
            conn.close()
    
    def _recreate_table_with_new_schema(self, conn, cursor):
        """Recrée la table avec le nouveau schéma"""
        try:
            # Sauvegarder les données existantes
            cursor.execute("SELECT nom, prenom, email, telephone, adresse, fonction, entreprise, categorie FROM contacts")
            existing_contacts = cursor.fetchall()
            
            # Supprimer l'ancienne table
            cursor.execute("DROP TABLE contacts")
            
            # Créer la nouvelle table avec le schéma correct
            cursor.execute('''
                CREATE TABLE contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    telephone TEXT NOT NULL UNIQUE,
                    adresse TEXT DEFAULT '',
                    fonction TEXT DEFAULT '',
                    entreprise TEXT DEFAULT '',
                    categorie TEXT DEFAULT 'Personnel',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Restaurer les données
            for contact in existing_contacts:
                try:
                    cursor.execute('''
                        INSERT INTO contacts (nom, prenom, email, telephone, adresse, fonction, entreprise, categorie)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', contact)
                except sqlite3.IntegrityError:
                    # Ignorer les doublons
                    pass
            
            conn.commit()
            print(f"✓ Schéma de la base de données migré avec succès ({len(existing_contacts)} contacts)")
        except Exception as e:
            conn.rollback()
            print(f"✗ Erreur lors de la migration: {e}")
    
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
                email TEXT NOT NULL UNIQUE,
                telephone TEXT NOT NULL UNIQUE,
                adresse TEXT DEFAULT '',
                fonction TEXT DEFAULT '',
                entreprise TEXT DEFAULT '',
                categorie TEXT DEFAULT 'Personnel',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table contacts initialisée")
    
    def valider_email(self, email):
        """
        MODIFICATION PROF : Validation stricte de l'email
        L'email doit contenir obligatoirement @ et .
        
        Args:
            email (str): Email à valider
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        # Vérifier la présence de @
        if '@' not in email:
            return (False, "❌ L'email doit contenir le symbole @ !")
        
        # Vérifier la présence de .
        if '.' not in email:
            return (False, "❌ L'email doit contenir un point (.) !")
        
        # Vérifier que @ vient avant .
        at_index = email.index('@')
        dot_index = email.rfind('.')
        
        if at_index >= dot_index:
            return (False, "❌ Format email invalide : @ doit venir avant le point !")
        
        # Vérifier qu'il y a au moins un caractère avant @
        if at_index == 0:
            return (False, "❌ L'email doit avoir au moins un caractère avant @ !")
        
        # Vérifier qu'il y a au moins un caractère entre @ et .
        if dot_index - at_index <= 1:
            return (False, "❌ L'email doit avoir au moins un caractère entre @ et . !")
        
        # Vérifier qu'il y a au moins un caractère après le dernier .
        if dot_index == len(email) - 1:
            return (False, "❌ L'email doit avoir au moins un caractère après le point !")
        
        # Validation avec regex pour plus de sécurité
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return (False, "❌ Format email invalide ! Exemple valide: nom@domaine.com")
        
        return (True, "✓ Email valide")
    
    def valider_telephone(self, telephone):
        """
        MODIFICATION PROF : Validation stricte du téléphone
        Le numéro doit contenir exactement 10 chiffres
        
        Args:
            telephone (str): Téléphone à valider
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        # Extraire uniquement les chiffres
        chiffres = ''.join(filter(str.isdigit, telephone))
        
        # Vérifier qu'il y a exactement 10 chiffres
        if len(chiffres) != 10:
            return (False, f"❌ Le numéro de téléphone doit contenir exactement 10 chiffres ! (Trouvé: {len(chiffres)} chiffres)")
        
        # Vérifier que le numéro commence par 0 (format marocain)
        if not chiffres.startswith('0'):
            return (False, "❌ Le numéro doit commencer par 0 ! Exemple: 0612345678")
        
        return (True, "✓ Téléphone valide")
    
    def ajouter_contact(self, nom, prenom, email, telephone, adresse="", fonction="", entreprise="", categorie="Personnel"):
        """
        Ajoute un nouveau contact au carnet avec validation stricte
        
        Args:
            nom (str): Nom du contact
            prenom (str): Prénom du contact
            email (str): Email du contact
            telephone (str): Téléphone du contact
            adresse (str): Adresse (optionnel)
            fonction (str): Fonction (optionnel)
            entreprise (str): Entreprise (optionnel)
            categorie (str): Catégorie (Personnel, Entreprise, Client, Fournisseur)
            
        Returns:
            bool: True si ajouté, False sinon
        """
        # VALIDATION EMAIL
        email_valide, message_email = self.valider_email(email)
        if not email_valide:
            print(message_email)
            return False, message_email
        
        # VALIDATION TÉLÉPHONE
        tel_valide, message_tel = self.valider_telephone(telephone)
        if not tel_valide:
            print(message_tel)
            return False, message_tel
        
        # Les noms seront automatiquement convertis en majuscules par la classe Contact
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            # Convertir en majuscules avant insertion
            nom_maj = nom.upper()
            prenom_maj = prenom.upper()
            
            cursor.execute(
                """INSERT INTO contacts 
                   (nom, prenom, email, telephone, adresse, fonction, entreprise, categorie) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (nom_maj, prenom_maj, email, telephone, adresse, fonction, entreprise, categorie)
            )
            conn.commit()
            message = f"✓ Contact '{nom_maj} {prenom_maj}' ajouté avec succès!"
            print(message)
            
            # Recharger les contacts
            self.charger_contacts()
            return True, message
        except sqlite3.IntegrityError as e:
            error_msg = str(e).lower()
            if "email" in error_msg:
                message = f"✗ Erreur : L'email '{email}' est déjà utilisé par un autre contact !"
            elif "telephone" in error_msg or "unique" in error_msg:
                message = f"✗ Erreur : Le numéro de téléphone '{telephone}' est déjà utilisé !"
            else:
                message = f"✗ Erreur : Le contact '{nom.upper()} {prenom.upper()}' existe déjà !"
            print(message)
            return False, message
        finally:
            conn.close()
    
    def afficher_contacts(self):
        """Affiche tous les contacts du carnet"""
        if not self.contacts:
            print("\n📭 Le carnet d'adresses est vide.\n")
            return
        
        print("\n" + "="*80)
        print("📇 LISTE DES CONTACTS")
        print("="*80)
        
        # Trier les contacts par catégorie puis par nom
        contacts_tries = sorted(self.contacts, key=lambda c: (c.categorie, c.nom.lower(), c.prenom.lower()))
        
        categorie_actuelle = None
        for i, contact in enumerate(contacts_tries, 1):
            # Afficher l'en-tête de catégorie si changement
            if contact.categorie != categorie_actuelle:
                print(f"\n📂 Catégorie: {contact.categorie}")
                print("-" * 80)
                categorie_actuelle = contact.categorie
            
            print(f"{i}. {contact}")
        
        print("="*80 + "\n")
    
    def rechercher_contact(self, nom, prenom=None):
        """Recherche un contact par son nom et prénom"""
        nom_upper = nom.upper()
        prenom_upper = prenom.upper() if prenom else None
        
        for contact in self.contacts:
            if prenom_upper:
                if contact.nom == nom_upper and contact.prenom == prenom_upper:
                    return contact
            else:
                if contact.nom == nom_upper:
                    return contact
        return None
    
    def supprimer_contact(self, nom, prenom=None):
        """Supprime un contact du carnet"""
        nom_upper = nom.upper()
        prenom_upper = prenom.upper() if prenom else None
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        if prenom_upper:
            cursor.execute(
                "DELETE FROM contacts WHERE nom = ? AND prenom = ?",
                (nom_upper, prenom_upper)
            )
        else:
            cursor.execute(
                "DELETE FROM contacts WHERE nom = ?",
                (nom_upper,)
            )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            message = f"✓ Contact '{nom_upper} {prenom_upper or ''}' supprimé avec succès!"
            print(message)
            self.charger_contacts()
            return True, message
        else:
            conn.close()
            message = f"✗ Contact '{nom_upper} {prenom_upper or ''}' introuvable."
            print(message)
            return False, message
    
    def modifier_contact(self, nom, prenom=None, nouveau_nom=None, nouveau_prenom=None, 
                        nouveau_email=None, nouveau_telephone=None, nouvelle_adresse=None,
                        nouvelle_fonction=None, nouvelle_entreprise=None, nouvelle_categorie=None):
        """Modifie les informations d'un contact avec validation"""
        
        # Valider le nouvel email si fourni (même si vide, pour permettre la validation)
        if nouveau_email is not None and nouveau_email != "":
            email_valide, message = self.valider_email(nouveau_email)
            if not email_valide:
                print(message)
                return False, message
        
        # Valider le nouveau téléphone si fourni (même si vide)
        if nouveau_telephone is not None and nouveau_telephone != "":
            tel_valide, message = self.valider_telephone(nouveau_telephone)
            if not tel_valide:
                print(message)
                return False, message
        
        nom_upper = nom.upper()
        prenom_upper = prenom.upper() if prenom else None
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        # Permettre la modification du nom/prénom uniquement si différent
        if nouveau_nom is not None and nouveau_nom.upper() != nom_upper:
            updates.append("nom = ?")
            params.append(nouveau_nom.upper())
        if nouveau_prenom is not None and prenom_upper and nouveau_prenom.upper() != prenom_upper:
            updates.append("prenom = ?")
            params.append(nouveau_prenom.upper())
        if nouveau_email is not None:
            updates.append("email = ?")
            params.append(nouveau_email)
        if nouveau_telephone is not None:
            updates.append("telephone = ?")
            params.append(nouveau_telephone)
        if nouvelle_adresse is not None:
            updates.append("adresse = ?")
            params.append(nouvelle_adresse)
        if nouvelle_fonction is not None:
            updates.append("fonction = ?")
            params.append(nouvelle_fonction)
        if nouvelle_entreprise is not None:
            updates.append("entreprise = ?")
            params.append(nouvelle_entreprise)
        if nouvelle_categorie is not None:
            updates.append("categorie = ?")
            params.append(nouvelle_categorie)
        
        if not updates:
            conn.close()
            message = "Aucune modification à effectuer."
            print(message)
            return True, message
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        
        params.append(nom_upper)
        if prenom_upper:
            params.append(prenom_upper)
            where_clause = "WHERE nom = ? AND prenom = ?"
        else:
            where_clause = "WHERE nom = ?"
        
        query = f"UPDATE contacts SET {', '.join(updates)} {where_clause}"
        
        try:
            cursor.execute(query, params)
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                message = "✓ Contact modifié avec succès!"
                print(message)
                self.charger_contacts()
                return True, message
            else:
                conn.close()
                message = "✗ Contact introuvable."
                print(message)
                return False, message
        except sqlite3.IntegrityError as e:
            conn.close()
            error_msg = str(e)
            if "email" in error_msg.lower():
                message = "✗ Erreur : Cet email est déjà utilisé par un autre contact !"
            elif "telephone" in error_msg.lower():
                message = "✗ Erreur : Ce numéro de téléphone est déjà utilisé par un autre contact !"
            else:
                message = "✗ Erreur : Une contrainte d'unicité a été violée !"
            print(message)
            return False, message
    
    def nombre_contacts(self):
        """Retourne le nombre total de contacts"""
        return len(self.contacts)
    
    def nombre_contacts_par_categorie(self, categorie):
        """Retourne le nombre de contacts dans une catégorie"""
        return len([c for c in self.contacts if c.categorie == categorie])
    
    def filtrer_par_categorie(self, categorie):
        """Retourne tous les contacts d'une catégorie"""
        return [c for c in self.contacts if c.categorie == categorie]
    
    def charger_contacts(self):
        """Charge les contacts depuis la base de données"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nom, prenom, email, telephone, adresse, fonction, entreprise, categorie 
            FROM contacts 
            ORDER BY nom, prenom
        """)
        rows = cursor.fetchall()
        
        self.contacts = []
        for row in rows:
            contact = Contact(
                row[0], row[1], row[2], row[3],  # nom, prenom, email, tel
                row[4], row[5], row[6], row[7]   # adresse, fonction, entreprise, categorie
            )
            self.contacts.append(contact)
        
        conn.close()
        print(f"✓ {len(self.contacts)} contact(s) chargé(s) depuis la base de données")
    
    def exporter_vers_csv(self, fichier_csv="contacts_export.csv"):
        """Exporte tous les contacts vers un fichier CSV"""
        try:
            import csv
            
            with open(fichier_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Adresse', 
                               'Fonction', 'Entreprise', 'Catégorie'])
                
                for contact in self.contacts:
                    writer.writerow([
                        contact.nom, contact.prenom, contact.email, contact.telephone,
                        contact.adresse, contact.fonction, contact.entreprise, contact.categorie
                    ])
            
            print(f"✓ {len(self.contacts)} contact(s) exporté(s) vers '{fichier_csv}'")
            return True
        except Exception as e:
            print(f"✗ Erreur lors de l'exportation : {e}")
            return False