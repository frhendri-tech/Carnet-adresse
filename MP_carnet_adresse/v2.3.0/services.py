import sqlite3

class ServicesPolyclinique:
    """Classe gérant les services de la polyclinique"""
    
    def __init__(self, db_name="polyclinique.db"):
        """
        Initialise la gestion des services
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.services = []
        self.creer_table_services()
        self.initialiser_services_par_defaut()
        self.charger_services()
    
    def creer_connexion(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_name)
    
    def creer_table_services(self):
        """Crée la table des services"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                description TEXT,
                responsable_id INTEGER,
                horaire_debut TEXT DEFAULT '08:00',
                horaire_fin TEXT DEFAULT '18:00',
                actif INTEGER DEFAULT 1,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (responsable_id) REFERENCES admins(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table services initialisée")
    
    def initialiser_services_par_defaut(self):
        """Initialise les services médicaux de base"""
        services_defaut = [
            ("Médecine Générale", "Consultations générales et suivi médical", "08:00", "18:00"),
            ("Pédiatrie", "Soins et consultations pour enfants", "08:00", "17:00"),
            ("Cardiologie", "Examens et consultations cardiaques", "09:00", "16:00"),
            ("Dermatologie", "Soins de la peau", "08:30", "17:30"),
            ("Ophtalmologie", "Examens de la vue", "08:00", "16:00"),
            ("Dentaire", "Soins dentaires", "08:00", "18:00"),
            ("Radiologie", "Examens radiologiques", "08:00", "17:00"),
            ("Laboratoire", "Analyses médicales", "07:00", "19:00"),
        ]
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        for nom, description, debut, fin in services_defaut:
            try:
                cursor.execute(
                    "INSERT INTO services (nom, description, horaire_debut, horaire_fin) VALUES (?, ?, ?, ?)",
                    (nom, description, debut, fin)
                )
            except sqlite3.IntegrityError:
                pass  # Service déjà existant
        
        conn.commit()
        conn.close()
    
    def ajouter_service(self, nom, description, horaire_debut="08:00", horaire_fin="18:00"):
        """
        Ajoute un nouveau service
        
        Args:
            nom (str): Nom du service
            description (str): Description
            horaire_debut (str): Heure d'ouverture
            horaire_fin (str): Heure de fermeture
            
        Returns:
            bool: True si ajouté, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO services (nom, description, horaire_debut, horaire_fin) VALUES (?, ?, ?, ?)",
                (nom, description, horaire_debut, horaire_fin)
            )
            conn.commit()
            conn.close()
            print(f"✓ Service '{nom}' ajouté avec succès!")
            self.charger_services()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            print(f"✗ Le service '{nom}' existe déjà !")
            return False
    
    def attribuer_responsable(self, service_id, responsable_id):
        """
        Attribue un responsable à un service
        
        Args:
            service_id (int): ID du service
            responsable_id (int): ID de l'admin responsable
            
        Returns:
            bool: True si attribué, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE services SET responsable_id = ? WHERE id = ?",
            (responsable_id, service_id)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            print(f"✓ Responsable attribué au service")
            self.charger_services()
            return True
        else:
            conn.close()
            return False
    
    def desactiver_service(self, service_id):
        """Désactive un service"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE services SET actif = 0 WHERE id = ?", (service_id,))
        conn.commit()
        conn.close()
        self.charger_services()
    
    def activer_service(self, service_id):
        """Active un service"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE services SET actif = 1 WHERE id = ?", (service_id,))
        conn.commit()
        conn.close()
        self.charger_services()
    
    def obtenir_service_par_id(self, service_id):
        """Retourne un service par son ID"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'nom': row[1],
                'description': row[2],
                'responsable_id': row[3],
                'horaire_debut': row[4],
                'horaire_fin': row[5],
                'actif': row[6]
            }
        return None
    
    def obtenir_services_actifs(self):
        """Retourne tous les services actifs"""
        return [s for s in self.services if s['actif'] == 1]
    
    def charger_services(self):
        """Charge tous les services depuis la base de données"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM services ORDER BY nom")
        rows = cursor.fetchall()
        
        self.services = []
        for row in rows:
            self.services.append({
                'id': row[0],
                'nom': row[1],
                'description': row[2],
                'responsable_id': row[3],
                'horaire_debut': row[4],
                'horaire_fin': row[5],
                'actif': row[6]
            })
        
        conn.close()
        print(f"✓ {len(self.services)} service(s) chargé(s)")