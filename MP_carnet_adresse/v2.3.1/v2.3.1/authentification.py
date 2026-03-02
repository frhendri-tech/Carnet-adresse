import sqlite3
import hashlib

class Authentification:
    """Classe gérant l'authentification avec rôles (Super-Admin, Admin et User)"""
    
    ROLE_SUPER_ADMIN = "super_admin"  # Directeur - peut tout faire
    ROLE_ADMIN = "admin"               # Responsable de service - peut créer des users
    ROLE_USER = "user"                 # Utilisateur standard - lecture seule
    
    # Mapping pour l'affichage
    ROLE_DISPLAY = {
        ROLE_SUPER_ADMIN: "Directeur",
        ROLE_ADMIN: "Responsable",
        ROLE_USER: "Utilisateur"
    }
    
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
                role TEXT NOT NULL DEFAULT 'user',
                service_id INTEGER,
                email TEXT UNIQUE,
                contact_id INTEGER,
                actif INTEGER DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table admins initialisée")
        
        # Migrer pour ajouter les nouvelles colonnes si elles n'existent pas
        self._migrer_table_admins()
    
    def _migrer_table_admins(self):
        """Ajoute les colonnes email et contact_id si elles n'existent pas"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("PRAGMA table_info(admins)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'email' not in columns:
                cursor.execute("ALTER TABLE admins ADD COLUMN email TEXT UNIQUE")
                print("✓ Colonne email ajoutée à la table admins")
            
            if 'contact_id' not in columns:
                cursor.execute("ALTER TABLE admins ADD COLUMN contact_id INTEGER")
                print("✓ Colonne contact_id ajoutée à la table admins")
            
            conn.commit()
        except Exception as e:
            print(f"⚠️ Note: {e}")
        finally:
            conn.close()
    
    def hasher_mot_de_passe(self, mot_de_passe):
        """Hache un mot de passe avec SHA-256"""
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()
    
    def creer_admin(self, nom_utilisateur, mot_de_passe, role=ROLE_USER, service_id=None, email=None, contact_id=None):
        """
        Crée un nouveau compte utilisateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            role (str): super_admin, admin, ou user
            service_id (int): ID du service (pour admin seulement)
            email (str): Email de l'utilisateur
            contact_id (int): ID du contact associé (pour les patients)
            
        Returns:
            bool: True si créé, False sinon
        """
        if len(mot_de_passe) < 6:
            print("✗ Le mot de passe doit contenir au moins 6 caractères !")
            return False
        
        if role not in [self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN, self.ROLE_USER]:
            print(f"✗ Rôle invalide ! Utilisez '{self.ROLE_SUPER_ADMIN}', '{self.ROLE_ADMIN}' ou '{self.ROLE_USER}'")
            return False
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
            cursor.execute(
                """INSERT INTO admins (nom_utilisateur, mot_de_passe_hash, role, service_id, email, contact_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (nom_utilisateur, hash_mot_de_passe, role, service_id, email, contact_id)
            )
            conn.commit()
            
            role_fr = self.ROLE_DISPLAY.get(role, role)
            print(f"✓ {role_fr} '{nom_utilisateur}' créé avec succès !")
            return True
        except sqlite3.IntegrityError as e:
            error_msg = str(e).lower()
            if 'email' in error_msg:
                print(f"✗ L'email '{email}' est déjà utilisé !")
            else:
                print(f"✗ L'utilisateur '{nom_utilisateur}' existe déjà !")
            return False
        finally:
            conn.close()
    
    def creer_compte_patient(self, nom_utilisateur, mot_de_passe, email):
        """
        Crée un compte patient (user) lié à un contact existant
        Vérifie d'abord que l'email existe dans la table contacts
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            email (str): Email (doit exister dans contacts)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Vérifier que l'email existe dans contacts
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, prenom FROM contacts WHERE email = ?", (email,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return (False, "Cet email n'existe pas dans notre base de patients. Veuillez contacter l'administration.")
        
        contact_id, nom, prenom = contact
        
        # Créer le compte user lié au contact
        success = self.creer_admin(
            nom_utilisateur=nom_utilisateur,
            mot_de_passe=mot_de_passe,
            role=self.ROLE_USER,
            email=email,
            contact_id=contact_id
        )
        
        if success:
            return (True, f"Compte créé avec succès pour {nom} {prenom}!")
        else:
            return (False, "Impossible de créer le compte. Le nom d'utilisateur ou l'email existe déjà.")
    
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
            "SELECT id, nom_utilisateur, role, service_id, actif, email FROM admins WHERE nom_utilisateur = ? AND mot_de_passe_hash = ?",
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
                'actif': resultat[4],
                'email': resultat[5]
            }
        return None
    
    def est_super_admin(self, admin_info):
        """Vérifie si l'utilisateur est super-admin"""
        return admin_info and admin_info.get('role') == self.ROLE_SUPER_ADMIN
    
    def est_admin(self, admin_info):
        """Vérifie si l'utilisateur est admin (responsable de service)"""
        return admin_info and admin_info.get('role') == self.ROLE_ADMIN
    
    def est_user(self, admin_info):
        """Vérifie si l'utilisateur est un utilisateur standard"""
        return admin_info and admin_info.get('role') == self.ROLE_USER
    
    def peut_creer_compte(self, createur_info, role_cible):
        """
        Vérifie si un utilisateur peut créer un compte avec le rôle spécifié
        
        Règles:
        - Super Admin peut créer Admin et User
        - Admin peut créer User uniquement
        - User ne peut créer aucun compte
        
        Args:
            createur_info (dict): Infos du créateur
            role_cible (str): Rôle du compte à créer
            
        Returns:
            bool: True si autorisé, False sinon
        """
        if not createur_info:
            return False
        
        role_createur = createur_info.get('role')
        
        # Super Admin peut créer Admin et User
        if role_createur == self.ROLE_SUPER_ADMIN:
            return role_cible in [self.ROLE_ADMIN, self.ROLE_USER]
        
        # Admin peut créer User uniquement
        if role_createur == self.ROLE_ADMIN:
            return role_cible == self.ROLE_USER
        
        # User ne peut rien créer
        return False
    
    def get_role_display(self, role):
        """Retourne le nom d'affichage du rôle"""
        return self.ROLE_DISPLAY.get(role, role)
    
    def obtenir_service_admin(self, admin_id):
        """Retourne l'ID du service géré par l'admin"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT service_id FROM admins WHERE id = ?", (admin_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def modifier_mot_de_passe(self, nom_utilisateur, ancien_mdp, nouveau_mdp, forcer=False):
        """
        Modifie le mot de passe d'un admin
        
        Args:
            nom_utilisateur: Nom d'utilisateur
            ancien_mdp: Ancien mot de passe (ignoré si forcer=True)
            nouveau_mdp: Nouveau mot de passe
            forcer: Si True, ne vérifie pas l'ancien mot de passe (admin only)
        """
        if not forcer:
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
    
    def modifier_admin(self, admin_id, role=None, service_id=None, email=None, nouveau_mdp=None):
        """
        Modifie un compte administrateur
        
        Args:
            admin_id (int): ID de l'admin
            role (str): Nouveau rôle (optionnel)
            service_id (int): Nouveau service (optionnel)
            email (str): Nouvel email (optionnel)
            nouveau_mdp (str): Nouveau mot de passe (optionnel)
            
        Returns:
            bool: True si modifié, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        
        if service_id is not None:
            updates.append("service_id = ?")
            params.append(service_id)
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if nouveau_mdp:
            updates.append("mot_de_passe_hash = ?")
            params.append(self.hasher_mot_de_passe(nouveau_mdp))
        
        if not updates:
            conn.close()
            return False
        
        params.append(admin_id)
        query = f"UPDATE admins SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def supprimer_admin(self, admin_id):
        """
        Supprime un compte administrateur
        
        Args:
            admin_id (int): ID de l'admin
            
        Returns:
            bool: True si supprimé, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def lister_admins(self):
        """Retourne la liste de tous les admins"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.nom_utilisateur, a.role, a.service_id, s.nom, a.actif, 
                   a.date_creation, a.email, a.contact_id, c.nom, c.prenom
            FROM admins a
            LEFT JOIN services s ON a.service_id = s.id
            LEFT JOIN contacts c ON a.contact_id = c.id
            ORDER BY 
                CASE a.role 
                    WHEN 'super_admin' THEN 1 
                    WHEN 'admin' THEN 2 
                    ELSE 3 
                END,
                a.nom_utilisateur
        """)
        
        admins = []
        for row in cursor.fetchall():
            admins.append({
                'id': row[0],
                'nom_utilisateur': row[1],
                'role': row[2],
                'service_id': row[3],
                'service_nom': row[4],
                'actif': row[5],
                'date_creation': row[6],
                'email': row[7],
                'contact_id': row[8],
                'contact_nom': row[9],
                'contact_prenom': row[10],
                'role_display': self.get_role_display(row[2])
            })
        
        conn.close()
        return admins
    
    def obtenir_admin_par_id(self, admin_id):
        """Retourne un admin par son ID"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.nom_utilisateur, a.role, a.service_id, s.nom, a.actif, 
                   a.date_creation, a.email, a.contact_id
            FROM admins a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.id = ?
        """, (admin_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'nom_utilisateur': row[1],
                'role': row[2],
                'service_id': row[3],
                'service_nom': row[4],
                'actif': row[5],
                'date_creation': row[6],
                'email': row[7],
                'contact_id': row[8],
                'role_display': self.get_role_display(row[2])
            }
        return None
    
    def obtenir_par_email(self, email):
        """Retourne un admin par son email"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nom_utilisateur, role, service_id, actif, email, contact_id
            FROM admins 
            WHERE email = ? AND actif = 1
        """, (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'nom_utilisateur': row[1],
                'role': row[2],
                'service_id': row[3],
                'actif': row[4],
                'email': row[5],
                'contact_id': row[6]
            }
        return None
    
    def nombre_admins(self):
        """Retourne le nombre d'administrateurs"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM admins")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
