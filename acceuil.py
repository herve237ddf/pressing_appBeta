import streamlit as st
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Accueil - PressingApp",
    page_icon="🧺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Supprimer la sidebar (optionnel si elle est vide)
st.sidebar.empty()

# Logo et titre
st.image("logo.png", width=120)  # Assure-toi que 'logo.png' est bien dans le dossier principal
st.title("Bienvenue sur PressingApp")
st.markdown("### Gérez votre pressing efficacement, en toute simplicité.")

# Zone d'informations
st.markdown("""
Avec **PressingApp**, vous pouvez :
- Enregistrer les commandes et les clients
- Suivre la production et les livraisons
- Gérer les services, les stocks et les employés
- Suivre la comptabilité et les statistiques
""")

# Boutons vers les différentes pages/modules
col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Gérer les Commandes"):
        st.switch_page("pages/commandes.py")
    if st.button("👥 Gérer les Clients"):
        st.switch_page("pages/clients.py")
    if st.button("🚚 Livraisons"):
        st.switch_page("pages/livraisons.py")

with col2:
    if st.button("⚙️ Services & Production"):
        st.switch_page("pages/services.py")
    if st.button("📊 Statistiques"):
        st.switch_page("pages/statistiques.py")
    if st.button("🔒 Se déconnecter"):
        st.switch_page("pages/login.py")

# Pied de page
st.markdown("---")
st.markdown("© 2025 NovaSolution – L'innovation au service de votre réussite.")
