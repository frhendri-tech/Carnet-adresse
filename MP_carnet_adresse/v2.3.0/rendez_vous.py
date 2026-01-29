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
                statut TEXT DEFAULT 'confirmé',
                cree_par INTEGER,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id),
                FOREIGN KEY (cree_par) REFERENCES admins(id),
                UNIQUE(service_id, date_rdv, heure_debut)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Table rendez_vous initialisée")
    
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