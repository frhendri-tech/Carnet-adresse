import sqlite3
from datetime import datetime, timedelta

class RendezVous:
    """Classe gérant les rendez-vous de la polyclinique"""
    
    def __init__(self, db_name="polyclinique.db"):
        """
        Initialise la gestion des rendez-vous
        
        Args:
            db_name (str): Nom de la base de données
        """
        self.db_name = db_name
        self.creer_table_rendez_vous()
    
    def creer_connexion(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_name)
    
    def creer_table_rendez_vous(self):
        """Crée la table des rendez-vous"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rendez_vous (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                patient_nom TEXT NOT NULL,
                patient_prenom TEXT NOT NULL,
                patient_telephone TEXT NOT NULL,
                patient_email TEXT,
                date_rdv DATE NOT NULL,
                heure_debut TIME NOT NULL,
                heure_fin TIME NOT NULL,
                motif TEXT,
                statut TEXT DEFAULT 'en_attente',
                cree_par INTEGER,
                valide_par INTEGER,
                date_validation TIMESTAMP,
                commentaire_validation TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id),
                FOREIGN KEY (cree_par) REFERENCES admins(id),
                FOREIGN KEY (valide_par) REFERENCES admins(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table rendez_vous initialisée")
        
        # Migrer les anciens rendez-vous si nécessaire
        self._migrer_statuts_rendez_vous()
        
        # Supprimer la contrainte UNIQUE si elle existe
        self._supprimer_contrainte_unique()
    
    def _supprimer_contrainte_unique(self):
        """Supprime la contrainte UNIQUE sur (service_id, date_rdv, heure_debut) si elle existe"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            # Vérifier si la contrainte UNIQUE existe
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='rendez_vous'")
            result = cursor.fetchone()
            
            if result and 'UNIQUE(service_id, date_rdv, heure_debut)' in result[0]:
                print("🔄 Suppression de la contrainte UNIQUE sur rendez_vous...")
                
                # SQLite ne permet pas de supprimer une contrainte directement, il faut recréer la table
                cursor.execute("ALTER TABLE rendez_vous RENAME TO rendez_vous_old")
                
                # Créer la nouvelle table sans la contrainte UNIQUE
                cursor.execute('''
                    CREATE TABLE rendez_vous (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service_id INTEGER NOT NULL,
                        patient_nom TEXT NOT NULL,
                        patient_prenom TEXT NOT NULL,
                        patient_telephone TEXT NOT NULL,
                        patient_email TEXT,
                        date_rdv DATE NOT NULL,
                        heure_debut TIME NOT NULL,
                        heure_fin TIME NOT NULL,
                        motif TEXT,
                        statut TEXT DEFAULT 'en_attente',
                        cree_par INTEGER,
                        valide_par INTEGER,
                        date_validation TIMESTAMP,
                        commentaire_validation TEXT,
                        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (service_id) REFERENCES services(id),
                        FOREIGN KEY (cree_par) REFERENCES admins(id),
                        FOREIGN KEY (valide_par) REFERENCES admins(id)
                    )
                ''')
                
                # Copier les données
                cursor.execute('''
                    INSERT INTO rendez_vous 
                    (id, service_id, patient_nom, patient_prenom, patient_telephone, patient_email,
                     date_rdv, heure_debut, heure_fin, motif, statut, cree_par, 
                     valide_par, date_validation, commentaire_validation, date_creation)
                    SELECT id, service_id, patient_nom, patient_prenom, patient_telephone, patient_email,
                     date_rdv, heure_debut, heure_fin, motif, statut, cree_par, 
                     valide_par, date_validation, commentaire_validation, date_creation
                    FROM rendez_vous_old
                ''')
                
                # Supprimer l'ancienne table
                cursor.execute("DROP TABLE rendez_vous_old")
                
                conn.commit()
                print("✓ Contrainte UNIQUE supprimée avec succès")
            
        except Exception as e:
            print(f"⚠️ Note lors de la suppression de la contrainte: {e}")
        finally:
            conn.close()
    
    def _migrer_statuts_rendez_vous(self):
        """Met à jour les statuts des anciens rendez-vous"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            # Vérifier s'il y a des rendez-vous avec statut 'confirmé' à migrer
            cursor.execute("SELECT COUNT(*) FROM rendez_vous WHERE statut = 'confirmé'")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"🔄 Migration des statuts de rendez-vous ({count} rendez-vous trouvés)")
                # Les anciens rendez-vous confirmés restent confirmés
                # Les nouveaux seront 'en_attente' par défaut
                print("✓ Migration des statuts terminée")
            
            conn.commit()
        except Exception as e:
            print(f"⚠️ Note: {e}")
        finally:
            conn.close()
    
    def generer_creneaux(self, date, horaire_debut="08:00", horaire_fin="18:00", duree_minutes=30):
        """
        Génère tous les créneaux horaires pour une journée
        
        Args:
            date (str): Date au format YYYY-MM-DD
            horaire_debut (str): Heure de début (HH:MM)
            horaire_fin (str): Heure de fin (HH:MM)
            duree_minutes (int): Durée de chaque créneau en minutes
            
        Returns:
            list: Liste des créneaux [(heure_debut, heure_fin), ...]
        """
        creneaux = []
        
        # Convertir les heures en datetime
        debut = datetime.strptime(horaire_debut, "%H:%M")
        fin = datetime.strptime(horaire_fin, "%H:%M")
        
        current = debut
        while current < fin:
            heure_debut = current.strftime("%H:%M")
            current += timedelta(minutes=duree_minutes)
            heure_fin = current.strftime("%H:%M")
            
            if current <= fin:
                creneaux.append((heure_debut, heure_fin))
        
        return creneaux
    
    def verifier_disponibilite(self, service_id, date, heure_debut):
        """
        Vérifie si un créneau est disponible
        
        Args:
            service_id (int): ID du service
            date (str): Date (YYYY-MM-DD)
            heure_debut (str): Heure de début (HH:MM)
            
        Returns:
            bool: True si disponible, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM rendez_vous WHERE service_id = ? AND date_rdv = ? AND heure_debut = ? AND statut != 'annulé'",
            (service_id, date, heure_debut)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count == 0
    
    def prendre_rendez_vous(self, service_id, patient_nom, patient_prenom, patient_telephone, 
                           date_rdv, heure_debut, heure_fin, motif="", patient_email="", cree_par=None):
        """
        Prend un rendez-vous
        
        Args:
            service_id (int): ID du service
            patient_nom (str): Nom du patient
            patient_prenom (str): Prénom du patient
            patient_telephone (str): Téléphone
            date_rdv (str): Date (YYYY-MM-DD)
            heure_debut (str): Heure début (HH:MM)
            heure_fin (str): Heure fin (HH:MM)
            motif (str): Motif de consultation
            patient_email (str): Email (optionnel)
            cree_par (int): ID de l'admin qui crée le RDV
            
        Returns:
            tuple: (success: bool, message: str, rdv_id: int or None)
        """
        # Vérifier disponibilité
        if not self.verifier_disponibilite(service_id, date_rdv, heure_debut):
            return (False, "Ce créneau est déjà réservé !", None)
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO rendez_vous 
                (service_id, patient_nom, patient_prenom, patient_telephone, patient_email,
                 date_rdv, heure_debut, heure_fin, motif, cree_par)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (service_id, patient_nom.upper(), patient_prenom.upper(), patient_telephone, 
                  patient_email, date_rdv, heure_debut, heure_fin, motif, cree_par))
            
            rdv_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return (True, f"Rendez-vous confirmé pour le {date_rdv} à {heure_debut}", rdv_id)
        except Exception as e:
            conn.close()
            return (False, f"Erreur : {str(e)}", None)
    
    def obtenir_creneaux_disponibles(self, service_id, date, horaire_debut="08:00", horaire_fin="18:00"):
        """
        Retourne tous les créneaux disponibles pour un service et une date
        
        Returns:
            list: Liste de tuples (heure_debut, heure_fin, disponible)
        """
        tous_creneaux = self.generer_creneaux(date, horaire_debut, horaire_fin)
        
        creneaux_avec_dispo = []
        for heure_debut, heure_fin in tous_creneaux:
            disponible = self.verifier_disponibilite(service_id, date, heure_debut)
            creneaux_avec_dispo.append((heure_debut, heure_fin, disponible))
        
        return creneaux_avec_dispo
    
    def obtenir_rendez_vous_par_service(self, service_id, date_debut=None, date_fin=None):
        """Retourne tous les RDV d'un service"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        if date_debut and date_fin:
            cursor.execute("""
                SELECT * FROM rendez_vous 
                WHERE service_id = ? AND date_rdv BETWEEN ? AND ?
                ORDER BY date_rdv, heure_debut
            """, (service_id, date_debut, date_fin))
        else:
            cursor.execute("""
                SELECT * FROM rendez_vous 
                WHERE service_id = ?
                ORDER BY date_rdv DESC, heure_debut
            """, (service_id,))
        
        rdv_list = []
        for row in cursor.fetchall():
            rdv_list.append({
                'id': row[0],
                'service_id': row[1],
                'patient_nom': row[2],
                'patient_prenom': row[3],
                'patient_telephone': row[4],
                'patient_email': row[5],
                'date_rdv': row[6],
                'heure_debut': row[7],
                'heure_fin': row[8],
                'motif': row[9],
                'statut': row[10]
            })
        
        conn.close()
        return rdv_list
    
    def obtenir_rendez_vous_par_date(self, date):
        """Retourne tous les RDV d'une date"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, s.nom as service_nom
            FROM rendez_vous r
            JOIN services s ON r.service_id = s.id
            WHERE r.date_rdv = ?
            ORDER BY s.nom, r.heure_debut
        """, (date,))
        
        rdv_list = []
        for row in cursor.fetchall():
            rdv_list.append({
                'id': row[0],
                'service_id': row[1],
                'patient_nom': row[2],
                'patient_prenom': row[3],
                'patient_telephone': row[4],
                'patient_email': row[5],
                'date_rdv': row[6],
                'heure_debut': row[7],
                'heure_fin': row[8],
                'motif': row[9],
                'statut': row[10],
                'service_nom': row[13]
            })
        
        conn.close()
        return rdv_list
    
    def annuler_rendez_vous(self, rdv_id):
        """Annule un rendez-vous"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE rendez_vous SET statut = 'annulé' WHERE id = ?",
            (rdv_id,)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def valider_rendez_vous(self, rdv_id, admin_id, commentaire=None):
        """
        Valide un rendez-vous (passage de 'en_attente' à 'confirmé')
        Vérifie d'abord qu'il n'y a pas déjà un rendez-vous confirmé à ce créneau
        
        Args:
            rdv_id (int): ID du rendez-vous
            admin_id (int): ID de l'admin qui valide
            commentaire (str): Commentaire optionnel
            
        Returns:
            tuple: (success: bool, message: str)
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        # Vérifier les détails du rendez-vous à valider
        cursor.execute("""
            SELECT service_id, date_rdv, heure_debut FROM rendez_vous 
            WHERE id = ? AND statut = 'en_attente'
        """, (rdv_id,))
        rdv = cursor.fetchone()
        
        if not rdv:
            conn.close()
            return (False, "Rendez-vous introuvable ou déjà traité.")
        
        service_id, date_rdv, heure_debut = rdv
        
        # Vérifier s'il y a déjà un rendez-vous confirmé à ce créneau
        cursor.execute("""
            SELECT COUNT(*) FROM rendez_vous 
            WHERE service_id = ? AND date_rdv = ? AND heure_debut = ? 
            AND statut = 'confirmé' AND id != ?
        """, (service_id, date_rdv, heure_debut, rdv_id))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return (False, "Ce créneau est déjà occupé par un rendez-vous confirmé.")
        
        # Valider le rendez-vous
        cursor.execute("""
            UPDATE rendez_vous 
            SET statut = 'confirmé', 
                valide_par = ?, 
                date_validation = CURRENT_TIMESTAMP,
                commentaire_validation = ?
            WHERE id = ?
        """, (admin_id, commentaire, rdv_id))
        
        success = cursor.rowcount > 0
        if success:
            conn.commit()
            conn.close()
            return (True, "Rendez-vous validé avec succès !")
        
        conn.close()
        return (False, "Erreur lors de la validation.")
    
    def rejeter_rendez_vous(self, rdv_id, admin_id, commentaire=None):
        """
        Rejette un rendez-vous (passage de 'en_attente' à 'rejeté')
        
        Args:
            rdv_id (int): ID du rendez-vous
            admin_id (int): ID de l'admin qui rejette
            commentaire (str): Commentaire optionnel (raison du rejet)
            
        Returns:
            bool: True si rejeté, False sinon
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE rendez_vous 
            SET statut = 'rejeté', 
                valide_par = ?, 
                date_validation = CURRENT_TIMESTAMP,
                commentaire_validation = ?
            WHERE id = ? AND statut = 'en_attente'
        """, (admin_id, commentaire, rdv_id))
        
        success = cursor.rowcount > 0
        if success:
            conn.commit()
        
        conn.close()
        return success
    
    def obtenir_rendez_vous_en_attente(self, service_id=None):
        """
        Retourne les rendez-vous en attente de validation
        
        Args:
            service_id (int, optional): Filtrer par service spécifique
            
        Returns:
            list: Liste des rendez-vous en attente
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        if service_id:
            cursor.execute("""
                SELECT r.*, s.nom as service_nom, 
                       a.nom_utilisateur as cree_par_nom
                FROM rendez_vous r
                JOIN services s ON r.service_id = s.id
                LEFT JOIN admins a ON r.cree_par = a.id
                WHERE r.statut = 'en_attente' AND r.service_id = ?
                ORDER BY r.date_rdv ASC, r.heure_debut ASC
            """, (service_id,))
        else:
            cursor.execute("""
                SELECT r.*, s.nom as service_nom,
                       a.nom_utilisateur as cree_par_nom
                FROM rendez_vous r
                JOIN services s ON r.service_id = s.id
                LEFT JOIN admins a ON r.cree_par = a.id
                WHERE r.statut = 'en_attente'
                ORDER BY r.date_rdv ASC, r.heure_debut ASC
            """)
        
        rdv_list = []
        for row in cursor.fetchall():
            rdv_list.append({
                'id': row[0],
                'service_id': row[1],
                'patient_nom': row[2],
                'patient_prenom': row[3],
                'patient_telephone': row[4],
                'patient_email': row[5],
                'date_rdv': row[6],
                'heure_debut': row[7],
                'heure_fin': row[8],
                'motif': row[9],
                'statut': row[10],
                'cree_par': row[11],
                'valide_par': row[12],
                'date_validation': row[13],
                'commentaire_validation': row[14],
                'date_creation': row[15],
                'service_nom': row[16],
                'cree_par_nom': row[17]
            })
        
        conn.close()
        return rdv_list
    
    def obtenir_statistiques_service(self, service_id):
        """Retourne les statistiques d'un service"""
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        # Total RDV
        cursor.execute(
            "SELECT COUNT(*) FROM rendez_vous WHERE service_id = ?",
            (service_id,)
        )
        total = cursor.fetchone()[0]
        
        # RDV confirmés
        cursor.execute(
            "SELECT COUNT(*) FROM rendez_vous WHERE service_id = ? AND statut = 'confirmé'",
            (service_id,)
        )
        confirmes = cursor.fetchone()[0]
        
        # RDV annulés
        cursor.execute(
            "SELECT COUNT(*) FROM rendez_vous WHERE service_id = ? AND statut = 'annulé'",
            (service_id,)
        )
        annules = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'confirmes': confirmes,
            'annules': annules
        }
    
    def obtenir_rendez_vous_par_patient(self, patient_email):
        """
        Retourne tous les rendez-vous d'un patient (par email)
        
        Args:
            patient_email (str): Email du patient
            
        Returns:
            list: Liste des rendez-vous du patient
        """
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT r.*, s.nom as service_nom
            FROM rendez_vous r
            JOIN services s ON r.service_id = s.id
            WHERE r.patient_email = ?
            ORDER BY r.date_rdv DESC, r.heure_debut
        """, (patient_email,))
        
        rdv_list = []
        for row in cursor.fetchall():
            rdv_list.append({
                'id': row[0],
                'service_id': row[1],
                'patient_nom': row[2],
                'patient_prenom': row[3],
                'patient_telephone': row[4],
                'patient_email': row[5],
                'date_rdv': row[6],
                'heure_debut': row[7],
                'heure_fin': row[8],
                'motif': row[9],
                'statut': row[10],
                'service_nom': row[13]
            })
        
        conn.close()
        return rdv_list
    
    def obtenir_prochains_rendez_vous(self, patient_email, limite=5):
        """
        Retourne les prochains rendez-vous d'un patient
        
        Args:
            patient_email (str): Email du patient
            limite (int): Nombre maximum de rendez-vous à retourner
            
        Returns:
            list: Liste des prochains rendez-vous
        """
        from datetime import date
        
        conn = self.creer_connexion()
        cursor = conn.cursor()
        
        today = date.today().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT r.*, s.nom as service_nom
            FROM rendez_vous r
            JOIN services s ON r.service_id = s.id
            WHERE r.patient_email = ? 
              AND r.date_rdv >= ? 
              AND r.statut = 'confirmé'
            ORDER BY r.date_rdv ASC, r.heure_debut ASC
            LIMIT ?
        """, (patient_email, today, limite))
        
        rdv_list = []
        for row in cursor.fetchall():
            rdv_list.append({
                'id': row[0],
                'service_id': row[1],
                'patient_nom': row[2],
                'patient_prenom': row[3],
                'patient_telephone': row[4],
                'patient_email': row[5],
                'date_rdv': row[6],
                'heure_debut': row[7],
                'heure_fin': row[8],
                'motif': row[9],
                'statut': row[10],
                'service_nom': row[13]
            })
        
        conn.close()
        return rdv_list