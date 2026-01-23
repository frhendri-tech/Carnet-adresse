import sqlite3

def get_connection():
    conn = sqlite3.connect("carnet.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            email TEXT UNIQUE,
            telephone TEXT
        )
    """)
    conn.commit()
    return conn
