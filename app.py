import os
import re
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Audit Conformité Renault - MVP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"
LOGO_FILE = "nouveau_logo_renault.webp"  # ajoute ce fichier dans ton repo GitHub

os.makedirs(UPLOAD_DIR, exist_ok=True)

SITES = {
    "Aubevoye": {"lat": 49.1720, "lon": 1.3380},
    "Lardy": {"lat": 48.5200, "lon": 2.2600},
    "Guyancourt": {"lat": 48.7610, "lon": 2.0820},
    "Villiers-Saint-Frédéric": {"lat": 48.8200, "lon": 1.9000},
    "Boulogne": {"lat": 48.8350, "lon": 2.2400},
}

TYPES_ESPACE = ["Parking", "Site", "Salle de réunion", "Chantier"]
CATEGORIES = ["Sécurité", "Propreté", "Maintenance", "Signalétique", "Accessibilité", "Autre"]
GRAVITES = ["Mineure", "Majeure", "Critique"]
CONFORMITES = ["Conforme", "Non conforme"]
STATUTS = ["Ouvert", "En cours", "Clos"]

OBJETS_OBSERVES = [
    "Être humain",
    "Table",
    "Chaise",
    "Salle de réunion",
    "PC",
    "Parking",
    "Barrière",
    "Lampe",
    "Chantier",
    "Chaîne",
    "Porte",
    "Fenêtre",
    "Véhicule",
    "Signalisation",
    "Autre"
]

AUDIT_COLUMNS = [
    "id_audit",
    "date_audit",
    "site",
    "type_espace",
    "zone",
    "reference_local",
    "mode_saisie",
    "media_nom",
    "source_document",
    "conformite",
    "gravite",
    "categorie",
    "commentaire",
    "auditeur",
    "action_immediate",
    "statut",
    "objets_observes",
    "nb_humains",
    "synthèse_import"
]

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #242734 0%, #2F3444 35%, #394258 100%);
    color: white;
}

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.2rem;
}

.sub-title {
    font-size: 1rem;
    color: #d1d5db;
    margin-bottom: 1.2rem;
}

.card {
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 22px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    margin-bottom: 1rem;
    color: white;
}

.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.08) 100%);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 8px 22px rgba(0,0,0,0.15);
    text-align: center;
    color: white;
}

.metric-title {
    font-size: 0.9rem;
    color: #d1d5db;
    margin-bottom: 0.2rem;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
}

.chip-green {
    background: #86efac;
    color: #14532d;
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}

.chip-red {
    background: #fca5a5;
    color: #7f1d1d;
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}

.chip-orange {
    background: #fdba74;
    color: #7c2d12;
    padding: 0.35rem 0.65rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}

.nav-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.6rem;
}

.small-note {
    color: #d1d5db;
    font-size: 0.88rem;
}

.stButton > button {
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.12);
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border-radius: 12px !important;
}

.bottom-nav {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 0.7rem 0.8rem;
    margin-top: 1rem;
    box-shadow: 0 8px 22px rgba(0,0,0,0.18);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# STOCKAGE
# =========================================================
def init_storage():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=AUDIT_COLUMNS).to_csv(DATA_FILE, index=False)

def load_audits():
    init_storage()
    df = pd.read_csv(DATA_FILE)
    if not df.empty and "date_audit" in df.columns:
        df["date_audit"] = pd.to_datetime(df["date_audit"], errors="coerce")
    return df

def save_audits(df):
    df2 = df.copy()
    if "date_audit" in df2.columns:
        df2["date_audit"] = pd.to_datetime(df2["date_audit"], errors="coerce")
        df2["date_audit"] = df2["date_audit"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df2.to_csv(DATA_FILE, index=False)

def append_audit(row_dict):
    df = load_audits()
    new_row = pd.DataFrame([row_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    save_audits(df)

# =========================================================
# OUTILS
# =========================================================
def save_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return ""
    filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filename

def parse_pdf_text(uploaded_pdf):
    try:
        reader = PdfReader(uploaded_pdf)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Erreur de lecture PDF : {e}"

def extract_pdf_fields(text)
