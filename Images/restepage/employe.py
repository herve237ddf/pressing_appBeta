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
SELECT employe_id AS ID, 
       nom AS Nom, 
       prenom AS Prénom, 
       poste AS poste, 
       telephone AS Téléphone, 
       email AS Email, 
       salaire AS "salaire" 
FROM Employes 
ORDER BY Nom DESC;
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
