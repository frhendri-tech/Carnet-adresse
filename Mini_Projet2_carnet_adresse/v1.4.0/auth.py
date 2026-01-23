import hashlib

FICHIER_ADMINS = "admins.txt"

def hacher_mot_de_passe(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

def verifier_login(username, password):
    hash_mdp = hacher_mot_de_passe(password)

    try:
        with open(FICHIER_ADMINS, "r", encoding="utf-8") as f:
            for ligne in f:
                user, hash_stocke = ligne.strip().split(";")
                if user == username and hash_stocke == hash_mdp:
                    return True
    except FileNotFoundError:
        pass

    return False
