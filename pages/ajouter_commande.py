import streamlit as st
import sqlite3
import re
from datetime import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Nouvelle Commande", layout="centered")

# Connexion à la base de données
conn = sqlite3.connect("pressing1.db", check_same_thread=False)
cursor = conn.cursor()

# Fonctions de validation
def validate_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def validate_telephone(telephone):
    return re.match(r"^\+237\s6\d{2}\s\d{3}\s\d{3}$", telephone)

# Chargement des services
cursor.execute("SELECT service_id, nom_service, prix_service FROM Services")
services_data = cursor.fetchall()
service_dict = {nom: (sid, prix) for sid, nom, prix in services_data}
noms_services_disponibles = list(service_dict.keys())

# Initialisation de session
if "client_data" not in st.session_state:
    st.session_state.client_data = None

# Titre
st.title("🧾 Ajouter une Commande")

# Type de client
st.subheader("👤 Type de Client")
type_client = st.radio("Sélectionnez le type de client :", ["Client existant", "Nouveau client"])

# Recherche client existant
if type_client == "Client existant":
    with st.form(key="search_form"):
        search_email = st.text_input("Email du client")
        search_tel = st.text_input("Téléphone du client")
        search_btn = st.form_submit_button("🔍 Rechercher")

        if search_btn and (search_email or search_tel):
            cursor.execute("SELECT * FROM Clients WHERE email = ? OR telephone = ?", (search_email, search_tel))
            client_data = cursor.fetchone()
            if client_data:
                st.session_state.client_data = client_data
                df = pd.DataFrame([client_data], columns=["ID", "Nom", "Prénom", "Adresse", "Téléphone", "Email", "Date Inscription", "Points"])
                st.success("🎉 Client trouvé :")
                st.dataframe(df)
            else:
                st.warning("⚠️ Aucun client trouvé. Veuillez le saisir comme nouveau client.")
                st.session_state.client_data = None
                type_client = "Nouveau client"

# Récupération du client existant depuis session
client_data = st.session_state.client_data

# Formulaire principal
with st.form(key="order_form"):
    with st.expander("📋 Informations Client", expanded=True):
        if client_data:
            st.text_input("Identifiant Client", value=client_data[0], disabled=True)
            client_id = client_data[0]
        elif type_client == "Nouveau client":
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            adresse = st.text_input("Adresse")
            telephone = st.text_input("Téléphone", placeholder="+237 6xx xxx xxx")
            email = st.text_input("Email", placeholder="exemple@gmail.com")

    with st.expander("📦 Détails de la Commande", expanded=True):
        date_commande = st.date_input("Date de Commande", value=datetime.today())
        date_retour_prevue = st.date_input("Date de Retour Prévue")
        adresse_livraison = st.text_input("Adresse de Livraison")
        statut_commande = st.selectbox("Statut", ["En attente", "En cours", "Terminé", "Annulé"])

        selected_services = st.multiselect("🛠️ Sélectionner les Services", noms_services_disponibles)
        services_selectionnes = []
        montant_total = 0

        for service_nom in selected_services:
            st.subheader(f"🧺 {service_nom}")
            quantite = st.number_input(f"Quantité", min_value=1, step=1, key=f"qte_{service_nom}")
            type_article = st.text_input("Type d'article", key=f"type_{service_nom}")
            matiere = st.text_input("Matière", key=f"matiere_{service_nom}")
            couleur = st.text_input("Couleur", key=f"couleur_{service_nom}")
            marque = st.text_input("Marque", key=f"marque_{service_nom}")
            taille = st.text_input("Taille", key=f"taille_{service_nom}")

            service_id, prix_unitaire = service_dict[service_nom]
            total_service = quantite * prix_unitaire
            montant_total += total_service

            st.info(f"💰 Total pour {service_nom} : {total_service} FCFA")

            services_selectionnes.append({
                "service_id": service_id,
                "quantite": quantite,
                "prix_unitaire": prix_unitaire,
                "type_article": type_article,
                "matiere": matiere,
                "couleur": couleur,
                "marque": marque,
                "taille": taille
            })


        remise = st.number_input("Remise (facultative)", min_value=0.0, step=100.0)
        montant_final = montant_total - remise
        st.success(f"💵 Montant Final : {montant_final} FCFA")

    submit_button = st.form_submit_button("✅ Enregistrer la Commande")

# Traitement de l'enregistrement
if submit_button:
    try:
        conn.execute("BEGIN")

        # Traitement client
        if type_client == "Client existant":
            if not client_data:
                st.error("❗ Aucun client existant sélectionné. Veuillez effectuer une recherche valide.")
                st.stop()
            client_id = client_data[0]
            cursor.execute("UPDATE Clients SET points_fidelite = points_fidelite + 1 WHERE client_id = ?", (client_id,))
        elif type_client == "Nouveau client":
            if not nom or not prenom or not adresse or not telephone or not email:
                st.error("❗ Tous les champs client sont obligatoires.")
                st.stop()
            elif not validate_email(email):
                st.error("❗ Email invalide.")
                st.stop()
            elif not validate_telephone(telephone):
                st.error("❗ Téléphone invalide (ex: +237 6xx xxx xxx).")
                st.stop()
    
            cursor.execute("""
                INSERT INTO Clients (nom, prenom, adresse, telephone, email, date_inscription)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nom, prenom, adresse, telephone, email, datetime.now().strftime('%Y-%m-%d')))
            client_id = cursor.lastrowid

        # Fidélité bonus
        cursor.execute("SELECT points_fidelite FROM Clients WHERE client_id = ?", (client_id,))
        points = cursor.fetchone()
        if points and points[0] >= 50:
            remise += 500
            st.info("🎁 Bonus fidélité : 500 FCFA appliqué automatiquement !")
        #id service
        query = f"SELECT service_id FROM Services WHERE nom_service =?", (services_selectionnes[0]["service_id"],)
        cursor.execute(query, services_selectionnes)
        resultats = cursor.fetchall()
        service_ids = resultats[0][0]
        # Commande
        cursor.execute("""
            INSERT INTO Commandes (client_id, date_commande, date_retour_prevue, montant_total, remise, adress_livraison, statut, service_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_id, date_commande, date_retour_prevue, montant_total, remise, adresse_livraison, statut_commande, service_ids))
        commande_id = cursor.lastrowid

        # Articles
        for service in services_selectionnes:
            articles = [a.strip() for a in service["type_article"].split(",") if a.strip()]
            for article in articles:
                cursor.execute("""
                    INSERT INTO Articles (commande_id, type_article, matiere, couleur, marque, taille)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (commande_id, article, service["matiere"], service["couleur"], service["marque"], service["taille"]))

        conn.commit()
        st.success("✅ Commande enregistrée avec succès !")

        # Réinitialisation
        st.session_state.client_data = None

    except Exception as e:
        conn.rollback()
        st.error(f"❌ Erreur lors de l'enregistrement : {e}")
