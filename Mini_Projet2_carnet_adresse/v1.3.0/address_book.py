import csv
from contact import Contact

FICHIER = "contacts.csv"

class AddressBook:
    def __init__(self):
        self.contacts = []
        self.charger_contacts()

    def charger_contacts(self):
        try:
            with open(FICHIER, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.contacts.append(Contact(row["nom"], row["email"], row["telephone"]))
        except FileNotFoundError:
            with open(FICHIER, "w", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["nom", "email", "telephone"])

    def sauvegarder_contacts(self):
        with open(FICHIER, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["nom", "email", "telephone"])
            for c in self.contacts:
                writer.writerow([c.nom, c.email, c.telephone])

    def ajouter_contact(self, nom, email, telephone):
        self.contacts.append(Contact(nom, email, telephone))
        self.sauvegarder_contacts()
        print("Contact ajouté")
