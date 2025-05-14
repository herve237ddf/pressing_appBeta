import streamlit as st
import sqlite3
import re

# Connexion à la base de données SQLite
conn = sqlite3.connect("pressing1.db")
cursor = conn.cursor()

# ➕ Ajouter les contraintes UNIQUE si elles n'existent pas déjà
try:
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_email ON Employes(email)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS unique_telephone ON Employes(telephone)")
    conn.commit()
except Exception as e:
    st.warning(f"Erreur lors de la création des contraintes UNIQUE : {e}")

# Configuration de la page
st.set_page_config(page_title="Ajouter un Employé", layout="centered", initial_sidebar_state="collapsed")

# Titre de la page
st.title("Ajouter un Nouveau Employé")

# Formulaire d'ajout d'employé
with st.form(key="employee_form"):
    # Informations de l'employé
    st.subheader("Informations Employé")
    
    nom = st.text_input("Nom de l'Employé")
    prenom = st.text_input("Prénom de l'Employé")
    
    # Sélection du poste parmi les choix disponibles
    poste_options = ["Repasseur", "Blanchisseur", "Livreur"]
    poste = st.selectbox("Poste de l'Employé", poste_options)
    
    # Ajouter un placeholder pour le numéro de téléphone et la validation avec regex
    telephone = st.text_input("Numéro de Téléphone (+237 6xx xxx xxx)", placeholder="+237 6xx xxx xxx")
    
    # Ajouter un placeholder pour l'email et la validation avec regex
    email = st.text_input("Email de l'Employé (exemple@gmail.com)", placeholder="exemple@gmail.com")
    
    salaire = st.number_input("Salaire de l'Employé", min_value=0.0, step=0.01)

    submit_button = st.form_submit_button("Ajouter l'Employé")

# Fonction de validation du numéro de téléphone
def validate_telephone(telephone):
    pattern = r"^\+237 6\d{2} \d{3} \d{3}$"  # Format : +237 6xx xxx xxx
    return re.match(pattern, telephone)

# Fonction de validation de l'email
def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # Format : exemple@gmail.com
    return re.match(pattern, email)

# Lorsque le formulaire est soumis
if submit_button:
    # Vérifier si tous les champs sont remplis
    if not nom or not prenom or not poste or not telephone or not email or salaire == 0.0:
        st.error("Tous les champs doivent être remplis.")
    elif not validate_telephone(telephone):
        st.error("Le numéro de téléphone doit être au format : +237 6xx xxx xxx.")
    elif not validate_email(email):
        st.error("L'email doit être au format : exemple@gmail.com.")
    else:
        try:
            # Vérifier si l'employé existe déjà dans la base de données par email ou téléphone
            cursor.execute("SELECT employe_id FROM Employes WHERE email = ? OR telephone = ?", (email, telephone))
            employe = cursor.fetchone()

            if employe is None:
                # Ajouter l'employé dans la base de données
                cursor.execute(
                    "INSERT INTO Employes (nom, prenom, poste, telephone, email, salaire) VALUES (?, ?, ?, ?, ?, ?)",
                    (nom, prenom, poste, telephone, email, salaire),
                )
                conn.commit()
                st.success("✅ Employé ajouté avec succès !")
            else:
                st.warning("⚠️ Un employé avec cet email ou téléphone existe déjà !")

        except Exception as e:
            st.error(f"❌ Erreur lors de l'ajout de l'employé : {e}")
