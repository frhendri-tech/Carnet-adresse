class Contact:
    def __init__(self, nom, email, telephone):
        self.nom = nom
        self.email = email
        self.telephone = telephone

    def __str__(self):
        return f"{self.nom} | {self.email} | {self.telephone}"
