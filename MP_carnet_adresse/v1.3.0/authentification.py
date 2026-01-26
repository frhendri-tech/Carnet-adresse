import json
import os
import hashlib

class Authentification:
    """Classe gérant l'authentification des administrateurs"""
    
    def __init__(self, fichier="admins.json"):
        """
        Initialise le système d'authentification
        
        Args:
            fichier (str): Nom du fichier de sauvegarde des admins
        """
        self.fichier = fichier
        self.admins = {}
        self.charger_admins()
        
        # Créer un admin par défaut si aucun n'existe
        if not self.admins:
            self.creer_admin("admin", "admin123")
            print("ℹ️  Admin par défaut créé : admin / admin123")
    
    def hasher_mot_de_passe(self, mot_de_passe):
        """
        Hache un mot de passe avec SHA-256
        
        Args:
            mot_de_passe (str): Mot de passe en clair
            
        Returns:
            str: Hash du mot de passe
        """
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()
    
    def creer_admin(self, nom_utilisateur, mot_de_passe):
        """
        Crée un nouveau compte administrateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            
        Returns:
            bool: True si créé, False sinon
        """
        if nom_utilisateur in self.admins:
            print(f"✗ L'administrateur '{nom_utilisateur}' existe déjà !")
            return False
        
        if len(mot_de_passe) < 6:
            print("✗ Le mot de passe doit contenir au moins 6 caractères !")
            return False
        
        # Hacher et sauvegarder
        hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
        self.admins[nom_utilisateur] = hash_mot_de_passe
        self.sauvegarder_admins()
        print(f"✓ Administrateur '{nom_utilisateur}' créé avec succès !")
        return True
    
    def verifier_connexion(self, nom_utilisateur, mot_de_passe):
        """
        Vérifie les identifiants de connexion
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            mot_de_passe (str): Mot de passe
            
        Returns:
            bool: True si connexion valide, False sinon
        """
        if nom_utilisateur not in self.admins:
            return False
        
        hash_mot_de_passe = self.hasher_mot_de_passe(mot_de_passe)
        return self.admins[nom_utilisateur] == hash_mot_de_passe
    
    def modifier_mot_de_passe(self, nom_utilisateur, ancien_mdp, nouveau_mdp):
        """
        Modifie le mot de passe d'un admin
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            ancien_mdp (str): Ancien mot de passe
            nouveau_mdp (str): Nouveau mot de passe
            
        Returns:
            bool: True si modifié, False sinon
        """
        if not self.verifier_connexion(nom_utilisateur, ancien_mdp):
            print("✗ Ancien mot de passe incorrect !")
            return False
        
        if len(nouveau_mdp) < 6:
            print("✗ Le nouveau mot de passe doit contenir au moins 6 caractères !")
            return False
        
        hash_nouveau_mdp = self.hasher_mot_de_passe(nouveau_mdp)
        self.admins[nom_utilisateur] = hash_nouveau_mdp
        self.sauvegarder_admins()
        print(f"✓ Mot de passe de '{nom_utilisateur}' modifié avec succès !")
        return True
    
    def supprimer_admin(self, nom_utilisateur):
        """
        Supprime un compte administrateur
        
        Args:
            nom_utilisateur (str): Nom d'utilisateur
            
        Returns:
            bool: True si supprimé, False sinon
        """
        if nom_utilisateur not in self.admins:
            print(f"✗ L'administrateur '{nom_utilisateur}' n'existe pas !")
            return False
        
        if len(self.admins) == 1:
            print("✗ Impossible de supprimer le dernier administrateur !")
            return False
        
        del self.admins[nom_utilisateur]
        self.sauvegarder_admins()
        print(f"✓ Administrateur '{nom_utilisateur}' supprimé avec succès !")
        return True
    
    def lister_admins(self):
        """
        Retourne la liste des noms d'utilisateurs
        
        Returns:
            list: Liste des admins
        """
        return list(self.admins.keys())
    
    def nombre_admins(self):
        """Retourne le nombre d'administrateurs"""
        return len(self.admins)
    
    def sauvegarder_admins(self):
        """Sauvegarde les admins dans le fichier JSON"""
        try:
            with open(self.fichier, 'w', encoding='utf-8') as f:
                json.dump(self.admins, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde des admins : {e}")
    
    def charger_admins(self):
        """Charge les admins depuis le fichier JSON"""
        if os.path.exists(self.fichier):
            try:
                with open(self.fichier, 'r', encoding='utf-8') as f:
                    self.admins = json.load(f)
                print(f"✓ {len(self.admins)} administrateur(s) chargé(s)")
            except Exception as e:
                print(f"✗ Erreur lors du chargement des admins : {e}")
                self.admins = {}
        else:
            print(f"ℹ️  Aucun fichier d'admins trouvé. Un nouveau sera créé.")
            self.admins = {}