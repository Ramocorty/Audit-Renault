import os
import uuid
from datetime import datetime, date

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# CONFIGURATION GENERALE
# =========================================================
st.set_page_config(
    page_title="Audit Renault MVP",
    page_icon="📋",
    layout="wide"
)

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #ffffff;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    }
    .small-text {
        color: #6b7280;
        font-size: 0.9rem;
    }
    .green-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background-color: #dcfce7;
        color: #166534;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .orange-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background-color: #ffedd5;
        color: #9a3412;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .red-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background-color: #fee2e2;
        color: #991b1b;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTES
# =========================================================

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Coordonnées indicatives à ajuster/valider si besoin
# Elles servent uniquement à afficher une carte MVP.
SITES = {
    "Aubevoye": {"lat": 49.1720, "lon": 1.3380},
    "Lardy": {"lat": 48.5200, "lon": 2.2600},
    "Guyancourt": {"lat": 48.7610, "lon": 2.0820},
    "Villiers-Saint-Frédéric": {"lat": 48.8200, "lon": 1.9000},
    "Boulogne": {"lat": 48.8350, "lon": 2.2400},  # à ajuster/valider
}

TYPES_ESPACE = ["Parking", "Site", "Salle de réunion", "Chantier"]
CATEGORIES = ["Sécurité", "Propreté", "Maintenance", "Signalétique", "Accessibilité", "Autre"]
GRAVITES = ["Mineure", "Majeure", "Critique"]
CONFORMITES = ["Conforme", "Non conforme"]
STATUTS = ["Ouvert", "En cours", "Clos"]

COLONNES_AUDIT = [
    "id_audit",
    "date_audit",
    "site",
    "type_espace",
    "zone",
    "reference_local",
    "mode_saisie",
    "photo_nom",
    "conformite",
    "gravite",
    "categorie",
    "commentaire",
    "auditeur",
    "action_immediate",
    "statut"
]

# =========================================================
# OUTILS
# =========================================================

def init_data_file():
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=COLONNES_AUDIT)
        df_init.to_csv(DATA_FILE, index=False)

def load_audits():
    init_data_file()
    df = pd.read_csv(DATA_FILE)
    if not df.empty and "date_audit" in df.columns:
        df["date_audit"] = pd.to_datetime(df["date_audit"], errors="coerce")
    return df

def save_audits(df):
    df_to_save = df.copy()
    if "date_audit" in df_to_save.columns:
        df_to_save["date_audit"] = pd.to_datetime(df_to_save["date_audit"], errors="coerce")
        df_to_save["date_audit"] = df_to_save["date_audit"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df_to_save.to_csv(DATA_FILE, index=False)

def append_audit(row_dict):
    df = load_audits()
    new_row = pd.DataFrame([row_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    save_audits(df)

def standardize_import_columns(df_import):
    """
    Essaie de renommer quelques colonnes courantes pour faciliter l'import.
    """
    mapping = {
        "date": "date_audit",
        "date audit": "date_audit",
        "date_audit": "date_audit",
        "site": "site",
        "type espace": "type_espace",
        "type_espace": "type_espace",
        "zone": "zone",
        "batiment": "reference_local",
        "salle": "reference_local",
        "reference": "reference_local",
        "conformite": "conformite",
        "gravite": "gravite",
        "categorie": "categorie",
        "commentaire": "commentaire",
        "auditeur": "auditeur",
        "statut": "statut"
    }

    df2 = df_import.copy()
    df2.columns = [str(c).strip().lower() for c in df2.columns]

    renamed = {}
    for c in df2.columns:
        if c in mapping:
