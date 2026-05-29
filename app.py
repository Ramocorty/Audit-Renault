import os
import re
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from pypdf import PdfReader

# =========================================================
# CONFIGURATION GENERALE
# =========================================================

st.set_page_config(
    page_title="Audit Conformité Renault - MVP",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"
LOGO_FILE = "nouveau_logo_renault.webp"   # Mets ce fichier dans ton repo GitHub

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
    background: linear-gradient(180deg, #1f2430 0%, #2b3140 45%, #394258 100%);
    color: white;
}

html, body, [class*="css"] {
    font-family: Arial, sans-serif;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.15rem;
}

.sub-title {
    font-size: 1rem;
    color: #d1d5db;
    margin-bottom: 1rem;
}

.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 22px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 28px rgba(0,0,0,0.18);
    margin-bottom: 1rem;
    color: white;
}

.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.08) 100%);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 8px 22px rgba(0,0,0,0.16);
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

.small-note {
    color: #d1d5db;
    font-size: 0.88rem;
}

.nav-box {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 0.5rem;
    margin-bottom: 1rem;
}

.bottom-nav {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 0.7rem 0.8rem;
    margin-top: 1rem;
    box-shadow: 0 8px 22px rgba(0,0,0,0.14);
}

.stButton > button {
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.12);
}

.stDownloadButton > button {
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%) !important;
    color: white !important;
    font-weight: 700 !important;
}

div[data-baseweb="select"] > div,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    border-radius: 12px !important;
}

[data-testid="stRadio"] label, 
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label {
    color: white !important;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: inherit;
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
        "statut": "statut",
        "objets_observes": "objets_observes",
        "nb_humains": "nb_humains"
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
            "audits_jour": 0,
            "audits_semaine": 0,
            "audits_mois": 0
        }

    df2 = df.copy()
    df2["date_audit"] = pd.to_datetime(df2["date_audit"], errors="coerce")

    total = len(df2)
    conformes = (df2["conformite"] == "Conforme").sum()
    non_conformes = (df2["conformite"] == "Non conforme").sum()
    critiques = (df2["gravite"] == "Critique").sum()

    pct = round((conformes / total) * 100, 1) if total > 0 else 0.0

    now = pd.Timestamp.now()
    start_day = now.normalize()
    start_week = now.normalize() - pd.to_timedelta(now.weekday(), unit="D")
    start_month = pd.Timestamp(year=now.year, month=now.month, day=1)

    audits_jour = (df2["date_audit"] >= start_day).sum()
    audits_semaine = (df2["date_audit"] >= start_week).sum()
    audits_mois = (df2["date_audit"] >= start_month).sum()

    return {
        "total_audits": int(total),
        "conformes": int(conformes),
        "non_conformes": int(non_conformes),
        "pourcentage_conformite": pct,
        "critiques": int(critiques),
        "audits_jour": int(audits_jour),
        "audits_semaine": int(audits_semaine),
        "audits_mois": int(audits_mois)
    }

def render_logo():
    if os.path.exists(LOGO_FILE):
        c1, c2 = st.columns([1, 6])
        with c1:
            st.image(LOGO_FILE, width=90)
        with c2:
            st.markdown('<div class="main-title">Audit Conformité Renault</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-title">MVP mobile-first pour audits terrain, import formulaires et pilotage KPI.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="main-title">Audit Conformité Renault</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Ajoute le fichier nouveau_logo_renault.webp dans le repo pour afficher le logo.</div>', unsafe_allow_html=True)

def render_top_nav():
    st.markdown('<div class="nav-box">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠 Accueil", use_container_width=True):
            st.session_state["page"] = "Accueil"
            st.rerun()
    with c2:
        if st.button("📷 Audit", use_container_width=True):
            st.session_state["page"] = "Audit terrain"
            st.rerun()
    with c3:
        if st.button("📄 Import", use_container_width=True):
            st.session_state["page"] = "Import formulaire"
            st.rerun()
    with c4:
        if st.button("📊 KPI", use_container_width=True):
            st.session_state["page"] = "Dashboard"
            st.rerun()
    with c5:
        if st.button("🗺️ Carte", use_container_width=True):
            st.session_state["page"] = "Carte des sites"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_right_panel():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Actions rapides")
    st.write("Navigation simple pour mobile / terrain.")
    if st.button("Nouvel audit terrain", use_container_width=True, key="quick_audit"):
        st.session_state["page"] = "Audit terrain"
        st.rerun()
    if st.button("Importer un formulaire", use_container_width=True, key="quick_import"):
        st.session_state["page"] = "Import formulaire"
        st.rerun()
    if st.button("Voir les KPI", use_container_width=True, key="quick_kpi"):
        st.session_state["page"] = "Dashboard"
        st.rerun()
    if st.button("Voir la carte", use_container_width=True, key="quick_map"):
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
        if st.button("🏠", use_container_width=True, key="bottom_home"):
            st.session_state["page"] = "Accueil"
            st.rerun()
    with c2:
        if st.button("📷", use_container_width=True, key="bottom_audit"):
            st.session_state["page"] = "Audit terrain"
            st.rerun()
    with c3:
        if st.button("📄", use_container_width=True, key="bottom_import"):
            st.session_state["page"] = "Import formulaire"
            st.rerun()
    with c4:
        if st.button("📊", use_container_width=True, key="bottom_kpi"):
            st.session_state["page"] = "Dashboard"
            st.rerun()
    with c5:
        if st.button("🗺️", use_container_width=True, key="bottom_map"):
            st.session_state["page"] = "Carte des sites"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ETAT
# =========================================================

if "page" not in st.session_state:
    st.session_state["page"] = "Accueil"

df_audits = load_audits()

# =========================================================
# HEADER COMMUN
# =========================================================

render_logo()
render_top_nav()

# =========================================================
# ACCUEIL
# =========================================================

if st.session_state["page"] == "Accueil":
    left, right = st.columns([4, 1.25])

    with left:
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
            st.write("Photo chantier, parking, salle, site ou image uploadée, puis qualification de conformité.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📄 Import formulaire")
            st.write("Import PDF / Excel / CSV pour intégrer des audits déjà réalisés et alimenter les KPI.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🗺️ Aperçu des sites Renault")
        df_sites = pd.DataFrame([
            {"site": site, "latitude": coords["lat"], "longitude": coords["lon"]}
            for site, coords in SITES.items()
        ])
        st.map(df_sites)
        st.dataframe(df_sites, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        render_bottom_nav()

    with right:
        render_right_panel()

# =========================================================
# AUDIT TERRAIN
# =========================================================

elif st.session_state["page"] == "Audit terrain":
    left, right = st.columns([4, 1.25])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📷 Nouvel audit terrain")
        st.write("Version mobile-first : photo + objets observés + conformité + stockage CSV.")

        with st.form("audit_terrain_form"):
            col1, col2 = st.columns(2)

            with col1:
                site = st.selectbox("Site", list(SITES.keys()))
                type_espace = st.selectbox("Type d’espace", TYPES_ESPACE)
                zone = st.text_input("Zone / secteur")
                reference_local = st.text_input("Référence locale (bâtiment / salle / chantier / repère)")

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
                media_file = st.camera_input("Prendre une photo du site / chantier / salle / parking")
            elif media_mode == "Uploader une image":
                media_file = st.file_uploader("Uploader une image", type=["jpg", "jpeg", "png"])

            st.markdown("### Objets observés (analyse assistée)")
            objets_observes = st.multiselect(
                "Que vois-tu dans la photo / la zone auditée ?",
                OBJETS_OBSERVES
            )
            nb_humains = st.number_input("Nombre d’êtres humains observés", min_value=0, step=1)

            commentaire = st.text_area("Commentaire / observation")
            auditeur = st.text_input("Auditeur")
            action_immediate = st.text_area("Action immédiate / mesure conservatoire")

            submit_audit = st.form_submit_button("Enregistrer l’audit")

        if submit_audit:
            media_name = ""
            if media_file is not None:
                media_name = save_uploaded_file(media_file)

            row = {
                "id_audit": uuid.uuid4().hex[:8],
                "date_audit": datetime.now(),
                "site": site,
                "type_espace": type_espace,
                "zone": zone,
                "reference_local": reference_local,
                "mode_saisie": "terrain_photo" if media_name else "terrain_sans_photo",
                "media_nom": media_name,
                "source_document": "",
                "conformite": conformite,
                "gravite": gravite,
                "categorie": categorie,
                "commentaire": commentaire,
                "auditeur": auditeur,
                "action_immediate": action_immediate,
                "statut": statut,
                "objets_observes": ", ".join(objets_observes),
                "nb_humains": nb_humains,
                "synthèse_import": ""
            }

            append_audit(row)
            st.success("Audit enregistré avec succès ✅")
            st.rerun()

        st.markdown('<div class="small-note">Conseil MVP : les objets observés sont saisis manuellement ici. La vraie détection IA viendra dans une V2.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        render_bottom_nav()

    with right:
        render_right_panel()

# =========================================================
# IMPORT FORMULAIRE
# =========================================================

elif st.session_state["page"] == "Import formulaire":
    left, right = st.columns([4, 1.25])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📄 Import de formulaire d’audit")
        st.write("Uploader un PDF, un Excel ou un CSV. Le résultat sera stocké dans le CSV et intégré aux KPI.")

        uploaded_doc = st.file_uploader(
            "Uploader un document",
            type=["pdf", "csv", "xlsx", "xls"]
        )

        if uploaded_doc is not None:
            file_name = uploaded_doc.name.lower()

            # -------------------------------------------------
            # PDF
            # -------------------------------------------------
            if file_name.endswith(".pdf"):
                pdf_saved_name = save_uploaded_file(uploaded_doc)
                uploaded_doc.seek(0)
                pdf_text = parse_pdf_text(uploaded_doc)

                st.markdown("### Texte extrait du PDF")
                st.text_area("Aperçu du PDF", pdf_text[:5000], height=250)

                parsed = extract_pdf_fields(pdf_text)

                st.markdown("### Vérifier / corriger les champs")
                with st.form("pdf_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        site = st.selectbox(
                            "Site",
                            list(SITES.keys()),
                            index=list(SITES.keys()).index(parsed["site"]) if parsed["site"] in SITES else 0
                        )
                        type_espace = st.selectbox(
                            "Type d’espace",
                            TYPES_ESPACE,
                            index=TYPES_ESPACE.index(parsed["type_espace"]) if parsed["type_espace"] in TYPES_ESPACE else 0
                        )
                        zone = st.text_input("Zone / secteur", value=parsed["zone"])
                        reference_local = st.text_input("Référence locale", value=parsed["reference_local"])

                    with col2:
                        conformite = st.selectbox(
                            "Conformité",
                            CONFORMITES,
                            index=CONFORMITES.index(parsed["conformite"]) if parsed["conformite"] in CONFORMITES else 0
                        )
                        gravite = st.selectbox(
                            "Gravité",
                            GRAVITES,
                            index=GRAVITES.index(parsed["gravite"]) if parsed["gravite"] in GRAVITES else 0
                        )
                        categorie = st.selectbox(
                            "Catégorie",
                            CATEGORIES,
                            index=CATEGORIES.index(parsed["categorie"]) if parsed["categorie"] in CATEGORIES else 0
                        )
                        statut = st.selectbox(
                            "Statut",
                            STATUTS,
                            index=STATUTS.index(parsed["statut"]) if parsed["statut"] in STATUTS else 0
                        )

                    commentaire = st.text_area("Commentaire / observation", value=parsed["commentaire"])
                    auditeur = st.text_input("Auditeur", value=parsed["auditeur"])
                    action_immediate = st.text_area("Action immédiate / mesure conservatoire")
                    objets_observes = st.multiselect("Objets observés si connus", OBJETS_OBSERVES)
                    nb_humains = st.number_input("Nombre d’êtres humains si connu", min_value=0, step=1)

                    submit_pdf = st.form_submit_button("Importer ce PDF")

                if submit_pdf:
                    row = {
                        "id_audit": uuid.uuid4().hex[:8],
                        "date_audit": datetime.now(),
                        "site": site,
                        "type_espace": type_espace,
                        "zone": zone,
                        "reference_local": reference_local,
                        "mode_saisie": "import_pdf",
                        "media_nom": "",
                        "source_document": pdf_saved_name,
                        "conformite": conformite,
                        "gravite": gravite,
                        "categorie": categorie,
                        "commentaire": commentaire,
                        "auditeur": auditeur,
                        "action_immediate": action_immediate,
                        "statut": statut,
                        "objets_observes": ", ".join(objets_observes),
                        "nb_humains": nb_humains,
                        "synthèse_import": pdf_text[:1000]
                    }

                    append_audit(row)
                    st.success("PDF importé avec succès ✅")
                    st.rerun()

            # -------------------------------------------------
            # CSV / EXCEL
            # -------------------------------------------------
            elif file_name.endswith(".csv") or file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                try:
                    if file_name.endswith(".csv"):
                        df_import = pd.read_csv(uploaded_doc)
                    else:
                        df_import = pd.read_excel(uploaded_doc)

                    st.markdown("### Aperçu du fichier")
                    st.dataframe(df_import.head(30), use_container_width=True)

                    if st.button("Importer ce fichier dans les audits"):
                        df_std = standardize_import_columns(df_import)
                        df_current = load_audits()
                        df_final = pd.concat([df_current, df_std], ignore_index=True)
                        save_audits(df_final)
                        st.success(f"{len(df_std)} ligne(s) importée(s) avec succès ✅")
                        st.rerun()

                except Exception as e:
                    st.error(f"Erreur lors de la lecture du fichier : {e}")

        st.markdown('<div class="small-note">Remarque : cette version lit correctement les PDF textuels. Pour de l’écriture manuscrite, il faudra brancher un OCR/IA externe en V2.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        render_bottom_nav()

    with right:
        render_right_panel()

# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state["page"] == "Dashboard":
    left, right = st.columns([4, 1.25])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 KPI et analyses")

        df = load_audits()

        if df.empty:
            st.info("Aucun audit enregistré pour le moment.")
        else:
            df["date_audit"] = pd.to_datetime(df["date_audit"], errors="coerce")

            colf1, colf2, colf3 = st.columns(3)
            with colf1:
                options_site = sorted([x for x in df["site"].dropna().unique() if str(x).strip() != ""])
                f_site = st.multiselect("Filtrer par site", options=options_site, default=options_site)

            with colf2:
                options_type = sorted([x for x in df["type_espace"].dropna().unique() if str(x).strip() != ""])
                f_type = st.multiselect("Filtrer par type d’espace", options=options_type, default=options_type)

            with colf3:
                options_conf = sorted([x for x in df["conformite"].dropna().unique() if str(x).strip() != ""])
                f_conf = st.multiselect("Filtrer par conformité", options=options_conf, default=options_conf)

            df_f = df.copy()
            if len(f_site) > 0:
                df_f = df_f[df_f["site"].isin(f_site)]
            if len(f_type) > 0:
                df_f = df_f[df_f["type_espace"].isin(f_type)]
            if len(f_conf) > 0:
                df_f = df_f[df_f["conformite"].isin(f_conf)]

            kpis = compute_kpis(df_f)

            m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-title">Audits</div><div class="metric-value">{kpis["total_audits"]}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-title">% conformité</div><div class="metric-value">{kpis["pourcentage_conformite"]}%</div></div>', unsafe_allow_html=True)
            with m3:
