import streamlit as st
import pdfplumber
import pandas as pd

# -----------------------------
# Lecture PDF
# -----------------------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text


# -----------------------------
# Transformation en table
# -----------------------------
def parse_audit(text):
    lines = text.split("\n")

    data = []
    current_section = "Non défini"

    for line in lines:
        l = line.strip().lower()

        # Détection sections
        if "plan de prévention" in l:
            current_section = "Plan de prévention"
        elif "balisage" in l:
            current_section = "Balisage"
        elif "protection collective" in l:
            current_section = "Protection collective"
        elif "protection individuelles" in l:
            current_section = "Protection individuelle"
        elif "outillage" in l:
            current_section = "Outillage"
        elif "produits chimiques" in l:
            current_section = "Produits chimiques"
        elif "environnement" in l:
            current_section = "Environnement"

        # Détection statut
        if "oui" in l or "non" in l or "x" in l:
            if "non" in l:
                statut = "NOK"
            elif "oui" in l or "x" in l:
                statut = "OK"
            else:
                statut = "NC"

            data.append({
                "Section": current_section,
                "Ligne": l,
                "Statut": statut
            })

    return pd.DataFrame(data)


# -----------------------------
# KPI
# -----------------------------
def compute_kpi(df):
    ok = (df["Statut"] == "OK").sum()
    nok = (df["Statut"] == "NOK").sum()
    total = ok + nok

    score = (ok / total * 100) if total > 0 else 0

    return ok, nok, score


# -----------------------------
# UI
# -----------------------------
st.title("📊 Audit Renault - Analyse locale (sans IA externe)")

file = st.file_uploader("Upload ton PDF", type=["pdf"])

if file:
    st.success("✅ PDF chargé")

    text = extract_text(file)

    st.subheader("📄 Aperçu texte")
    st.text(text[:1000])

    df = parse_audit(text)

    st.subheader("📋 Table d'audit")

    if df.empty:
        st.warning("⚠️ Aucune donnée détectée")
    else:
        st.dataframe(df)

        ok, nok, score = compute_kpi(df)

        st.subheader("📊 KPI")

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ OK", ok)
        col2.metric("❌ NOK", nok)
        col3.metric("🎯 Score qualité", f"{round(score,1)} %")

        st.subheader("📈 Répartition")
        st.bar_chart(df["Statut"].value_counts())

        # Export Excel
        st.subheader("⬇️ Export")
        st.download_button(
            label="Télécharger Excel",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="audit_result.csv",
            mime="text/csv"
        )
