import sqlite3
import hashlib

class Authentification:
    """Classe gérant l'authentification des administrateurs avec SQLite"""
    
    def __init__(self, db_name="carnet_adresses.db"):
        """
        Initialise le système d'authentification
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.creer_table_admins()
        
        # Créer un admin par défaut si aucun n'existe
        if self.nombre_admins() == 0:
            self.creer_admin("admin", "admin123")
            print("ℹ️  Admin par défaut créé : admin / admin123")
    
    def creer_connexion(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_name)
    
    def creer_table_admins(self):
        """Crée la table admins si elle n'existe pas"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe_hash TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table admins initialisée")
    
    def hasher_mot_de_passe(self, mot_de_passe):
        """
        Hache un mot de passe avec SHA-256
        
        Args:
            mot_de_passe (str): Mot de passe en clair
            
        Returns:
            str: Hash du mot de passe
        """
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()
    
    def creer_admin(self, nom_utilisateur, mot_de_passe):
        """
        Crée un nouveau compte administrateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            
        Returns:
            bool: True si créé, False sinon
        """
        if len(mot_de_passe) < 6:
            print("✗ Le mot de passe doit contenir au moins 6 caractères !")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
            cursor.execute(
                "INSERT INTO admins (nom_utilisateur, mot_de_passe_hash) VALUES (?, ?)",
                (nom_utilisateur, hash_mot_de_passe)
            )
            conn.commit()
            print(f"✓ Administrateur '{nom_utilisateur}' créé avec succès !")
            return True
        except sqlite3.IntegrityError:
            print(f"✗ L'administrateur '{nom_utilisateur}' existe déjà !")
            return False
        finally:
            conn.close()
    
    def verifier_connexion(self, nom_utilisateur, mot_de_passe):
        """
        Vérifie les identifiants de connexion
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            
        Returns:
            bool: True si connexion valide, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
        cursor.execute(
            "SELECT * FROM admins WHERE nom_utilisateur = ? AND mot_de_passe_hash = ?",
            (nom_utilisateur, hash_mot_de_passe)
        )
        
        resultat = cursor.fetchone()
        conn.close()
        
        return resultat is not None
    
    def modifier_mot_de_passe(self, nom_utilisateur, ancien_mdp, nouveau_mdp):
        """
        Modifie le mot de passe d'un admin
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            ancien_mdp (str): Ancien mot de passe
            nouveau_mdp (str): Nouveau mot de passe
            
        Returns:
            bool: True si modifié, False sinon
        """
        if not self.verifier_connexion(nom_utilisateur, ancien_mdp):
            print("✗ Ancien mot de passe incorrect !")
            return False
        
        if len(nouveau_mdp) < 6:
            print("✗ Le nouveau mot de passe doit contenir au moins 6 caractères !")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        hash_nouveau_mdp = self.hasher_mot_de_passe(nouveau_mdp)
        cursor.execute(
            "UPDATE admins SET mot_de_passe_hash = ? WHERE nom_utilisateur = ?",
            (hash_nouveau_mdp, nom_utilisateur)
        )
        
        conn.commit()
        conn.close()
        print(f"✓ Mot de passe de '{nom_utilisateur}' modifié avec succès !")
        return True
    
    def supprimer_admin(self, nom_utilisateur):
        """
        Supprime un compte administrateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            
        Returns:
            bool: True si supprimé, False sinon
        """
        if self.nombre_admins() == 1:
            print("✗ Impossible de supprimer le dernier administrateur !")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM admins WHERE nom_utilisateur = ?", (nom_utilisateur,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            print(f"✓ Administrateur '{nom_utilisateur}' supprimé avec succès !")
            return True
        else:
            conn.close()
            print(f"✗ L'administrateur '{nom_utilisateur}' n'existe pas !")
            return False
    
    def lister_admins(self):
        """
        Retourne la liste des noms d'utilisateurs
        
        Returns:
            list: Liste des admins
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nom_utilisateur FROM admins ORDER BY nom_utilisateur")
        admins = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return admins
    
    def nombre_admins(self):
        """Retourne le nombre d'administrateurs"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM admins")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count