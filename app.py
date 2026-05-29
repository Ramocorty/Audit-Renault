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
# Parsing intelligent (corrigé)
# -----------------------------
def parse_audit(text):
    lines = text.split("\n")

    data = []
    current_section = "Non défini"

    for i in range(len(lines)):
        line = lines[i].strip().lower()

        # Détection sections
        if "plan de prévention" in line:
            current_section = "Plan de prévention"
        elif "balisage" in line:
            current_section = "Balisage"
        elif "protection collective" in line:
            current_section = "Protection collective"
        elif "protection individuelle" in line:
            current_section = "Protection individuelle"
        elif "outillage" in line:
            current_section = "Outillage"
        elif "produits chimiques" in line:
            current_section = "Produits chimiques"
        elif "environnement" in line:
            current_section = "Environnement"

        # Logique principale : question + ligne suivante = statut
        if i < len(lines) - 1:
            next_line = lines[i + 1].strip().lower()

            # On considère une "question"
            if len(line) > 20:

                if "x" in next_line or "k" in next_line:
                    statut = "OK"
                elif "non" in next_line:
                    statut = "NOK"
                else:
                    continue

                data.append({
                    "Section": current_section,
                    "Question": line,
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
st.title("📊 Audit Renault - Analyse locale (offline)")

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

        # Export CSV
        st.subheader("⬇️ Export")
        st.download_button(
            label="Télécharger le résultat (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="audit_kpi.csv",
            mime="text/csv"
        )
