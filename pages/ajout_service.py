import streamlit as st
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# Configuration de la page
st.set_page_config(page_title="Ajouter un Service", layout="centered", initial_sidebar_state="collapsed")
st.title("Ajouter un Nouveau Service")

# Formulaire d'ajout de service
with st.form("form_ajout_service"):
    nom_service = st.text_input("Nom du Service")
    prix_service = st.number_input("Prix du Service", min_value=0.0, step=0.01)
    description = st.text_area("Description du Service")
    
    submit_button = st.form_submit_button("Ajouter le Service")

# Traitement du formulaire
if submit_button:
    if not nom_service or not description:
        st.error("Tous les champs doivent être remplis.")
    elif prix_service <= 0:
        st.error("Le prix du service doit être supérieur à 0.")
    else:
        try:
            # Vérifier si le service existe déjà
            cursor.execute("SELECT * FROM Services WHERE nom_service = ?", (nom_service,))
            existing_service = cursor.fetchone()

            if existing_service:
                st.warning("Ce service existe déjà.")
            else:
                cursor.execute(
                    "INSERT INTO Services (nom_service, prix_service, description_service) VALUES (?, ?, ?)",
                    (nom_service, prix_service, description)
                )
                conn.commit()
                st.success(f"Le service '{nom_service}' a été ajouté avec succès !")
        except Exception as e:
            st.error(f"Erreur lors de l'ajout : {e}")
