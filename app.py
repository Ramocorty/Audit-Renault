import streamlit as st
import requests
import pandas as pd

API_KEY = "TA_CLE_API_ICI"

# -----------------------------
# Upload PDF
# -----------------------------
def upload_pdf(file):
    url = "https://api.pdf.ai/v1/upload"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {
        "file": file
    }

    response = requests.post(url, headers=headers, files=files)

    # ✅ ne plus jamais planter ici
    try:
        return response.json()
    except:
        return {
            "error": True,
            "status_code": response.status_code,
            "text": response.text
        }


# -----------------------------
# Question IA
# -----------------------------
def ask_pdf(doc_id):
    url = "https://api.pdf.ai/v1/ask"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "doc_id": doc_id,
        "query": "Retourne un JSON avec nombre_ok, nombre_nok et score"
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        return response.json()
    except:
        return {
            "error": True,
            "status_code": response.status_code,
            "text": response.text
        }


# -----------------------------
# UI
# -----------------------------
st.title("🤖 Audit Renault IA")

file = st.file_uploader("Upload PDF", type=["pdf"])

if file:

    if st.button("Analyser"):

        st.info("Upload du PDF...")

        upload_result = upload_pdf(file)

        if upload_result.get("error"):
            st.error("❌ Erreur upload")
            st.write(upload_result)
        elif "doc_id" not in upload_result:
            st.error("❌ doc_id non reçu")
            st.write(upload_result)
        else:
            doc_id = upload_result["doc_id"]

            st.success("✅ PDF uploadé")

            st.info("Analyse IA...")

            result = ask_pdf(doc_id)

            if result.get("error"):
                st.error("❌ Erreur analyse")
                st.write(result)
            else:
                st.success("✅ Réponse IA")

                st.subheader("📦 Résultat brut")
                st.json(result)

                # ⚠️ ici réponse souvent texte
                answer = result.get("answer", "")

                df = pd.DataFrame({
                    "KPI": ["Résultat IA"],
                    "Valeur": [answer]
                })

                st.subheader("📊 KPI")
                st.dataframe(df)
