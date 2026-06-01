import streamlit as st
import pdfplumber
import pandas as pd
import sqlite3
from PIL import Image
import pytesseract
from datetime import datetime
import plotly.express as px
import os

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Audit Sécurité Renault",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOGO
# =====================================================

logo_path = "nouveau_logo_renault.png"

if os.path.exists(logo_path):
    st.image(logo_path, width=250)

st.title("📊 Audit Sécurité Renault")
st.markdown("Analyse automatique des audits PDF et photos")

# =====================================================
# BASE SQLITE
# =====================================================

conn = sqlite3.connect("audits.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_audit TEXT,
    site TEXT,
    societe TEXT,
    section TEXT,
    question TEXT,
    statut TEXT
)
""")

conn.commit()

# =====================================================
# EXTRACTION PDF
# =====================================================

def extract_text_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# =====================================================
# EXTRACTION PHOTO (OCR)
# =====================================================

def extract_text_image(image):

    text = pytesseract.image_to_string(
        Image.open(image),
        lang="fra"
    )

    return text

# =====================================================
# PARSING AUDIT
# =====================================================

def parse_audit(text):

    lines = text.split("\n")

    data = []
    current_section = "Non défini"

    sections = {
        "plan de prévention": "Plan de prévention",
        "balisage": "Balisage",
        "protection collective": "Protection collective",
        "protection individuelle": "Protection individuelle",
        "outillage": "Outillage",
        "produits chimiques": "Produits chimiques",
        "environnement": "Environnement"
    }

    for i in range(len(lines)-1):

        line = lines[i].strip()
        next_line = lines[i+1].strip().lower()

        for key, value in sections.items():
            if key in line.lower():
                current_section = value

        if len(line) > 20:

            statut = None

            if "x" in next_line or "ok" in next_line:
                statut = "OK"

            elif "non" in next_line or "nok" in next_line:
                statut = "NOK"

            if statut:

                data.append({
                    "Section": current_section,
                    "Question": line,
                    "Statut": statut
                })

    return pd.DataFrame(data)

# =====================================================
# ENREGISTREMENT SQL
# =====================================================

def save_audit(df, site, societe):

    today = datetime.today().strftime("%Y-%m-%d")

    for _, row in df.iterrows():

        cursor.execute("""
        INSERT INTO audits
        (
            date_audit,
            site,
            societe,
            section,
            question,
            statut
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            today,
            site,
            societe,
            row["Section"],
            row["Question"],
            row["Statut"]
        ))

    conn.commit()

# =====================================================
# KPI
# =====================================================

def compute_kpis():

    df = pd.read_sql_query(
        "SELECT * FROM audits",
        conn
    )

    if df.empty:
        return None

    ok = (df["statut"] == "OK").sum()
    nok = (df["statut"] == "NOK").sum()

    total = ok + nok

    score = round(ok / total * 100, 1) if total > 0 else 0

    return df, ok, nok, score

# =====================================================
# SAISIE
# =====================================================

st.sidebar.header("Informations Audit")

site = st.sidebar.text_input(
    "Site Renault",
    value="Flins"
)

societe = st.sidebar.text_input(
    "Société intervenante",
    value="SPIE"
)

# =====================================================
# UPLOAD PDF
# =====================================================

st.header("📄 Analyse PDF")

pdf_file = st.file_uploader(
    "Importer un audit PDF",
    type=["pdf"]
)

if pdf_file:

    text = extract_text_pdf(pdf_file)

    st.subheader("Texte extrait")

    st.text(text[:2000])

    df_audit = parse_audit(text)

    if not df_audit.empty:

        st.success(
            f"{len(df_audit)} contrôles détectés"
        )

        st.dataframe(df_audit)

        if st.button("Enregistrer l'audit PDF"):

            save_audit(
                df_audit,
                site,
                societe
            )

            st.success("Audit enregistré")

# =====================================================
# PHOTO
# =====================================================

st.header("📷 Photo Audit Papier")

photo = st.camera_input(
    "Prendre une photo"
)

if photo:

    st.image(photo)

    text = extract_text_image(photo)

    st.subheader("Texte OCR")

    st.text(text[:2000])

    df_photo = parse_audit(text)

    if not df_photo.empty:

        st.dataframe(df_photo)

        if st.button("Enregistrer l'audit Photo"):

            save_audit(
                df_photo,
                site,
                societe
            )

            st.success("Audit enregistré")

# =====================================================
# DASHBOARD KPI
# =====================================================

st.header("📊 Dashboard KPI")

result = compute_kpis()

if result:

    df, ok, nok, score = result

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "✅ Conformes",
        ok
    )

    col2.metric(
        "❌ Non conformes",
        nok
    )

    col3.metric(
        "🎯 Taux conformité",
        f"{score}%"
    )

    st.subheader("Audits par site")

    site_df = (
        df.groupby("site")
        .size()
        .reset_index(name="Nombre audits")
    )

    fig_site = px.bar(
        site_df,
        x="site",
        y="Nombre audits",
        title="Nombre d'audits par site"
    )

    st.plotly_chart(
        fig_site,
        use_container_width=True
    )

    st.subheader("Audits par société")

    soc_df = (
        df.groupby("societe")
        .size()
        .reset_index(name="Nombre audits")
    )

    fig_soc = px.bar(
        soc_df,
        x="societe",
        y="Nombre audits",
        title="Nombre d'audits par société"
    )

    st.plotly_chart(
        fig_soc,
        use_container_width=True
    )

    st.subheader("Conformité par société")

    conf_soc = (
        df.groupby(["societe", "statut"])
        .size()
        .reset_index(name="Nombre")
    )

    fig_conf = px.bar(
        conf_soc,
        x="societe",
        y="Nombre",
        color="statut",
        barmode="group",
        title="OK / NOK par société"
    )

    st.plotly_chart(
        fig_conf,
        use_container_width=True
    )

    st.subheader("Audits par semaine")

    df["date_audit"] = pd.to_datetime(
        df["date_audit"]
    )

    df["semaine"] = (
        df["date_audit"]
        .dt.isocalendar()
        .week
    )

    week_df = (
        df.groupby("semaine")
        .size()
        .reset_index(name="Nombre audits")
    )

    fig_week = px.line(
        week_df,
        x="semaine",
        y="Nombre audits",
        markers=True,
        title="Audits par semaine"
    )

    st.plotly_chart(
        fig_week,
        use_container_width=True
    )

    st.subheader("Données détaillées")

    st.dataframe(df)

else:

    st.info(
        "Aucun audit enregistré pour le moment."
    )
