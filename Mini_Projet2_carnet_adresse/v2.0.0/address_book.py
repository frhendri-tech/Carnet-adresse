from database import get_connection
from contact import Contact


class AddressBook:
    def __init__(self):
        self.conn = get_connection()

    def ajouter_contact(self, nom, prenom, email, telephone):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)",
            (nom, prenom, email, telephone)
        )
        self.conn.commit()

    def modifier_contact(self, email, nom, prenom, telephone):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE contacts
            SET nom = ?, prenom = ?, telephone = ?
            WHERE email = ?
            """,
            (nom, prenom, telephone, email)
        )
        self.conn.commit()

    def supprimer_contact(self, email):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM contacts WHERE email = ?",
            (email,)
        )
        self.conn.commit()

    def lister_contacts(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT nom, prenom, email, telephone FROM contacts ORDER BY nom"
        )
        rows = cursor.fetchall()
        return [Contact(*row) for row in rows]
