import streamlit as st
import sqlite3
import pandas as pd

# Connexion à la base de données
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Titre de la page
st.set_page_config(page_title="Liste des Clients", layout="centered")
st.title("📋 Liste des Clients")

# Requête SQL pour récupérer les infos des clients
query = """
SELECT client_id AS ID,
       nom AS Nom,
       prenom AS Prénom,
       adresse AS Adresse,
       telephone AS Téléphone,
       email AS Email,
       date_inscription AS "Date d'inscription",
       points_fidelite AS "Points de fidélité"
FROM Clients
ORDER BY date_inscription DESC
"""

try:
    df_clients = pd.read_sql_query(query, conn)

    if df_clients.empty:
        st.warning("Aucun client enregistré pour le moment.")
    else:
        st.dataframe(df_clients, use_container_width=True)
        st.success(f"{len(df_clients)} client(s) trouvé(s).")
except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")
