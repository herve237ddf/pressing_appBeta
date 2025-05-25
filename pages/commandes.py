import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Connexion à la base de données
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de l'application
st.set_page_config(page_title="Liste des Commandes", layout="centered", initial_sidebar_state="collapsed")
st.title("📦 Liste des Commandes")

# Chargement des commandes
query_commandes = '''
SELECT c.commande_id, cl.nom, cl.prenom, c.date_commande, c.date_retour_prevue, c.statut, c.remise, c.montant_total
FROM Commandes c
JOIN Clients cl ON c.client_id = cl.client_id
ORDER BY c.date_commande DESC
'''
cursor.execute(query_commandes)
commandes = cursor.fetchall()

if commandes:
    df = pd.DataFrame(commandes, columns=[
        "Commande ID", "Nom Client", "Prénom Client",
        "Date Commande", "Date Retour Prévue", "Statut",
        "Remise", "Montant Total"
    ])
    st.dataframe(df)

    commande_id = st.selectbox("🔍 Sélectionnez une commande pour voir plus de détails", df["Commande ID"])

    if commande_id:
        st.subheader(f"🧾 Détails de la commande {commande_id}")

        # Récupérer les détails des articles pour la commande sélectionnée
        query_details = '''
            SELECT 
                a.type_article, a.matiere, a.couleur, a.marque, a.taille, 
                a.taches, c.montant_total,c.date_retour_prevue, a.instructions_speciales
            FROM Articles a
            JOIN Commandes c ON a.commande_id = c.commande_id
            LEFT JOIN Lignes_Commande_Services ls ON c.commande_id = ls.commande_id
            LEFT JOIN Services s ON ls.service_id = s.service_id
            WHERE c.commande_id = ?
        '''
        cursor.execute(query_details, (commande_id,))
        details = cursor.fetchall()

        if details:
            # Convertir les résultats en DataFrame
            df_details = pd.DataFrame(details, columns=[
            "Type Article", "Matière", "Couleur", "Marque", "Taille", 
            "Taches", "Prix","Date retour prevue", "Instructions Spéciales"
            ])
            st.dataframe(df_details)
        else:
            st.info("Aucun détail trouvé pour cette commande.")

        # Section modification
        st.subheader(f"✏️ Modifier la commande {commande_id}")
        cursor.execute("SELECT statut, date_retour_prevue FROM Commandes WHERE commande_id = ?", (commande_id,))
        current_info = cursor.fetchone()

        statut_modif = st.selectbox("Statut de la commande", ["En attente", "En cours", "Terminé", "Annulé"],
                                    index=["En attente", "En cours", "Terminé", "Annulé"].index(current_info[0]))
        date_retour_modif = st.date_input("Date de retour prévue", value=pd.to_datetime(current_info[1]).date())

        if st.button("Modifier la commande"):
            try:
                cursor.execute('''
                    UPDATE Commandes 
                    SET statut = ?, date_retour_prevue = ? 
                    WHERE commande_id = ?
                ''', (statut_modif, date_retour_modif, commande_id))
                conn.commit()
                st.success(f"Commande {commande_id} mise à jour avec succès.")
            except sqlite3.Error as e:
                conn.rollback()
                st.error(f"Erreur lors de la mise à jour de la commande {commande_id}: {e}")

else:
    st.warning("Aucune commande disponible.")

# Affichage des livreurs
st.subheader("🚚 Liste des Livreurs disponibles")
try:
    df_livreurs = pd.read_sql_query("SELECT employe_id AS ID, nom AS Nom FROM Employes WHERE poste = 'Livreur' ORDER BY nom", conn)
    if df_livreurs.empty:
        st.info("Aucun livreur trouvé.")
    else:
        st.dataframe(df_livreurs)
except Exception as e:
    st.error(f"Erreur lors du chargement des livreurs : {e}")

# Adresse des clients par commande
st.subheader("📍 Adresses des Clients")
try:
    df_adresses = pd.read_sql_query('''
        SELECT c.commande_id AS "Commande ID", cl.adresse AS "Adresse Client"
        FROM Commandes c
        JOIN Clients cl ON c.client_id = cl.client_id
        ORDER BY c.commande_id
    ''', conn)
    if df_adresses.empty:
        st.info("Aucune adresse trouvée.")
    else:
        st.dataframe(df_adresses)
except Exception as e:
    st.error(f"Erreur lors du chargement des adresses : {e}")

# Livrer une commande
st.subheader("📤 Command livrer")

commandes_terminees = pd.read_sql_query('''
    SELECT c.commande_id, cl.adresse
    FROM Commandes c
    JOIN Clients cl ON c.client_id = cl.client_id
    LEFT JOIN Livraisons l ON c.commande_id = l.commande_id
    WHERE c.statut = 'Terminé' AND l.commande_id IS NULL
''', conn)

if not commandes_terminees.empty and not df_livreurs.empty:
    commande_sel = st.selectbox("Commande à livrer", commandes_terminees["commande_id"])
    livreur_sel = st.selectbox("Livreur assigné", df_livreurs["Nom"])

    if st.button("✅ Confirmer la livraison"):
        adresse_livraison = commandes_terminees.loc[commandes_terminees["commande_id"] == commande_sel, "adresse"].values[0]
        livreur_id = df_livreurs.loc[df_livreurs["Nom"] == livreur_sel, "ID"].values[0]

        try:
            cursor.execute('''
                INSERT INTO Livraisons (commande_id, employe_id, adresse_livraison)
                VALUES (?, ?, ?)
            ''', (commande_sel, livreur_id, adresse_livraison))
            conn.commit()
            st.success(f"Livraison enregistrée pour la commande {commande_sel} avec {livreur_sel}.")
        except sqlite3.Error as e:
            conn.rollback()
            st.error(f"Erreur lors de l'enregistrement de la livraison pour la commande {commande_sel}: {e}")
else:
    st.info("Aucune commande terminée à livrer ou aucun livreur disponible.")

# Historique des livraisons
st.subheader("📦 Historique des Livraisons")
try:
    df_livraisons = pd.read_sql_query('''
        SELECT 
            l.livraison_id, l.commande_id,
            e.nom AS livreur, l.adresse_livraison, l.date_livraison_reelle
        FROM Livraisons l
        JOIN Employes e ON l.employe_id = e.employe_id
        ORDER BY l.date_livraison_reelle DESC
        LIMIT 50
    ''', conn)

    if df_livraisons.empty:
        st.info("Aucune livraison enregistrée.")
    else:
        st.dataframe(df_livraisons)
except Exception as e:
    st.error(f"Erreur lors du chargement des livraisons : {e}")

    

st.subheader("📋 Commandes livrées par livreur")
try:
    df_livreur_commandes = pd.read_sql_query('''
        SELECT e.nom AS Livreurs, GROUP_CONCAT(l.commande_id, ', ') AS Commandes
        FROM Livraisons l
        JOIN Employes e ON l.employe_id = e.employe_id
        GROUP BY e.nom
        ORDER BY e.nom
    ''', conn)
    if df_livreur_commandes.empty:
        st.info("Aucune livraison enregistrée pour les livreurs.")
    else:
        st.dataframe(df_livreur_commandes)
except Exception as e:
    st.error(f"Erreur lors du chargement des commandes par livreur : {e}")

st.subheader("📝 Commande terminé et non livrer")

# Sélectionner les commandes terminées non encore livrées
commandes_terminees_a_assigner = pd.read_sql_query('''
    SELECT c.commande_id, c.adress_livraison, c.date_retour_prevue
    FROM Commandes c
    WHERE c.statut = 'Terminé'
      AND c.commande_id NOT IN (SELECT commande_id FROM Livraisons)

''', conn)
if commandes_terminees_a_assigner.empty:
    st.info("Toutes les commandes terminées ont été livrées.")
else:
    st.dataframe(commandes_terminees_a_assigner, use_container_width=True)



