import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Connexion à la base
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Requêtes pour les KPI
def get_kpi():
    # Total commandes
    cursor.execute("SELECT COUNT(*) FROM Commandes")
    total_commandes = cursor.fetchone()[0]

    # Commandes livrées
    cursor.execute("SELECT COUNT(*) FROM Commandes WHERE statut = 'livré'")
    commandes_livrees = cursor.fetchone()[0]

    # Commandes en cours
    cursor.execute("SELECT COUNT(*) FROM Commandes WHERE statut = 'En cours'")
    commandes_en_cours = cursor.fetchone()[0]

    # Commandes en attente
    cursor.execute("SELECT COUNT(*) FROM Commandes WHERE statut = 'En attente'")
    commandes_attente = cursor.fetchone()[0]

    # Commandes terminées
    cursor.execute("SELECT COUNT(*) FROM Commandes WHERE statut = 'Terminé'")
    commandes_termine = cursor.fetchone()[0]

    # Chiffre d'affaire
    cursor.execute("SELECT COALESCE(SUM(montant_total), 0) FROM Commandes")
    chiffre_affaire = cursor.fetchone()[0]


    return total_commandes, commandes_livrees, commandes_en_cours, commandes_attente, commandes_termine, chiffre_affaire


# Récupérer les données
total, livrees, en_cours, attente, terminer, ca = get_kpi()

# En-tête
st.set_page_config(page_title="Dashboard - PressingApp", layout="wide", initial_sidebar_state="collapsed")
st.title("🏠 Tableau de Bord - PressingApp")
st.markdown(f"#### Date : {datetime.today().strftime('%d/%m/%Y')}")

st.markdown("---")

# KPIs affichés en colonnes
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("💰 Chiffre d'affaires", f"{ca:.0f} FCFA")
col2.metric("📦 Commandes", total)
col3.metric("✅ Livrées", livrees)
col4.metric("🚧 En cours", en_cours)
col5.metric("🕒 En attente", attente)
col6.metric("🕒 Terminé", terminer)

st.markdown("---")

# Boutons d'action centrés
st.markdown("### Actions rapides")
b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("➕ Ajouter une Commande"):
        st.switch_page("pages/ajouter_commande.py")

with b2:
    if st.button("👔 Ajouter un Employé"):
        st.switch_page("pages/ajouter_employe.py")

with b3:
    if st.button("📋 Voir toutes les Commandes"):
        st.switch_page("pages/commandes.py")

with b4:
    if st.button("📋 Ajouter un service"):
        st.switch_page("pages/ajout_service.py")        

# Partie Clients et Employés
a1, a2 = st.columns(2)

with a1:
    st.title("📋 Liste des Clients")
    # Requête SQL pour récupérer les infos des clients
    query_clients = """
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
        df_clients = pd.read_sql_query(query_clients, conn)

        if df_clients.empty:
            st.warning("Aucun client enregistré pour le moment.")
        else:
            st.dataframe(df_clients, use_container_width=True)
            st.success(f"{len(df_clients)} client(s) trouvé(s).")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")

with a2:
    st.title("📋 Liste des Employés")
    # Requête SQL pour récupérer les infos des employés
    query_employes = """
    SELECT employe_id AS ID, 
           nom AS Nom, 
           prenom AS Prénom, 
           poste AS Poste, 
           telephone AS Téléphone, 
           email AS Email, 
           salaire AS Salaire 
    FROM Employes 
    ORDER BY Nom DESC;
    """

    try:
        df_employes = pd.read_sql_query(query_employes, conn)

        if df_employes.empty:
            st.warning("Aucun employé enregistré pour le moment.")
        else:
            st.dataframe(df_employes, use_container_width=True)
            st.success(f"{len(df_employes)} employé(s) trouvé(s).")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")

st.title("📋 Liste des Services")
# Requête SQL pour récupérer les infos des services
query_service = """
SELECT *
FROM Services ;
"""


try:
    df_service = pd.read_sql_query(query_service, conn)
    if df_service.empty:
        st.warning("Aucun service enregistré pour le moment.")
    else:
        st.dataframe(df_service, use_container_width=True)
        st.success(f"{len(df_service)} service(s) trouvé(s).")  
except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")        
    
# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")
