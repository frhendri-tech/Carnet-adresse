from database import get_connection
from auth import hacher_mot_de_passe

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    "INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)",
    ("admin", hacher_mot_de_passe("admin"))
)

conn.commit()
conn.close()

print("Admin créé (admin / admin)")
