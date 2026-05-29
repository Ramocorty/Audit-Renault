import streamlit as st
import pdfplumber
import pandas as pd

# -----------------------------
# Lecture PDF
# -----------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text


# -----------------------------
# Transformation PDF -> Table
# -----------------------------
def transform_to_table(text):
    lines = text.split("\n")

    data = []
    current_section = "Non défini"

    for line in lines:
        clean_line = line.strip().lower()

        # Détection sections (adapté audit Renault)
        if "plan de prévention" in clean_line:
            current_section = "Plan de prévention"
        elif "balisages" in clean_line:
            current_section = "Balisage"
        elif "protection collective" in clean_line:
            current_section = "Protection collective"
        elif "protection individuelles" in clean_line:
            current_section = "Protection individuelle"
        elif "outillage" in clean_line:
            current_section = "Outillage"
        elif "produits chimiques" in clean_line:
            current_section = "Produits chimiques"
        elif "environnement" in clean_line:
            current_section = "Environnement"

        # Détection lignes audit
        if len(clean_line) > 15:
            if "oui" in clean_line or "non" in clean_line or "x" in clean_line:
                
                if "oui" in clean_line or "x" in clean_line:
                    statut = "OK"
                elif "non" in clean_line:
                    statut = "NOK"
                else:
                    statut = "NC"

                data.append({
                    "Section": current_section,
                    "Question": clean_line,
                    "Statut": statut
                })

    return pd.DataFrame(data)


# -----------------------------
# KPI
# -----------------------------
def compute_kpi(df):
    total_ok = (df["Statut"] == "OK").sum()
    total_nok = (df["Statut"] == "NOK").sum()

    total = total_ok + total_nok
    score = (total_ok / total * 100) if total > 0 else 0

    return total_ok, total_nok, score


# -----------------------------
# UI STREAMLIT
# -----------------------------
st.title("📊 Audit Renault - PDF → KPI")

file = st.file_uploader("Upload ton audit PDF", type=["pdf"])

if file:
    st.success("✅ PDF chargé")

    # Extraction texte
    text = extract_text_from_pdf(file)

    st.subheader("📄 Aperçu")
    st.text(text[:1000])

    # Transformation
    df = transform_to_table(text)

    st.subheader("📋 Table d'audit")

    if df.empty:
        st.warning("⚠️ Aucun élément détecté (ajuster le parsing)")
    else:
        st.dataframe(df)

        # KPI
        ok, nok, score = compute_kpi(df)

        st.subheader("📊 KPI")

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ OK", ok)
        col2.metric("❌ NOK", nok)
        col3.metric("🎯 Score qualité", f"{round(score,1)} %")

        # Graph
        st.subheader("📈 Répartition")
        st.bar_chart(df["Statut"].value_counts())


# -----------------------------
# REQUIREMENTS (à créer à part)
# -----------------------------
# streamlit
# pdfplumber
# pandas
