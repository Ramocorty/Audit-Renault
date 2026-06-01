import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from PIL import Image

st.set_page_config(page_title="Audit Renault", layout="wide", page_icon="🚧")

st.title("🚧 Audit Visite Terrain Entreprises Extérieures - Renault")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Renault_2024.svg/2560px-Renault_2024.svg.png", width=180)
    st.title("Navigation")
    page = st.radio("Aller à :", ["📤 Nouvel Audit", "📊 Dashboard", "📜 Historique"])

# ====================== DATA STORAGE ======================
DATA_FILE = "audits_history.csv"

def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        cols = ["date_audit", "site", "batiment", "entreprise", "charge_affaires",
                "conformite_pct", "points_controles", "conformes", "non_conformes", "file_name"]
        return pd.DataFrame(columns=cols)

def save_audit(data):
    df = load_history()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ====================== DÉTECTIONS SIMPLES ======================
def detect_site(text):
    text_lower = text.lower()
    if any(x in text_lower for x in ["lardy", "hardy"]):
        return "CTL"
    return "INCONNU"

def detect_entreprise(text):
    text_upper = text.upper()
    if "EIFFAGE" in text_upper:
        return "EIFFAGE"
    if "ITG" in text_upper:
        return "ITG C"
    return "INCONNU"

def count_yes_no(text):
    text_upper = text.upper()
    oui = len(re.findall(r'OUI|X', text_upper))
    non = len(re.findall(r'NON', text_upper))
    return max(oui, 1), max(non, 0)

# ====================== MAIN ======================
if page == "📤 Nouvel Audit":
    st.header("📤 Nouvel Audit")

    uploaded_file = st.file_uploader("Déposez votre PDF ou Image", 
                                     type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        st.info("🔍 Analyse en cours... (version légère)")

        # Pour PDF : on ne peut pas extraire le texte sans lib lourde → on demande à l'utilisateur de copier-coller
        if uploaded_file.type == "application/pdf":
            st.warning("📄 PDF détecté. Sur Streamlit Cloud, l'extraction automatique est limitée.")
            st.info("➡️ Copiez-collez le texte du PDF dans le champ ci-dessous :")
            full_text = st.text_area("Collez le texte OCR ici :", height=300)
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Image uploadée", use_column_width=True)
            full_text = st.text_area("Collez le texte reconnu (si vous avez fait un OCR ailleurs) :", height=200)

        if full_text:
            site = detect_site(full_text)
            entreprise = detect_entreprise(full_text)
            
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            date_str = date_match.group(1) if date_match else datetime.now().strftime("%d/%m/%Y")

            oui, non = count_yes_no(full_text)
            total = oui + non
            conformite = round((oui / total * 100), 1) if total > 0 else 0.0

            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Site", site)
            with col2: st.metric("Entreprise", entreprise)
            with col3: st.metric("Date", date_str)
            with col4: st.metric("Conformité", f"{conformite}%")

            with st.form("save_audit"):
                col_a, col_b = st.columns(2)
                with col_a:
                    site_f = st.text_input("Site", value=site)
                    bat = st.text_input("Bâtiment", "Bâtiment 125")
                    ent_f = st.text_input("Entreprise", value=entreprise)
                with col_b:
                    charge = st.text_input("Chargé d'affaires", "Appalina W.")
                    date_f = st.date_input("Date", datetime.now())

                if st.form_submit_button("💾 Enregistrer l'Audit"):
                    data = {
                        "date_audit": str(date_f),
                        "site": site_f,
                        "batiment": bat,
                        "entreprise": ent_f,
                        "charge_affaires": charge,
                        "conformite_pct": conformite,
                        "points_controles": total,
                        "conformes": oui,
                        "non_conformes": non,
                        "file_name": uploaded_file.name
                    }
                    save_audit(data)
                    st.success("✅ Audit enregistré avec succès !")
                    st.balloons()

elif page == "📊 Dashboard":
    df = load_history()
    if not df.empty:
        st.header("📊 Dashboard")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Audits", len(df))
        with c2: st.metric("Conformité Moyenne", f"{df['conformite_pct'].mean():.1f}%")
        with c3: st.metric("Sites", df['site'].nunique())
        with c4: st.metric("Entreprises", df['entreprise'].nunique())

        st.bar_chart(df.groupby("entreprise")["conformite_pct"].mean())
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Aucun audit enregistré pour le moment.")

elif page == "📜 Historique":
    df = load_history()
    if not df.empty:
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Historique vide.")

st.caption("Audit Renault • Version Streamlit Cloud Stable v1.4")
