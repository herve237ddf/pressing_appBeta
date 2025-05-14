import streamlit as st
import sqlite3
from datetime import datetime


# Configuration de la page
st.set_page_config(page_title="Nouveau paiement", layout="centered")
# Connexion à la base de données
conn = sqlite3.connect("pressing1.db")
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

st.title("💳 Paiement et Facturation")

# Rechercher une commande
st.subheader("Rechercher une commande")
id_commande = st.number_input("Entrer l'identifiant de la commande", min_value=1, step=1)

if st.button("Rechercher la commande"):
    # Récupérer les infos de la commande
    cursor.execute("SELECT * FROM Commandes WHERE commande_id = ?", (id_commande,))
    commande = cursor.fetchone()

    if commande:
        st.success("✅ Commande trouvée")
        st.write("**ID Commande :**", commande[0])
        st.write("**ID Client :**", commande[1])
        st.write("**Date de commande :**", commande[2])
        st.write("**Montant total :**", commande[3])
        st.write("**Statut :**", commande[4])

        # Récupérer les infos du client
        cursor.execute("SELECT nom, telephone, adresse FROM Clients WHERE client_id = ?", (commande[1],))
        client = cursor.fetchone()
        if client:
            st.subheader("👤 Informations du client")
            st.write("**Nom :**", client[0])
            st.write("**Téléphone :**", client[1])
            st.write("**Adresse :**", client[2])

        # Récupérer les articles de la commande
        cursor.execute("""
            SELECT matiere, couleur, marque, taille, taches, prix, instructions_speciales, type_article
            FROM Articles 
            WHERE commande_id = ?
        """, (id_commande,))
        articles = cursor.fetchall()
        if articles:
            st.subheader("🧺 Détail de la commande")
            for art in articles:
                st.markdown(f"- **{art[0]}** | couleur : {art[1]} | marque : {art[2]}| taille : {art[3]} | taches : {art[4]} | prix : {art[5]} | instructions : {art[6]} | type : {art[7]}")

        # Paiement
        st.subheader("💰 Enregistrer le paiement")
        montant = commande[6]
        mode = st.selectbox("Mode de paiement", ["Espèces", "Orange Money", "Mobile Money", "Carte Bancaire"])
        if st.button("Valider le paiement"):
            date_paiement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO Paiement (id_commande, montant, date_paiement, mode_paiement)
                VALUES (?, ?, ?, ?)""",
                (id_commande, montant, date_paiement, mode))
            conn.commit()
            st.success("✅ Paiement enregistré avec succès.")

            # Facture
            st.subheader("🧾 Facture")
            st.write(f"Facture pour la commande **#{id_commande}**")
            st.write("**Date de paiement :**", date_paiement)
            st.write("**Montant payé :**", montant)
            st.write("**Mode de paiement :**", mode)
    else:
        st.error("❌ Commande non trouvée.")

conn.close()
# from fpdf import FPDF


# # Générer la facture PDF
# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", size=12)
# pdf.cell(200, 10, txt=f"Facture - Commande #{id_commande}", ln=True, align='C')
# pdf.ln(10)
# pdf.cell(200, 10, txt=f"Date de paiement : {date_paiement}", ln=True)
# pdf.cell(200, 10, txt=f"Montant payé : {montant} FCFA", ln=True)
# pdf.cell(200, 10, txt=f"Mode de paiement : {mode}", ln=True)
# pdf.ln(10)
# pdf.cell(200, 10, txt=f"Client : {client[0]}", ln=True)
# pdf.cell(200, 10, txt=f"Téléphone : {client[1]}", ln=True)
# pdf.cell(200, 10, txt=f"Adresse : {client[2]}", ln=True)
# pdf.ln(10)
# pdf.cell(200, 10, txt="Détails des articles :", ln=True)

# for art in articles:
#     nom_article, qte, prix = art
#     pdf.cell(200, 10, txt=f"- {nom_article} | Qté : {qte} | PU : {prix} FCFA", ln=True)

# # Sauvegarde du PDF dans un buffer
# pdf_output = f"facture_commande_{id_commande}.pdf"
# pdf.output(pdf_output)

# # Lire le fichier PDF et proposer le téléchargement
# with open(pdf_output, "rb") as f:
#     pdf_bytes = f.read()
#     st.download_button(
#         label="📥 Télécharger la facture PDF",
#         data=pdf_bytes,
#         file_name=pdf_output,
#         mime="application/pdf"
#     )
