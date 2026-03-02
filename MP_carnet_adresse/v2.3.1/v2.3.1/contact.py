class Contact:
    """Classe représentant un contact avec nom, prénom, email, téléphone et informations supplémentaires"""
    
    def __init__(self, nom, prenom, email, telephone, adresse="", fonction="", entreprise="", categorie="Personnel"):
        """
        Initialise un nouveau contact
        
        Args:
            nom (str): Nom de famille du contact
            prenom (str): Prénom du contact
            email (str): Adresse email du contact
            telephone (str): Numéro de téléphone du contact
            adresse (str): Adresse postale (optionnel)
            fonction (str): Fonction/poste (optionnel)
            entreprise (str): Nom de l'entreprise (optionnel)
            categorie (str): Catégorie du contact (Personnel, Entreprise, Client, Fournisseur)
        """
        # MODIFICATION PROF : Convertir nom et prénom en MAJUSCULES
        self.nom = nom.upper()
        self.prenom = prenom.upper()
        
        self.email = email
        self.telephone = telephone
        
        # Nouveaux champs pour Partie 8
        self.adresse = adresse
        self.fonction = fonction
        self.entreprise = entreprise
        self.categorie = categorie
    
    def __str__(self):
        """Retourne une représentation textuelle du contact"""
        base = f"Nom: {self.nom} {self.prenom} | Email: {self.email} | Tél: {self.telephone}"
        
        # Ajouter les informations supplémentaires si disponibles
        if self.entreprise:
            base += f" | Entreprise: {self.entreprise}"
        if self.fonction:
            base += f" | Fonction: {self.fonction}"
        if self.categorie != "Personnel":
            base += f" | Catégorie: {self.categorie}"
            
        return base
    
    def __repr__(self):
        """Retourne une représentation pour le débogage"""
        return f"Contact('{self.nom}', '{self.prenom}', '{self.email}', '{self.telephone}', '{self.categorie}')"
    
    def to_dict(self):
        """Convertit le contact en dictionnaire"""
        return {
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'fonction': self.fonction,
            'entreprise': self.entreprise,
            'categorie': self.categorie
        }
    
    def get_nom_complet(self):
        """Retourne le nom complet du contact en MAJUSCULES"""
        return f"{self.nom} {self.prenom}"
    
    def get_affichage_complet(self):
        """Retourne toutes les informations du contact formatées"""
        info = f"""
Nom complet : {self.get_nom_complet()}
Email       : {self.email}
Téléphone   : {self.telephone}
Catégorie   : {self.categorie}
"""
        if self.adresse:
            info += f"Adresse     : {self.adresse}\n"
        if self.entreprise:
            info += f"Entreprise  : {self.entreprise}\n"
        if self.fonction:
            info += f"Fonction    : {self.fonction}\n"
            
        return info.strip()