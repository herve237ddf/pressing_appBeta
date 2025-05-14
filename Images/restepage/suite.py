import streamlit as st
import sqlite3
import pandas as pd

# Connexion à la base de données SQLite

conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de la page

st.set_page_config(page_title="Liste des Commandes", layout="centered")

# Titre de la page

st.title("Liste des Commandes")

# Requête SQL pour récupérer les commandes

query = '''
SELECT c.commande_id, cl.nom, cl.prenom, c.date_commande, c.date_retour_prevue, c.statut, c.remise, c.montant_total
FROM Commandes c
JOIN Clients cl ON c.client_id = cl.client_id
'''

# Exécuter la requête et récupérer les données

cursor.execute(query)
commandes = cursor.fetchall()

# Vérifier si des commandes sont présentes

if commandes:
# Convertir les résultats en un DataFrame Pandas pour faciliter l'affichage
    df = pd.DataFrame(commandes, columns=["Commande ID", "Nom Client", "Prénom Client", "Date Commande", "Date Retour Prévue", "Statut", "Remise", "Montant Total"])


# Afficher le tableau des commandes
st.dataframe(df)

# Détails supplémentaires sur une commande (au clic sur un ID)
commande_id = st.selectbox("Sélectionnez une commande pour voir plus de détails", df["Commande ID"])

if commande_id:
    st.subheader(f"Détails de la commande {commande_id}")

    # Requête SQL pour récupérer les détails de la commande spécifique
    query_details = '''
        SELECT a.type_article, a.matiere, a.couleur, a.marque, a.taille, s.nom_service, ls.quantite, ls.prix_unitaire
        FROM Articles a
        JOIN Commandes c ON a.commande_id = c.commande_id
        LEFT JOIN Lignes_Commande_Services ls ON c.commande_id = ls.commande_id
        LEFT JOIN Services s ON ls.service_id = s.service_id
        WHERE c.commande_id = ?
    '''
    
    # Exécuter la requête et récupérer les détails
    cursor.execute(query_details, (commande_id,))
    details = cursor.fetchall()

    # Afficher les détails dans un tableau
    if details:
        df_details = pd.DataFrame(details, columns=["Type Article", "Matière", "Couleur", "Marque", "Taille", "Service", "Quantité", "Prix Unitaire"])
        st.dataframe(df_details)
    else:
        st.write("Aucun détail trouvé pour cette commande.")


else:
    st.write("Aucune commande n'a été trouvée.")

















##ajout commande
import streamlit as st
import sqlite3
import pandas as pd

# Connexion à la base de données SQLite
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de la page
st.set_page_config(page_title="Liste des Commandes", layout="centered")

# Titre de la page
st.title("Liste des Commandes")

# Requête SQL pour récupérer les commandes
query = '''
    SELECT c.commande_id, cl.nom, cl.prenom, c.date_commande, c.date_retour_prevue, c.statut, c.remise, c.montant_total
    FROM Commandes c
    JOIN Clients cl ON c.client_id = cl.client_id
'''

# Exécuter la requête et récupérer les données
cursor.execute(query)
commandes = cursor.fetchall()

# Vérifier si des commandes sont présentes
if commandes:
    # Convertir les résultats en un DataFrame Pandas pour faciliter l'affichage
    df = pd.DataFrame(commandes, columns=["Commande ID", "Nom Client", "Prénom Client", "Date Commande", "Date Retour Prévue", "Statut", "Remise", "Montant Total"])

    # Afficher le tableau des commandes
    st.dataframe(df)

    # Détails supplémentaires sur une commande (au clic sur un ID)
    commande_id = st.selectbox("Sélectionnez une commande pour voir plus de détails", df["Commande ID"])

    if commande_id:
        st.subheader(f"Détails de la commande {commande_id}")

        # Requête SQL pour récupérer les détails de la commande spécifique
        query_details = '''
            SELECT a.type_article, a.matiere, a.couleur, a.marque, a.taille, s.nom_service, ls.quantite, ls.prix_unitaire
            FROM Articles a
            JOIN Commandes c ON a.commande_id = c.commande_id
            LEFT JOIN Lignes_Commande_Services ls ON c.commande_id = ls.commande_id
            LEFT JOIN Services s ON ls.service_id = s.service_id
            WHERE c.commande_id = ?
        '''
        
        # Exécuter la requête et récupérer les détails
        cursor.execute(query_details, (commande_id,))
        details = cursor.fetchall()

        # Afficher les détails dans un tableau
        if details:
            df_details = pd.DataFrame(details, columns=["Type Article", "Matière", "Couleur", "Marque", "Taille", "Service", "Quantité", "Prix Unitaire"])
            st.dataframe(df_details)
        else:
            st.write("Aucun détail trouvé pour cette commande.")

        st.subheader(f"Modifier les informations de la commande {commande_id}")

        # Récupérer les informations actuelles de la commande
        cursor.execute("SELECT statut, date_retour_prevue FROM Commandes WHERE commande_id = ?", (commande_id,))
        current_info = cursor.fetchone()
        current_statut = current_info[0]
        current_date_retour_prevue = current_info[1]

        # Formulaire de modification
        statut_modification = st.selectbox("Statut de la Commande", ["En attente", "En cours", "Terminé", "Annulé"], index=["En attente", "En cours", "Terminé", "Annulé"].index(current_statut))
        date_retour_modification = st.date_input("Date de Retour Prévue", value=pd.to_datetime(current_date_retour_prevue).date())

        submit_button = st.button("Modifier la Commande")

        # Lorsque l'utilisateur clique sur "Modifier"
        if submit_button:
            # Mettre à jour le statut et la date de retour prévue dans la base de données
            cursor.execute("""
                UPDATE Commandes 
                SET statut = ?, date_retour_prevue = ? 
                WHERE commande_id = ?
            """, (statut_modification, date_retour_modification, commande_id))

            conn.commit()

            # Confirmation de la mise à jour
            st.success(f"Commande {commande_id} mise à jour avec succès !")
        else:    
            st.write("Aucune commande n'a été trouvée ni Modifier.")
else:
    st.write("Aucune commande n'a été trouvée.")


