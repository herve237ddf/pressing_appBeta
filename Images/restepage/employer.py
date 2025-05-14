import streamlit as st
import sqlite3
import pandas as pd

# Connexion à la base de données SQLite
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de la page
st.set_page_config(page_title="Liste des Commandes", layout="centered")

# Titre de la page
st.title("📦 Liste des Commandes")

# Requête SQL pour récupérer les commandes
query = '''
SELECT c.commande_id, cl.nom, cl.prenom, c.date_commande, c.date_retour_prevue, c.statut, c.remise, c.montant_total
FROM Commandes c
JOIN Clients cl ON c.client_id = cl.client_id
'''

cursor.execute(query)
commandes = cursor.fetchall()

# Vérifier si des commandes sont présentes
if commandes:
    df = pd.DataFrame(commandes, columns=["Commande ID", "Nom Client", "Prénom Client", "Date Commande", "Date Retour Prévue", "Statut", "Remise", "Montant Total"])
    st.dataframe(df)

    commande_id = st.selectbox("🔍 Sélectionnez une commande pour voir plus de détails", df["Commande ID"])

    if commande_id:
        st.subheader(f"🧾 Détails de la commande {commande_id}")

        # Récupérer les détails de la commande
        query_details = '''
            SELECT a.type_article, a.matiere, a.couleur, a.marque, a.taille, s.nom_service, ls.quantite, ls.prix_unitaire
            FROM Articles a
            JOIN Commandes c ON a.commande_id = c.commande_id
            LEFT JOIN Lignes_Commande_Services ls ON c.commande_id = ls.commande_id
            LEFT JOIN Services s ON ls.service_id = s.service_id
            WHERE c.commande_id = ?
        '''
        cursor.execute(query_details, (commande_id,))
        details = cursor.fetchall()

        if details:
            df_details = pd.DataFrame(details, columns=["Type Article", "Matière", "Couleur", "Marque", "Taille", "Service", "Quantité", "Prix Unitaire"])
            st.dataframe(df_details)
        else:
            st.info("Aucun détail trouvé pour cette commande.")

        # Modification de la commande
        st.subheader(f"✏️ Modifier la commande {commande_id}")

        cursor.execute("SELECT statut, date_retour_prevue FROM Commandes WHERE commande_id = ?", (commande_id,))
        current_info = cursor.fetchone()
        current_statut = current_info[0]
        current_date_retour_prevue = current_info[1]

        statut_modification = st.selectbox("Statut de la Commande", ["En attente", "En cours", "Terminé", "Annulé"],
                                           index=["En attente", "En cours", "Terminé", "Annulé"].index(current_statut))
        date_retour_modification = st.date_input("Date de Retour Prévue", value=pd.to_datetime(current_date_retour_prevue).date())

        if st.button("Modifier la Commande"):
            cursor.execute("""
                UPDATE Commandes 
                SET statut = ?, date_retour_prevue = ? 
                WHERE commande_id = ?
            """, (statut_modification, date_retour_modification, commande_id))
            conn.commit()
            st.success(f"Commande {commande_id} mise à jour avec succès !")

else:
    st.warning("Aucune commande trouvée.")

# ----------------------------------------------
# ➕ DataFrame : Informations des Employés
# ----------------------------------------------
st.subheader("👨‍💼 Informations des Employés")
try:
    df_employes = pd.read_sql_query('''
        SELECT employe_id AS "ID", nom AS "Nom", statut AS "Statut", adresse AS "Adresse"
        FROM Employes
    ''', conn)
    
    if df_employes.empty:
        st.info("Aucun employé trouvé.")
    else:
        st.dataframe(df_employes)

except Exception as e:
    st.error(f"Erreur lors du chargement des informations des employés : {e}")
