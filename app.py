import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "TA_CLE_API_ICI"  # 🔑 mets ta clé PDF.ai

# -----------------------------
# Fonction appel API IA
# -----------------------------
def analyse_pdf_with_ai(file):
    url = "https://api.pdf.ai/v1/extract"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {
        "file": file
    }

    prompt = """
    Tu es un expert HSE Renault.
    Analyse ce document d'audit et retourne un JSON avec :
    - nombre_ok
    - nombre_nok
    - sections (liste)
    - score (entre 0 et 100)
    """

    data = {
        "prompt": prompt
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    return response.json()

# -----------------------------
# UI STREAMLIT
# -----------------------------
st.title("🤖 Audit Renault IA - PDF → KPI")

file = st.file_uploader("Upload ton PDF", type=["pdf"])

if file:
    st.success("✅ PDF chargé")

    if st.button("🚀 Lancer analyse IA"):
        with st.spinner("Analyse en cours..."):
            result = analyse_pdf_with_ai(file)

        st.subheader("📊 Résultat IA brut")
        st.json(result)

        # -----------------------------
        # Essai extraction KPI
        # -----------------------------
        try:
            data = result.get("data", {})

            df = pd.DataFrame({
                "KPI": ["OK", "NOK", "Score"],
                "Valeur": [
                    data.get("nombre_ok", 0),
                    data.get("nombre_nok", 0),
                    data.get("score", 0)
                ]
            })

            st.subheader("📈 KPI")
            st.dataframe(df)

            st.bar_chart(df.set_index("KPI"))

        except:
            st.warning("⚠️ Impossible de parser proprement la réponse IA")
