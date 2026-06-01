import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import re
import fitz  # PyMuPDF

st.set_page_config(page_title="Audit Renault", layout="wide", page_icon="🚧")

st.title("🚧 Audit Visite Terrain Entreprises Extérieures")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Renault_2024.svg/2560px-Renault_2024.svg.png", width=180)
    st.title("Navigation")
    page = st.radio("Aller à :", ["📤 Nouvel Audit", "📊 Dashboard", "📜 Historique"])

# ====================== DATA ======================
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

# ====================== PDF to Text ======================
def pdf_to_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
        
        text = page.get_text("text")
        full_text += text + "\n"
    return full_text, images

# ====================== Détections simples ======================
def detect_site(text):
    text_lower = text.lower()
    if "lardy" in text_lower or "hardy" in text_lower:
        return "CTL"
    elif "aubevoye" in text_lower:
        return "CTA"
    elif "guyancourt" in text_lower:
        return "TCR"
    return "INCONNU"

def detect_entreprise(text):
    text_upper = text.upper()
    if "EIFFAGE" in text_upper or "CHEMISY" in text_upper:
        return "EIFFAGE"
    elif "ITG" in text_upper:
        return "ITG C Environnement"
    return "INCONNU"

def count_yes_no(text):
    text_upper = text.upper()
    oui = len(re.findall(r'OUI|X\s*OUI', text_upper))
    non = len(re.findall(r'NON|X\s*NON', text_upper))
    return max(oui, 1), max(non, 0)

# ====================== MAIN ======================
if page == "📤 Nouvel Audit":
    st.header("📤 Upload du formulaire d'audit")

    uploaded_file = st.file_uploader("Déposez PDF ou image", 
                                     type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file:
        with st.spinner("Traitement du document..."):
            try:
                if uploaded_file.type == "application/pdf":
                    pdf_bytes = uploaded_file.read()
                    full_text, images = pdf_to_text(pdf_bytes)
                    for i, img in enumerate(images):
                        st.image(img, caption=f"Page {i+1}", use_column_width=True)
                else:
                    image = Image.open(uploaded_file)
                    st.image(image, use_column_width=True)
                    full_text = "Image uploadée (OCR non disponible sur cette version)"

                # Détections
                site = detect_site(full_text)
                entreprise = detect_entreprise(full_text)
                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
                date_str = date_match.group(1) if date_match else datetime.now().strftime("%d/%m/%Y")

                oui, non = count_yes_no(full_text)
                total = oui + non
                conformite = round((oui / total * 100), 1) if total > 0 else 0.0

                # Affichage
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Site", site)
                with col2: st.metric("Entreprise", entreprise)
                with col3: st.metric("Date", date_str)
                with col4: st.metric("Conformité", f"{conformite}%")

                st.subheader("Texte extrait")
                st.text_area("Contenu détecté", full_text[:1500] + "..." if len(full_text) > 1500 else full_text, height=300)

                # Sauvegarde
                with st.form("save_audit"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        site_f = st.text_input("Site", site)
                        bat = st.text_input("Bâtiment", "Bâtiment 125")
                        ent_f = st.text_input("Entreprise", entreprise)
                    with col_b:
                        charge = st.text_input("Chargé d'affaires", "Appalina W.")
                        date_f = st.date_input("Date", datetime.now())

                    if st.form_submit_button("💾 Enregistrer"):
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
                        st.success("Audit enregistré !")
                        st.balloons()

            except Exception as e:
                st.error(f"Erreur : {str(e)}")
                st.info("Essaie avec un PDF plus propre ou contacte-moi.")

elif page == "📊 Dashboard":
    df = load_history()
    if not df.empty:
        st.header("📊 Dashboard")
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Audits", len(df))
        with c2: st.metric("Conformité Moy.", f"{df['conformite_pct'].mean():.1f}%")
        with c3: st.metric("Sites", df['site'].nunique())
        with c4: st.metric("Entreprises", df['entreprise'].nunique())

        st.bar_chart(df.groupby("entreprise")["conformite_pct"].mean())
        st.dataframe(df.sort_values("date_audit", ascending=False))
    else:
        st.info("Aucun audit pour le moment.")

elif page == "📜 Historique":
    df = load_history()
    if not df.empty:
        st.dataframe(df.sort_values("date_audit", ascending=False), use_container_width=True)
    else:
        st.info("Historique vide.")

st.caption("Audit Renault • Version Cloud Stable v1.3")
