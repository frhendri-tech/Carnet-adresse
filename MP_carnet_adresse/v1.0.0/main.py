from address_book import AddressBook

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("📱 CARNET D'ADRESSES")
    print("="*60)
    print("1. Ajouter un contact")
    print("2. Afficher tous les contacts")
    print("3. Afficher un contact")
    print("4. Rechercher un contact")
    print("5. Modifier un contact")
    print("6. Supprimer un contact")
    print("7. Statistiques")
    print("0. Quitter")
    print("="*60)

def main():
    """Fonction principale de l'application"""
    carnet = AddressBook()
    
    print("\n🎉 Bienvenue dans votre carnet d'adresses!")
    
    while True:
        afficher_menu()
        choix = input("\n➤ Votre choix : ").strip()
        
        if choix == "1":
            # Ajouter un contact
            print("\n--- AJOUTER UN CONTACT ---")
            nom = input("Nom : ").strip()
            prenom = input("Prénom : ").strip()
            email = input("Email : ").strip()
            telephone = input("Téléphone : ").strip()
            
            if nom and prenom and email and telephone:
                carnet.ajouter_contact(nom, prenom, email, telephone)
            else:
                print("✗ Erreur : Tous les champs sont obligatoires!")
        
        elif choix == "2":
            # Afficher tous les contacts
            carnet.afficher_contacts()
        
        elif choix == "3":
            # Afficher un contact spécifique
            print("\n--- AFFICHER UN CONTACT ---")
            nom = input("Nom : ").strip()
            prenom = input("Prénom : ").strip()
            contact = carnet.rechercher_contact(nom, prenom)
            
            if contact:
                print("\n" + "="*60)
                print("📋 DÉTAILS DU CONTACT")
                print("="*60)
                print(f"Nom complet : {contact.get_nom_complet()}")
                print(f"Email       : {contact.email}")
                print(f"Téléphone   : {contact.telephone}")
                print("="*60)
            else:
                print(f"\n✗ Aucun contact trouvé avec le nom '{nom} {prenom}'")
        
        elif choix == "4":
            # Rechercher un contact
            print("\n--- RECHERCHER UN CONTACT ---")
            nom = input("Nom à rechercher : ").strip()
            prenom = input("Prénom (optionnel, appuyez sur Entrée pour ignorer) : ").strip()
            
            if prenom:
                contact = carnet.rechercher_contact(nom, prenom)
            else:
                contact = carnet.rechercher_contact(nom)
            
            if contact:
                print(f"\n✓ Contact trouvé :")
                print(f"  {contact}")
            else:
                print(f"\n✗ Aucun contact trouvé")
        
        elif choix == "5":
            # Modifier un contact
            print("\n--- MODIFIER UN CONTACT ---")
            nom = input("Nom du contact à modifier : ").strip()
            prenom = input("Prénom du contact : ").strip()
            
            contact = carnet.rechercher_contact(nom, prenom)
            if contact:
                print(f"\nContact actuel : {contact}")
                print("\nLaissez vide pour conserver la valeur actuelle")
                
                nouveau_nom = input(f"Nouveau nom [{contact.nom}] : ").strip()
                nouveau_prenom = input(f"Nouveau prénom [{contact.prenom}] : ").strip()
                nouveau_email = input(f"Nouvel email [{contact.email}] : ").strip()
                nouveau_telephone = input(f"Nouveau téléphone [{contact.telephone}] : ").strip()
                
                carnet.modifier_contact(
                    nom, prenom,
                    nouveau_nom if nouveau_nom else None,
                    nouveau_prenom if nouveau_prenom else None,
                    nouveau_email if nouveau_email else None,
                    nouveau_telephone if nouveau_telephone else None
                )
            else:
                print(f"✗ Contact introuvable.")
        
        elif choix == "6":
            # Supprimer un contact
            print("\n--- SUPPRIMER UN CONTACT ---")
            nom = input("Nom du contact à supprimer : ").strip()
            prenom = input("Prénom du contact : ").strip()
            
            confirmation = input(f"⚠️  Confirmer la suppression de '{nom} {prenom}' ? (o/n) : ").strip().lower()
            
            if confirmation == 'o':
                carnet.supprimer_contact(nom, prenom)
            else:
                print("❌ Suppression annulée.")
        
        elif choix == "7":
            # Statistiques
            print(f"\n📊 Nombre total de contacts : {carnet.nombre_contacts()}")
        
        elif choix == "0":
            # Quitter
            print("\n👋 Au revoir! À bientôt!")
            break
        
        else:
            print("\n❌ Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()