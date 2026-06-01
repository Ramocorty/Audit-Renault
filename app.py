import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Audit Renault", layout="wide")

st.title("🚧 Audit Visite Terrain Entreprises Extérieures")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Renault_2024.svg/2560px-Renault_2024.svg.png", width=180)
    page = st.radio("Menu", ["📤 Nouvel Audit", "📊 Dashboard", "📜 Historique"])

# Fichier historique
DATA_FILE = "audits_history.csv"

def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["date_audit", "site", "batiment", "entreprise", 
                                     "charge_affaires", "conformite_pct", "points_controles", 
                                     "conformes", "non_conformes", "file_name"])

def save_audit(data):
    df = load_history()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

if page == "📤 Nouvel Audit":
    st.header("Nouvel Audit")

    uploaded_file = st.file_uploader("Upload PDF ou Image", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        st.success("Fichier uploadé avec succès")
        
        full_text = st.text_area("Colle ici le texte du formulaire (après avoir fait l'OCR manuellement ou via un autre outil)", 
                                height=400, 
                                placeholder="Copie-colle le texte reconnu ici...")

        if full_text:
            col1, col2 = st.columns(2)
            with col1:
                site = st.text_input("Site", "CTL")
                batiment = st.text_input("Bâtiment", "Bâtiment 125")
                entreprise = st.text_input("Entreprise", "EIFFAGE")
            with col2:
                charge = st.text_input("Chargé d'affaires", "Appalina W.")
                date_audit = st.date_input("Date", datetime.now())

            oui = st.number_input("Nombre de OUI / Conforme", min_value=0, value=17)
            non = st.number_input("Nombre de NON", min_value=0, value=1)
            total = oui + non
            conformite = round((oui / total * 100), 1) if total > 0 else 0

            st.metric("Taux de Conformité", f"{conformite}%")

            if st.button("💾 Enregistrer l'Audit", type="primary"):
                data = {
                    "date_audit": str(date_audit),
                    "site": site,
                    "batiment": batiment,
                    "entreprise": entreprise,
                    "charge_affaires": charge,
                    "conformite_pct": conformite,
                    "points_controles": total,
                    "conformes": oui,
                    "non_conformes": non,
                    "file_name": uploaded_file.name
                }
                save_audit(data)
                st.success("Audit enregistré avec succès !")
                st.balloons()

elif page == "📊 Dashboard":
    df = load_history()
    if not df.empty:
        st.header("Dashboard")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Audits", len(df))
        with c2: st.metric("Conformité Moyenne", f"{df['conformite_pct'].mean():.1f}%")
        with c3: st.metric("Entreprises", df['entreprise'].nunique())

        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Aucun audit enregistré")

elif page == "📜 Historique":
    df = load_history()
    if not df.empty:
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Historique vide")

st.caption("Version Ultra Stable - 2026")
