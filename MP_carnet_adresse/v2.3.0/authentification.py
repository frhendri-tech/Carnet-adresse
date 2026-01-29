import sqlite3
import hashlib

class Authentification:
    """Classe gérant l'authentification avec rôles (Super-Admin et Admin)"""
    
    ROLE_SUPER_ADMIN = "super_admin"  # Directeur
    ROLE_ADMIN = "admin"               # Responsable de service
    
    def __init__(self, db_name="polyclinique.db"):
        """
        Initialise le système d'authentification
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.creer_table_admins()
        
        # Créer un super-admin par défaut si aucun n'existe
        if self.nombre_admins() == 0:
            self.creer_admin("directeur", "directeur123", self.ROLE_SUPER_ADMIN)
            print("ℹ️  Super-Admin créé : directeur / directeur123")
    
    def creer_connexion(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_name)
    
    def creer_table_admins(self):
        """Crée la table admins avec rôles"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                service_id INTEGER,
                actif INTEGER DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table admins initialisée")
    
    def hasher_mot_de_passe(self, mot_de_passe):
        """Hache un mot de passe avec SHA-256"""
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()
    
    def creer_admin(self, nom_utilisateur, mot_de_passe, role=ROLE_ADMIN, service_id=None):
        """
        Crée un nouveau compte administrateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            role (str): super_admin ou admin
            service_id (int): ID du service (pour admin seulement)
            
        Returns:
            bool: True si créé, False sinon
        """
        if len(mot_de_passe) < 6:
            print("✗ Le mot de passe doit contenir au moins 6 caractères !")
            return False
        
        if role not in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN]:
            print(f"✗ Rôle invalide ! Utilisez '{self.ROLE_SUPER_ADMIN}' ou '{self.ROLE_ADMIN}'")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
            cursor.execute(
                "INSERT INTO admins (nom_utilisateur, mot_de_passe_hash, role, service_id) VALUES (?, ?, ?, ?)",
                (nom_utilisateur, hash_mot_de_passe, role, service_id)
            )
            conn.commit()
            
            role_fr = "Super-Administrateur" if role == self.ROLE_SUPER_ADMIN else "Administrateur"
            print(f"✓ {role_fr} '{nom_utilisateur}' créé avec succès !")
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
            dict or None: Infos de l'admin si connexion valide, None sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
        cursor.execute(
            "SELECT id, nom_utilisateur, role, service_id, actif FROM admins WHERE nom_utilisateur = ? AND mot_de_passe_hash = ?",
            (nom_utilisateur, hash_mot_de_passe)
        )
        
        resultat = cursor.fetchone()
        conn.close()
        
        if resultat and resultat[4] == 1:  # Vérifier que le compte est actif
            return {
                'id': resultat[0],
                'nom_utilisateur': resultat[1],
                'role': resultat[2],
                'service_id': resultat[3],
                'actif': resultat[4]
            }
        return None
    
    def est_super_admin(self, admin_info):
        """Vérifie si l'utilisateur est super-admin"""
        return admin_info and admin_info.get('role') == self.ROLE_SUPER_ADMIN
    
    def est_admin(self, admin_info):
        """Vérifie si l'utilisateur est admin (responsable de service)"""
        return admin_info and admin_info.get('role') == self.ROLE_ADMIN
    
    def obtenir_service_admin(self, admin_id):
        """Retourne l'ID du service géré par l'admin"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT service_id FROM admins WHERE id = ?", (admin_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def modifier_mot_de_passe(self, nom_utilisateur, ancien_mdp, nouveau_mdp):
        """Modifie le mot de passe d'un admin"""
        admin_info = self.verifier_connexion(nom_utilisateur, ancien_mdp)
        if not admin_info:
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
    
    def attribuer_service(self, admin_id, service_id):
        """Attribue un service à un admin"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE admins SET service_id = ? WHERE id = ?",
            (service_id, admin_id)
        )
        
        conn.commit()
        conn.close()
        print(f"✓ Service attribué à l'administrateur")
        return True
    
    def desactiver_admin(self, admin_id):
        """Désactive un compte admin"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE admins SET actif = 0 WHERE id = ?", (admin_id,))
        conn.commit()
        conn.close()
    
    def activer_admin(self, admin_id):
        """Active un compte admin"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE admins SET actif = 1 WHERE id = ?", (admin_id,))
        conn.commit()
        conn.close()
    
    def lister_admins(self):
        """Retourne la liste de tous les admins"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.nom_utilisateur, a.role, a.service_id, s.nom, a.actif
            FROM admins a
            LEFT JOIN services s ON a.service_id = s.id
            ORDER BY a.role DESC, a.nom_utilisateur
        """)
        
        admins = []
        for row in cursor.fetchall():
            admins.append({
                'id': row[0],
                'nom_utilisateur': row[1],
                'role': row[2],
                'service_id': row[3],
                'service_nom': row[4],
                'actif': row[5]
            })
        
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