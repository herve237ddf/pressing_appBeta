import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Récupération des tables dans la base de données
cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Affichage des tables
tables
