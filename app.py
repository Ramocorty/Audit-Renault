import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import easyocr
import numpy as np
import re
from pdf2image import convert_from_bytes
import tempfile

st.set_page_config(page_title="Audit Renault - CTL", layout="wide")
st.title("🚧 Audit Visite Terrain Entreprises Extérieures")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Renault_2024.svg/2560px-Renault_2024.svg.png", width=200)
    st.title("Menu")
    page = st.radio("Navigation", ["📤 Nouvel Audit", "📊 Dashboard", "📜 Historique"])

# ====================== DATA STORAGE ======================
DATA_FILE = "audits_history.csv"

def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "date_audit", "site", "batiment", "entreprise", 
            "charge_affaires", "conformite_pct", "points_controles",
            "conformes", "non_conformes", "file_name"
        ])

def save_audit(data):
    df = load_history()
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ====================== OCR FUNCTIONS ======================
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['fr'], gpu=False)

def pdf_to_images(pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    images = convert_from_bytes(pdf_bytes, dpi=300)
    os.unlink(tmp_path)
    return images

def extract_text_from_image(image):
    reader = get_ocr_reader()
    result = reader.readtext(np.array(image), detail=0)
    return " ".join(result)

def detect_site(text):
    site_map = {
        "lardy": "CTL", "hardy": "CTL",
        "aubevoye": "CTA",
        "guyancourt": "TCR",
        "flins": "FLI",
        "cléon": "CLE", "cleon": "CLE",
        "douai": "DOU"
    }
    text_lower = text.lower()
    for key, site in site_map.items():
        if key in text_lower:
            return site
    return "INCONNU"

def detect_entreprise(text):
    entreprises = ["EIFFAGE", "KES CHEMISY", "SPIE", "VINCI", "EQUANS", "SNEF", "ITG C"]
    text_upper = text.upper()
    for ent in entreprises:
        if ent in text_upper:
            return ent
    return "INCONNU"

def count_yes_no(text):
    # Recherche des cases OUI/NON
    oui_count = len(re.findall(r'\b(OUI|yes|x\s+oui)\b', text.upper()))
    non_count = len(re.findall(r'\b(NON|no|x\s+non)\b', text.upper()))
    return oui_count, non_count

# ====================== MAIN APP ======================
if page == "📤 Nouvel Audit":
    st.header("Upload du formulaire d'audit")

    uploaded_file = st.file_uploader("Déposez votre PDF ou image (JPG/PNG)", 
                                   type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        with st.spinner("Analyse OCR en cours..."):
            if uploaded_file.type == "application/pdf":
                images = pdf_to_images(uploaded_file.read())
                full_text = ""
                for img in images:
                    full_text += extract_text_from_image(img) + "\n"
                    st.image(img, caption="Page traitée", use_column_width=True)
            else:
                image = Image.open(uploaded_file)
                full_text = extract_text_from_image(image)
                st.image(image, caption="Image analysée", use_column_width=True)

            # Extraction intelligente
            site = detect_site(full_text)
            entreprise = detect_entreprise(full_text)
            
            # Recherche de dates
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            date_str = date_match.group(1) if date_match else datetime.now().strftime("%d/%m/%Y")

            oui, non = count_yes_no(full_text)
            total_points = oui + non
            conformite = round((oui / total_points * 100), 2) if total_points > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Site", site)
            with col2:
                st.metric("Entreprise", entreprise)
            with col3:
                st.metric("Date", date_str)
            with col4:
                st.metric("Conformité", f"{conformite}%", delta=None)

            st.subheader("Détails extraits")
            st.text_area("Texte OCR complet", full_text[:2000], height=300)

            # Formulaire de validation / correction
            with st.form("save_audit"):
                col_a, col_b = st.columns(2)
                with col_a:
                    site_corr = st.text_input("Site", value=site)
                    batiment = st.text_input("Bâtiment", value="Bâtiment 125")
                    entreprise_corr = st.text_input("Entreprise", value=entreprise)
                with col_b:
                    charge = st.text_input("Chargé d'affaires Renault", value="Appalina W.")
                    date_corr = st.date_input("Date", value=datetime.now())

                remarques = st.text_area("Remarques / Actions correctives", 
                                       "Les intervenants n'ont pas suffisamment d'espace...")

                submitted = st.form_submit_button("💾 Enregistrer l'audit")
                if submitted:
                    audit_data = {
                        "date_audit": str(date_corr),
                        "site": site_corr,
                        "batiment": batiment,
                        "entreprise": entreprise_corr,
                        "charge_affaires": charge,
                        "conformite_pct": conformite,
                        "points_controles": total_points,
                        "conformes": oui,
                        "non_conformes": non,
                        "file_name": uploaded_file.name
                    }
                    save_audit(audit_data)
                    st.success("Audit enregistré avec succès !")
                    st.balloons()

elif page == "📊 Dashboard":
    st.header("Dashboard KPI Audits")
    df = load_history()
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Audits totaux", len(df))
        with col2:
            st.metric("Conformité moyenne", f"{df['conformite_pct'].mean():.1f}%")
        with col3:
            st.metric("Sites couverts", df['site'].nunique())
        with col4:
            st.metric("Entreprises auditées", df['entreprise'].nunique())

        st.subheader("Conformité par Entreprise")
        fig = pd.DataFrame(df.groupby('entreprise')['conformite_pct'].mean()).reset_index()
        st.bar_chart(fig.set_index('entreprise'))

        st.subheader("Historique détaillé")
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)

        # Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger Excel", csv, "audits_renault.csv", "text/csv")
    else:
        st.info("Aucun audit enregistré pour le moment.")

elif page == "📜 Historique":
    df = load_history()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Historique vide.")

st.caption("Application Audit Renault • OCR EasyOCR • Version 1.0")
