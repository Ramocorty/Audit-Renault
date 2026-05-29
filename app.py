import os
import re
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader
from streamlit_option_menu import option_menu

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

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Coordonnées indicatives / à ajuster si besoin
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
    "statut"
]

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
/* Fond global */
.stApp {
    background: linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
}

/* Titre */
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #18212f;
    margin-bottom: 0.15rem;
}
.sub-title {
    font-size: 1rem;
    color: #5b6472;
    margin-bottom: 1.2rem;
}

/* Cartes */
.card {
    background: white;
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border: 1px solid #e8edf3;
    margin-bottom: 1rem;
}
.metric-card {
    background: white;
    border-radius: 18px;
    padding: 0.9rem 1rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    border: 1px solid #e8edf3;
    text-align: center;
}
.metric-title {
    font-size: 0.9rem;
    color: #5b6472;
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: #111827;
}

/* Chips */
.chip-green {
    background: #dcfce7;
    color: #166534;
    padding: 0.30rem 0.60rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}
.chip-red {
    background: #fee2e2;
    color: #991b1b;
    padding: 0.30rem 0.60rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}
.chip-orange {
    background: #ffedd5;
    color: #9a3412;
    padding: 0.30rem 0.60rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    display: inline-block;
}

/* Menu horizontal */
div[data-testid="stHorizontalBlock"] .nav-item {
    border-radius: 14px !important;
}

/* Boutons */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    border-radius: 12px !important;
}

/* Bloc de navigation basse */
.bottom-nav {
    background: white;
    border: 1px solid #e8edf3;
    border-radius: 18px;
    padding: 0.6rem 0.8rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    margin-top: 1rem;
}
.small-note {
    color: #6b7280;
    font-size: 0.88rem;
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
    if not df.empty:
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

def extract_pdf_fields(text):
    def find_value(pattern, default=""):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else default

    site = find_value(r"site\s*[:\-]\s*(.+)")
    type_espace = find_value(r"type(?:\s+d['’]espace)?\s*[:\-]\s*(.+)")
    zone = find_value(r"zone\s*[:\-]\s*(.+)")
    reference_local = find_value(r"(?:référence|reference|bâtiment|batiment|salle)\s*[:\-]\s*(.+)")
    conformite = find_value(r"conformit[eé]\s*[:\-]\s*(.+)")
    gravite = find_value(r"gravit[eé]\s*[:\-]\s*(.+)")
    categorie = find_value(r"cat[eé]gorie\s*[:\-]\s*(.+)")
    commentaire = find_value(r"(?:commentaire|observation|remarque)\s*[:\-]\s*(.+)")
    auditeur = find_value(r"auditeur\s*[:\-]\s*(.+)")
    statut = find_value(r"statut\s*[:\-]\s*(.+)")

    site = site if site in SITES else ""
    type_espace = type_espace if type_espace in TYPES_ESPACE else ""
    conformite = conformite if conformite in CONFORMITES else ""
    gravite = gravite if gravite in GRAVITES else ""
    categorie = categorie if categorie in CATEGORIES else ""
    statut = statut if statut in STATUTS else "Ouvert"

    return {
        "site": site,
        "type_espace": type_espace,
        "zone": zone,
        "reference_local": reference_local,
        "conformite": conformite,
        "gravite": gravite,
        "categorie": categorie,
        "commentaire": commentaire,
        "auditeur": auditeur,
        "statut": statut
    }

def standardize_import_columns(df_import):
    mapping = {
        "date": "date_audit",
        "date audit": "date_audit",
        "date_audit": "date_audit",
        "site": "site",
        "type espace": "type_espace",
        "type_espace": "type_espace",
        "zone": "zone",
        "référence": "reference_local",
        "reference": "reference_local",
        "bâtiment": "reference_local",
        "batiment": "reference_local",
        "salle": "reference_local",
        "conformité": "conformite",
        "conformite": "conformite",
        "gravité": "gravite",
        "gravite": "gravite",
        "catégorie": "categorie",
        "categorie": "categorie",
        "commentaire": "commentaire",
        "observation": "commentaire",
        "auditeur": "auditeur",
        "statut": "statut"
    }

    df = df_import.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    rename_dict = {}
    for c in df.columns:
        if c in mapping:
            rename_dict[c] = mapping[c]

    df = df.rename(columns=rename_dict)

    for col in AUDIT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["mode_saisie"] = "import_fichier"

    if "id_audit" not in df.columns or df["id_audit"].eq("").all():
        df["id_audit"] = [uuid.uuid4().hex[:8] for _ in range(len(df))]

    if "date_audit" in df.columns:
        df["date_audit"] = pd.to_datetime(df["date_audit"], errors="coerce")
        df["date_audit"] = df["date_audit"].fillna(pd.Timestamp.now())
    else:
        df["date_audit"] = pd.Timestamp.now()

    if "statut" not in df.columns:
        df["statut"] = "Ouvert"
    else:
        df["statut"] = df["statut"].replace("", "Ouvert")

    return df[AUDIT_COLUMNS]

def compute_kpis(df):
    if df.empty:
        return {
            "total_audits": 0,
            "conformes": 0,
            "non_conformes": 0,
            "pourcentage_conformite": 0.0,
            "critiques": 0,
            "semaine": 0,
            "mois": 0
        }

    df2 = df.copy()
    df2["date_audit"] = pd.to_datetime(df2["date_audit"], errors="coerce")

    total = len(df2)
    conformes = (df2["conformite"] == "Conforme").sum()
    non_conformes = (df2["conformite"] == "Non conforme").sum()
    critiques = (df2["gravite"] == "Critique").sum()

    pct = round((conformes / total) * 100, 1) if total > 0 else 0.0

    now = pd.Timestamp.now()
    start_week = now.normalize() - pd.to_timedelta(now.weekday(), unit="D")
    start_month = pd.Timestamp(year=now.year, month=now.month, day=1)

    audits_week = (df2["date_audit"] >= start_week).sum()
    audits_month = (df2["date_audit"] >= start_month).sum()

    return {
        "total_audits": int(total),
        "conformes": int(conformes),
        "non_conformes": int(non_conformes),
        "pourcentage_conformite": pct,
        "critiques": int(critiques),
        "semaine": int(audits_week),
        "mois": int(audits_month)
    }

def render_header(title, subtitle):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)

def render_right_panel():
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Actions rapides")
        st.write("Accès rapide aux grandes zones du MVP.")
        if st.button("📷 Nouvel audit terrain", use_container_width=True):
            st.session_state["page"] = "Audit terrain"
            st.rerun()
        if st.button("📄 Importer un formulaire", use_container_width=True):
            st.session_state["page"] = "Import formulaire"
            st.rerun()
        if st.button("📊 Voir les KPI", use_container_width=True):
            st.session_state["page"] = "Dashboard"
            st.rerun()
        if st.button("🗺️ Voir la carte", use_container_width=True):
            st.session_state["page"] = "Carte des sites"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🏷️ Légende")
        st.markdown('<span class="chip-green">Conforme</span>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<span class="chip-red">Non conforme</span>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<span class="chip-orange">Critique</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_bottom_nav():
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠\nAccueil", use_container_width=True):
            st.session_state["page"] = "Accueil"
            st.rerun()
    with c2:
        if st.button("📷\nAudit", use_container_width=True):
            st.session_state["page"] = "Audit terrain"
            st.rerun()
    with c3:
        if st.button("📄\nImport", use_container_width=True):
            st.session_state["page"] = "Import formulaire"
            st.rerun()
    with c4:
        if st.button("📊\nKPI", use_container_width=True):
            st.session_state["page"] = "Dashboard"
            st.rerun()
    with c5:
        if st.button("🗺️\nCarte", use_container_width=True):
            st.session_state["page"] = "Carte des sites"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# NAVIGATION PRINCIPALE
# =========================================================
if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

selected = option_menu(
    menu_title=None,
    options=["Accueil", "Audit terrain", "Import formulaire", "Dashboard", "Carte des sites"],
    icons=["house", "camera", "file-earmark-arrow-up", "bar-chart", "geo-alt"],
    orientation="horizontal",
    default_index=["Accueil", "Audit terrain", "Import formulaire", "Dashboard", "Carte des sites"].index(st.session_state["page"]),
    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "#0f766e", "font-size": "18px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px 6px",
            "padding": "10px 16px",
            "border-radius": "14px",
            "background-color": "#ffffff",
            "color": "#111827",
            "font-weight": "700",
            "box-shadow": "0 4px 14px rgba(0,0,0,0.05)"
        },
        "nav-link-selected": {
            "background-color": "#0f766e",
            "color": "white"
        }
    }
)

st.session_state["page"] = selected
page = st.session_state["page"]

# =========================================================
# DONNEES
# =========================================================
df_audits = load_audits()

# =========================================================
# PAGES
# =========================================================

if page == "Accueil":
    left, right = st.columns([4, 1.25])

    with left:
        render_header("📋 Audit de conformité multi-sites", "Une version plus visuelle, plus mobile et plus produit.")

        kpis = compute_kpis(df_audits)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Audits</div><div class="metric-value">{kpis["total_audits"]}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">% conformité</div><div class="metric-value">{kpis["pourcentage_conformite"]}%</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Non conformes</div><div class="metric-value">{kpis["non_conformes"]}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Critiques</div><div class="metric-value">{kpis["critiques"]}</div></div>', unsafe_allow_html=True)

        st.write("")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📷 Audit terrain")
            st.write("Photo depuis téléphone ou image uploadée, avec qualification immédiate.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📄 Import formulaire")
            st.write("Import PDF / Excel / CSV pour intégrer des audits déjà réalisés.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🗺️ Vue rapide des sites")
        df_sites = pd.DataFrame([
            {"site": site, "latitude": coords["lat"], "longitude": coords["lon"]}
            for site, coords in SITES.items()
        ])
        st.map(df_sites)
        st.markdown('</div>', unsafe_allow_html=True)

        render_bottom_nav()

    with right:
        render_right_panel()

elif page == "Audit terrain":
    left, right = st.columns([4, 1.25])

    with left:
        render_header("📷 Audit terrain", "Prendre une photo et qualifier un audit sur parking, site, salle ou chantier.")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("audit_terrain_form"):
            col1, col2 = st.columns(2)

            with col1:
                site = st.selectbox("Site", list(SITES.keys()))
                type_espace = st.selectbox("Type d’espace", TYPES_ESPACE)
                zone = st.text_input("Zone / secteur")
                reference_local = st.text_input("Référence locale")

            with col2:
                conformite = st.radio("Conformité", CONFORMITES, horizontal=True)
                gravite = st.selectbox("Gravité", GRAVITES)
                categorie = st.selectbox("Catégorie", CATEGORIES)
                statut = st.selectbox("Statut", STATUTS, index=0)

            st.markdown("### Média")
            media_mode = st.radio(
                "Choix du média",
                ["Prendre une photo", "Uploader une image", "Aucun média"],
                horizontal=True
            )

            media_file = None
            if media_mode == "Prendre une photo":
                media_file = st.camera_input("Prendre une photo du chantier / site / anomalie")
            elif media_mode == "Uploader une image":
                media_file = st.file_uploader("Uploader une image", type=["jpg", "jpeg", "png"])

            commentaire = st.text_area("Commentaire / observation")
            auditeur = st.text_input("Auditeur")
            action_immediate = st.text_area("Action immédiate / mesure conservatoire")

