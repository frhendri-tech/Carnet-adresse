from address_book import AddressBook

def menu():
    print("\n===== CARNET D'ADRESSES =====")
    print("1. Ajouter un contact")
    print("2. Supprimer un contact")
    print("3. Afficher les contacts")
    print("4. Quitter")

def main():
    carnet = AddressBook()

    while True:
        menu()
        choix = input("Votre choix : ")

        if choix == "1":
            nom = input("Nom : ")
            email = input("Email : ")
            telephone = input("Téléphone : ")
            carnet.ajouter_contact(nom, email, telephone)

        elif choix == "2":
            nom = input("Nom du contact à supprimer : ")
            carnet.supprimer_contact(nom)

        elif choix == "3":
            carnet.afficher_contacts()

        elif choix == "4":
            print("Au revoir !")
            break

        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()
