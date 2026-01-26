class Contact:
    """Classe représentant un contact avec nom, prénom, email et téléphone"""
    
    def __init__(self, nom, prenom, email, telephone):
        """
        Initialise un nouveau contact
        
        Args:
            nom (str): Nom de famille du contact
            prenom (str): Prénom du contact
            email (str): Adresse email du contact
            telephone (str): Numéro de téléphone du contact
        """
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
    
    def __str__(self):
        """Retourne une représentation textuelle du contact"""
        return f"Nom: {self.nom} {self.prenom} | Email: {self.email} | Tél: {self.telephone}"
    
    def __repr__(self):
        """Retourne une représentation pour le débogage"""
        return f"Contact('{self.nom}', '{self.prenom}', '{self.email}', '{self.telephone}')"
    
    def to_dict(self):
        """Convertit le contact en dictionnaire"""
        return {
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone
        }
    
    def get_nom_complet(self):
        """Retourne le nom complet du contact"""
        return f"{self.nom} {self.prenom}"