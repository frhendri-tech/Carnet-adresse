from contact import Contact
import os

class AddressBook:
    def __init__(self, filename="contacts.txt"):
        self.filename = filename
        if not os.path.exists(self.filename):
            open(self.filename, "w").close()

    def add_contact(self, nom, email, telephone):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(f"{nom};{email};{telephone}\n")

    def get_contacts(self):
        contacts = []
        with open(self.filename, "r", encoding="utf-8") as f:
            for line in f:
                nom, email, tel = line.strip().split(";")
                contacts.append(Contact(nom, email, tel))
        return contacts

    def remove_contact(self, nom):
        contacts = self.get_contacts()
        contacts = [c for c in contacts if c.nom != nom]

        with open(self.filename, "w", encoding="utf-8") as f:
            for c in contacts:
                f.write(f"{c.nom};{c.email};{c.telephone}\n")

    def display_contacts(self):
        contacts = self.get_contacts()
        if not contacts:
            print("Aucun contact.")
        for c in contacts:
            print(c)
