import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import easyocr
import numpy as np
import re

# PyMuPDF
import fitz  # doit être installé via pymupdf

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
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ====================== OCR ======================
@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['fr'], gpu=False)

def pdf_to_images(pdf_bytes):
    """Convert PDF to images using PyMuPDF"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Haute résolution
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def extract_text_from_image(image):
    reader = get_ocr_reader()
    result = reader.readtext(np.array(image), detail=0, paragraph=True)
    return " ".join(result)

# ====================== DÉTECTION ======================
def detect_site(text):
    mapping = {
        "lardy": "CTL", "hardy": "CTL",
        "aubevoye": "CTA", "guyancourt": "TCR",
        "flins": "FLI", "cléon": "CLE", "cleon": "CLE",
        "douai": "DOU"
    }
    text_lower = text.lower()
    for key, site in mapping.items():
        if key in text_lower:
            return site
    return "INCONNU"

def detect_entreprise(text):
    ent_list = ["EIFFAGE", "KES CHEMISY", "SPIE", "VINCI", "EQUANS", "SNEF", "ITG C", "ITGC"]
    text_upper = text.upper()
    for ent in ent_list:
        if ent in text_upper:
            return ent
    return "INCONNU"

def count_yes_no(text):
    text_upper = text.upper()
    oui = len(re.findall(r'\b(OUI|X\s*OUI|YES|☑)\b', text_upper))
    non = len(re.findall(r'\b(NON|X\s*NON|NO|☒)\b', text_upper))
    return max(oui, 1), max(non, 0)

# ====================== MAIN APP ======================
if page == "📤 Nouvel Audit":
    st.header("📤 Upload du formulaire d'audit")

    uploaded_file = st.file_uploader("Déposez votre PDF ou image (JPG/PNG)", 
                                     type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        with st.spinner("Analyse OCR en cours (peut prendre 15-25 secondes)..."):
            try:
                if uploaded_file.type == "application/pdf":
                    pdf_bytes = uploaded_file.read()
                    images = pdf_to_images(pdf_bytes)
                    full_text = ""
                    for i, img in enumerate(images):
                        st.image(img, caption=f"Page {i+1} traitée", use_column_width=True)
                        page_text = extract_text_from_image(img)
                        full_text += page_text + "\n"
                else:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Image analysée", use_column_width=True)
                    full_text = extract_text_from_image(image)

                # Détections
                site = detect_site(full_text)
                entreprise = detect_entreprise(full_text)
                
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
                date_str = date_match.group(1) if date_match else datetime.now().strftime("%d/%m/%Y")

                oui, non = count_yes_no(full_text)
                total = oui + non
                conformite = round((oui / total * 100), 1) if total > 0 else 0.0

                # KPI
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Site", site)
                with col2: st.metric("Entreprise", entreprise)
                with col3: st.metric("Date", date_str)
                with col4: st.metric("Conformité", f"{conformite}%")

                st.subheader("Texte extrait par OCR")
                st.text_area("OCR Result", full_text[:2000] + "..." if len(full_text) > 2000 else full_text, height=300)

                # Formulaire de sauvegarde
                with st.form("save_form"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        site_final = st.text_input("Site", value=site)
                        batiment = st.text_input("Bâtiment", value="Bâtiment 125")
                        entreprise_final = st.text_input("Entreprise", value=entreprise)
                    with col_b:
                        charge = st.text_input("Chargé d'affaires Renault", value="Appalina W.")
                        date_final = st.date_input("Date", datetime.now())

                    remarques = st.text_area("Remarques / Actions correctives", 
                        "Les intervenants n’ont pas suffisamment d’espace pour travailler...")

                    if st.form_submit_button("💾 Enregistrer l'Audit"):
                        data = {
                            "date_audit": str(date_final),
                            "site": site_final,
                            "batiment": batiment,
                            "entreprise": entreprise_final,
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

            except Exception as e:
                st.error(f"Erreur lors du traitement : {e}")

elif page == "📊 Dashboard":
    df = load_history()
    if not df.empty:
        st.header("📊 Tableau de Bord des Audits")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Audits", len(df))
        with c2: st.metric("Conformité Moyenne", f"{df['conformite_pct'].mean():.1f}%")
        with c3: st.metric("Sites", df['site'].nunique())
        with c4: st.metric("Entreprises", df['entreprise'].nunique())

        st.subheader("Conformité par Entreprise")
        st.bar_chart(df.groupby("entreprise")["conformite_pct"].mean())

        st.subheader("Historique complet")
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Aucun audit enregistré pour le moment.")

elif page == "📜 Historique":
    df = load_history()
    if not df.empty:
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Historique vide.")

st.caption("Audit Renault • EasyOCR + PyMuPDF • v1.2")
