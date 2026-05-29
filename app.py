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
    layout="wide"
)

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Coordonnées indicatives pour la carte
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
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #6b7280;
        margin-bottom: 1.2rem;
    }
    .section-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e5e7eb;
        padding: 0.9rem 1rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
    }
    .small-note {
        color: #6b7280;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION STOCKAGE
# =========================================================

def init_storage():
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=AUDIT_COLUMNS)
        df_init.to_csv(DATA_FILE, index=False)

def load_audits():
    init_storage()
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
    """
    Détection simple de champs dans un PDF textuel.
    Si le PDF est peu structuré, l'utilisateur corrigera à la main.
    """
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

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📋 Audit Conformité")
page = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Audit terrain", "Import formulaire", "Dashboard", "Carte des sites"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "MVP de démonstration : stockage local CSV + fichiers uploadés. "
    "Pour un usage réel entreprise, prévoir une base et un stockage sécurisé."
)

# =========================================================
# CHARGEMENT DONNEES
# =========================================================

df_audits = load_audits()

# =========================================================
# PAGE ACCUEIL
# =========================================================

if page == "Accueil":
    st.markdown('<div class="main-title">📋 Audit de conformité multi-sites</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">MVP pour audit terrain par photo, import de formulaires et pilotage des conformités.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📷 Audit terrain")
        st.write(
            "Prendre une photo d’un parking, d’un site, d’une salle de réunion ou d’un chantier, "
            "puis qualifier la conformité et enregistrer l’audit."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📄 Import de formulaire")
        st.write(
            "Uploader un formulaire d’audit PDF, Excel ou CSV, puis intégrer les résultats dans le pilotage KPI."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### KPI pilotés")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box">✅ % conformité</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box">📆 Audits par semaine / mois</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box">🚨 Non-conformités critiques</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-box">📍 Répartition par site</div>', unsafe_allow_html=True)

# =========================================================
# PAGE AUDIT TERRAIN
# =========================================================

elif page == "Audit terrain":
    st.markdown('<div class="main-title">📷 Audit terrain</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Photo chantier / salle / parking / site + qualification de conformité.</div>', unsafe_allow_html=True)

    with st.form("audit_terrain_form"):
        col1, col2 = st.columns(2)

        with col1:
            site = st.selectbox("Site", list(SITES.keys()))
            type_espace = st.selectbox("Type d’espace", TYPES_ESPACE)
            zone = st.text_input("Zone / secteur")
            reference_local = st.text_input("Référence locale (bâtiment, salle, repère...)")

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
            media_file = st.camera_input("Prendre une photo")
        elif media_mode == "Uploader une image":
            media_file = st.file_uploader("Uploader une image", type=["jpg", "jpeg", "png"])

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
            "statut": statut
        }

        append_audit(row)
        st.success("Audit enregistré avec succès ✅")
        st.rerun()

# =========================================================
# PAGE IMPORT FORMULAIRE
# =========================================================

elif page == "Import formulaire":
    st.markdown('<div class="main-title">📄 Import de formulaire d’audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Uploader un PDF, un Excel ou un CSV puis l’intégrer dans le pilotage.</div>', unsafe_allow_html=True)

    uploaded_doc = st.file_uploader(
        "Uploader un document",
        type=["pdf", "csv", "xlsx", "xls"]
    )

    if uploaded_doc is not None:
        file_name = uploaded_doc.name.lower()

        # ----------------------------
        # PDF
        # ----------------------------
        if file_name.endswith(".pdf"):
            pdf_saved_name = save_uploaded_file(uploaded_doc)

            uploaded_doc.seek(0)
            pdf_text = parse_pdf_text(uploaded_doc)

            st.markdown("### Texte extrait du PDF")
            st.text_area("Aperçu", pdf_text[:5000], height=250)

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
                    "statut": statut
                }

                append_audit(row)
                st.success("PDF importé avec succès ✅")
                st.rerun()

        # ----------------------------
        # CSV / EXCEL
        # ----------------------------
        elif file_name.endswith(".csv") or file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            try:
                if file_name.endswith(".csv"):
                    df_import = pd.read_csv(uploaded_doc)
                else:
                    df_import = pd.read_excel(uploaded_doc)

                st.markdown("### Aperçu du fichier")
                st.dataframe(df_import.head(20), use_container_width=True)

                if st.button("Importer ce fichier dans les audits"):
                    df_std = standardize_import_columns(df_import)
                    df_current = load_audits()
                    df_final = pd.concat([df_current, df_std], ignore_index=True)
                    save_audits(df_final)
                    st.success(f"{len(df_std)} ligne(s) importée(s) avec succès ✅")
                    st.rerun()

            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")

# =========================================================
# PAGE DASHBOARD
# =========================================================

elif page == "Dashboard":
    st.markdown('<div class="main-title">📊 Dashboard conformité</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Pilotage des audits, conformités et non-conformités.</div>', unsafe_allow_html=True)

    df = load_audits()

    if df.empty:
        st.info("Aucun audit enregistré pour le moment.")
    else:
        df["date_audit"] = pd.to_datetime(df["date_audit"], errors="coerce")

        # Filtres
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

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Audits", kpis["total_audits"])
        c2.metric("% conformité", f"{kpis['pourcentage_conformite']}%")
        c3.metric("Conformes", kpis["conformes"])
        c4.metric("Non conformes", kpis["non_conformes"])
        c5.metric("Critiques", kpis["critiques"])
        c6.metric("Ce mois", kpis["mois"])

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Audits par site")
            if not df_f.empty:
                fig_site = px.histogram(
                    df_f,
                    x="site",
                    color="conformite",
                    barmode="group",
                    title="Répartition des audits par site"
                )
                st.plotly_chart(fig_site, use_container_width=True)

        with col2:
            st.markdown("### Audits par type d’espace")
            if not df_f.empty:
                fig_type = px.histogram(
                    df_f,
                    x="type_espace",
                    color="conformite",
                    barmode="group",
                    title="Répartition des audits par type d’espace"
                )
                st.plotly_chart(fig_type, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### Gravité des écarts")
            df_nc = df_f[df_f["conformite"] == "Non conforme"].copy()
            if not df_nc.empty:
                fig_gravite = px.pie(
                    df_nc,
                    names="gravite",
                    title="Non-conformités par gravité"
                )
                st.plotly_chart(fig_gravite, use_container_width=True)
            else:
                st.info("Aucune non-conformité dans le filtre actuel.")

        with col4:
            st.markdown("### Catégories d’écarts")
            df_nc = df_f[df_f["conformite"] == "Non conforme"].copy()
            if not df_nc.empty:
                fig_cat = px.histogram(
                    df_nc,
                    x="categorie",
                    title="Non-conformités par catégorie"
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("Aucune non-conformité dans le filtre actuel.")

        st.markdown("### Evolution des audits dans le temps")
        if not df_f.empty:
            df_time = df_f.copy()
            df_time["jour"] = pd.to_datetime(df_time["date_audit"]).dt.date
            df_time = df_time.groupby("jour").size().reset_index(name="nb_audits")
            fig_time = px.line(df_time, x="jour", y="nb_audits", markers=True, title="Nombre d’audits par jour")
            st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("### Tableau des audits")
        st.dataframe(df_f.sort_values("date_audit", ascending=False), use_container_width=True)

# =========================================================
# PAGE CARTE
# =========================================================

elif page == "Carte des sites":
    st.markdown('<div class="main-title">🗺️ Carte des sites Renault</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Vue cartographique des implantations incluses dans le MVP.</div>', unsafe_allow_html=True)

    df_sites = pd.DataFrame([
        {"site": site, "lat": coords["lat"], "lon": coords["lon"]}
        for site, coords in SITES.items()
    ])

    st.map(df_sites.rename(columns={"lat": "latitude", "lon": "longitude"}))
    st.dataframe(df_sites, use_container_width=True)
``
