import streamlit as st
import sqlite3
import pandas as pd

# Connexion à la base de données SQLite
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de la page
st.set_page_config(page_title="Liste des Commandes", layout="centered", initial_sidebar_state="collapsed")

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

        # Partie d'ajout de services
        st.subheader("➕ Ajouter un Service à cette Commande")

        # Récupérer les services disponibles
        query_services = "SELECT service_id, nom_service, prix_unitaire FROM Services"
        cursor.execute(query_services)
        services = cursor.fetchall()

        if services:
            service_selection = st.selectbox("Sélectionnez un service", [s[1] for s in services])
            quantity = st.number_input("Quantité", min_value=1, step=1)
            service_id = [s[0] for s in services if s[1] == service_selection][0]
            unit_price = [s[2] for s in services if s[1] == service_selection][0]
            total_price = unit_price * quantity

            st.write(f"Prix Unitaire : {unit_price} FCFA")
            st.write(f"Prix Total pour {quantity} unité(s) : {total_price} FCFA")

            # Enregistrer les informations de service pour la commande
            if st.button("Ajouter ce service à la commande"):
                cursor.execute('''
                    INSERT INTO Lignes_Commande_Services (commande_id, service_id, quantite, prix_unitaire)
                    VALUES (?, ?, ?, ?)
                ''', (commande_id, service_id, quantity, unit_price))
                conn.commit()
                st.success(f"Service '{service_selection}' ajouté à la commande {commande_id} avec succès !")

        else:
            st.warning("Aucun service disponible pour cette commande.")

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

# -----------------------------------------------
# ➕ DataFrame : Livreurs (employé avec statut = 'Livreur')
# -----------------------------------------------
st.subheader("🚚 Liste des Livreurs (ID & Nom)")
try:
    df_livreurs = pd.read_sql_query("SELECT employe_id AS ID, nom AS Nom FROM Employes WHERE poste = 'Livreur'", conn)
    if df_livreurs.empty:
        st.info("Aucun livreur trouvé.")
    else:
        st.dataframe(df_livreurs)
except Exception as e:
    st.error(f"Erreur lors du chargement des livreurs : {e}")

# -----------------------------------------------------
# ➕ DataFrame : ID Commande et Adresse Client associée
# -----------------------------------------------------
st.subheader("📍 Adresse des Clients par Commande")
try:
    df_commandes_adresses = pd.read_sql_query('''
        SELECT c.commande_id AS "Commande ID", cl.adresse AS "Adresse Client"
        FROM Commandes c
        JOIN Clients cl ON c.client_id = cl.client_id
    ''', conn)
    if df_commandes_adresses.empty:
        st.info("Aucune adresse de client trouvée.")
    else:
        st.dataframe(df_commandes_adresses)
except Exception as e:
    st.error(f"Erreur lors du chargement des adresses clients : {e}")
