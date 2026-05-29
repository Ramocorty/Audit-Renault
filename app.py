import streamlit as st
import PyPDF2
import pandas as pd

# -----------------------------
# Fonction lecture PDF
# -----------------------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# -----------------------------
# Fonction analyse audit
# -----------------------------
def analyse_audit(text):
    text = text.lower()

    # KPI simples
    sections = [
        "plan de prévention",
        "balisages",
        "protection collective",
        "protection individuelles",
        "outillage",
        "produits chimiques",
        "environnement"
    ]

    results = []

    for section in sections:
        if section in text:
            score = text.count("oui") - text.count("non")
            results.append({
                "Section": section,
                "Score": score
            })

    # Score global
    total_oui = text.count("oui")
    total_non = text.count("non")

    kpi = {
        "Total OUI": total_oui,
        "Total NON": total_non,
        "Score global": total_oui - total_non
    }

    return pd.DataFrame(results), kpi


# -----------------------------
# UI Streamlit
# -----------------------------
st.title("📊 Audit Renault - Analyse PDF")

uploaded_file = st.file_uploader("Upload ton audit PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF chargé")

    text = extract_text_from_pdf(uploaded_file)

    st.subheader("📄 Aperçu texte")
    st.text(text[:1000])  # preview

    df, kpi = analyse_audit(text)

    st.subheader("📊 KPI Global")
    st.metric("Total OUI", kpi["Total OUI"])
    st.metric("Total NON", kpi["Total NON"])
    st.metric("Score Global", kpi["Score global"])

    st.subheader("📋 Résultat par section")
    st.dataframe(df)

    # Graph simple
    st.subheader("📈 Visualisation")
    st.bar_chart(df.set_index("Section"))
