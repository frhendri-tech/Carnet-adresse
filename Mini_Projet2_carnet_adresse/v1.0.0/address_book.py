from contact import Contact

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, nom, email, telephone):
        contact = Contact(nom, email, telephone)
        self.contacts.append(contact)

    def remove_contact(self, nom):
        self.contacts = [c for c in self.contacts if c.nom != nom]

    def display_contacts(self):
        if not self.contacts:
            print("Aucun contact.")
        for contact in self.contacts:
            print(contact)
