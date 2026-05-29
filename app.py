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
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# -----------------------------
# Transformation en table
# -----------------------------
def transform_to_table(text):
    lines = text.split("\n")

    data = []

    for line in lines:
        line = line.strip().lower()

        if "oui" in line or "non" in line:
            statut = "OUI" if "oui" in line else "NON"

            data.append({
                "Question": line,
                "Statut": statut
            })

    df = pd.DataFrame(data)
    return df

# -----------------------------
# KPI
# -----------------------------
def compute_kpi(df):
    total_oui = (df["Statut"] == "OUI").sum()
    total_non = (df["Statut"] == "NON").sum()

    score = total_oui / (total_oui + total_non) if (total_oui + total_non) > 0 else 0

    return total_oui, total_non, score

# -----------------------------
# UI
# -----------------------------
st.title("📊 Audit Renault - PDF → KPI")

file = st.file_uploader("Upload PDF", type=["pdf"])

if file:
    text = extract_text_from_pdf(file)

    df = transform_to_table(text)

    st.subheader("📋 Table d'audit")
    st.dataframe(df)

    if not df.empty:
        oui, non, score = compute_kpi(df)

        st.subheader("📊 KPI")
        st.metric("✅ OUI", oui)
        st.metric("❌ NON", non)
        st.metric("🎯 Score qualité", f"{round(score*100,1)} %")

        st.bar_chart(df["Statut"].value_counts())
