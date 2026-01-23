import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verifier_login(username, password):
    try:
        with open("admins.txt", "r") as f:
            for line in f:
                user, stored_hash = line.strip().split(";")
                if username == user and hash_password(password) == stored_hash:
                    return True
    except FileNotFoundError:
        return False

    return False
