import streamlit as st
import sqlite3
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Nouveau paiement", layout="centered")

# Connexion à la base de données
conn = sqlite3.connect("pressing1.db", check_same_thread=False)
cursor = conn.cursor()

# Créer la table Paiement si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS Paiement (
    id_paiement INTEGER PRIMARY KEY AUTOINCREMENT,
    id_commande INTEGER,
    montant REAL NOT NULL,
    date_paiement TEXT NOT NULL,
    mode_paiement TEXT,
    FOREIGN KEY (id_commande) REFERENCES Commandes(commande_id)
)
""")
conn.commit()

# Initialisation de la session
if "commande" not in st.session_state:
    st.session_state.commande = None
if "client" not in st.session_state:
    st.session_state.client = None
if "articles" not in st.session_state:
    st.session_state.articles = None
if "paiements" not in st.session_state:
    st.session_state.paiements = []

st.title("💳 Paiement et Facturation")

# Rechercher une commande
st.subheader("Rechercher une commande")
id_commande = st.number_input("Entrer l'identifiant de la commande", min_value=1, step=1)

if st.button("Rechercher la commande"):
    # Récupérer les infos de la commande (on sélectionne explicitement les colonnes)
    cursor.execute("SELECT commande_id, client_id, date_commande, montant_total, statut FROM Commandes WHERE commande_id = ?", (id_commande,))
    commande = cursor.fetchone()

    if commande:
        st.success("✅ Commande trouvée")
        st.write("**ID Commande :**", commande[0])
        st.write("**ID Client :**", commande[1])
        st.write("**Date de commande :**", commande[2])
        st.write("**Montant total :**", commande[3])
        st.write("**Statut :**", commande[4])

        # Enregistrer les informations de la commande dans la session
        st.session_state.commande = commande

        # Récupérer les infos du client
        cursor.execute("SELECT nom, telephone, adresse FROM Clients WHERE client_id = ?", (commande[1],))
        client = cursor.fetchone()
        if client:
            st.subheader("👤 Informations du client")
            st.write("**Nom :**", client[0])
            st.write("**Téléphone :**", client[1])
            st.write("**Adresse :**", client[2])

            # Enregistrer les informations du client dans la session
            st.session_state.client = client
        else:
            st.session_state.client = None

        # Récupérer les articles de la commande
        cursor.execute("""
            SELECT type_article, matiere, couleur, marque, taille, taches, prix, instructions_speciales
            FROM Articles 
            WHERE commande_id = ?""", (id_commande,))
        articles = cursor.fetchall()
        if articles:
            st.subheader("🧺 Détail de la commande")
            for art in articles:
                st.markdown(f"- **{art[0]}** | matière : {art[1]} | couleur : {art[2]} | marque : {art[3]} | taille : {art[4]} | taches : {art[5]} | prix : {art[6]} | instructions : {art[7]}")
            st.session_state.articles = articles
        else:
            st.session_state.articles = None

    else:
        st.error("❌ Commande non trouvée.")
        st.session_state.commande = None
        st.session_state.client = None
        st.session_state.articles = None

# Section pour le paiement
if st.session_state.commande and st.session_state.client:
    st.subheader("💰 Enregistrer le paiement")
    montant = st.session_state.commande[3]  # Montant de la commande
    mode = st.selectbox("Mode de paiement", ["Espèces", "Orange Money", "Mobile Money", "Carte Bancaire"])

    if st.button("Valider le paiement"):
        date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO Paiement (id_commande, montant, date_paiement, mode_paiement)
            VALUES (?, ?, ?, ?)""",
            (st.session_state.commande[0], montant, date_paiement, mode))
        conn.commit()

        # Ajouter le paiement à la session
        st.session_state.paiements.append({
            "id_commande": st.session_state.commande[0],
            "montant": montant,
            "date_paiement": date_paiement,
            "mode_paiement": mode
        })

        st.success("✅ Paiement enregistré avec succès.")

        # Facture
        st.subheader("🧾 Facture")
        st.write(f"Facture pour la commande **#{st.session_state.commande[0]}**")
        st.write("**Date de paiement :**", date_paiement)
        st.write("**Montant payé :**", montant)
        st.write("**Mode de paiement :**", mode)

        # Affichage des informations du client
        st.write("**Client :**", st.session_state.client[0])
        st.write("**Téléphone :**", st.session_state.client[1])
        st.write("**Adresse :**", st.session_state.client[2])

        # Détails des articles
        if st.session_state.articles:
            st.write("**Détails des articles :**")
            for art in st.session_state.articles:
                st.write(f"- {art[0]} | Tache : {art[5]} | Prix : {art[6]}")
        else:
            st.write("Aucun article pour cette commande.")

# Affichage de la liste des paiements
st.subheader("🧾 Liste des paiements effectués")
if st.session_state.paiements:
    for paiement in st.session_state.paiements:
        st.write(f"**Commande #{paiement['id_commande']}** - Montant : {paiement['montant']} - Date : {paiement['date_paiement']} - Mode : {paiement['mode_paiement']}")
else:
    st.write("Aucun paiement effectué pour le moment.")

