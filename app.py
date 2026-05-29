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
    
    return response.json()


# -----------------------------
# Question au PDF
# -----------------------------
def ask_pdf(doc_id):
    url = "https://api.pdf.ai/v1/ask"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "doc_id": doc_id,
        "query": "Donne moi le nombre de OK, NOK et le score qualité en JSON"
    }

    response = requests.post(url, headers=headers, json=json_data)

    try:
        return response.json()
    except:
        return {"error": response.text}


# -----------------------------
# UI
# -----------------------------
st.title("🤖 Audit Renault IA")

file = st.file_uploader("Upload PDF", type=["pdf"])

if file:
    st.success("PDF chargé")

    if st.button("Analyser"):
        
        # Step 1: Upload
        upload_result = upload_pdf(file)

        if "doc_id" not in upload_result:
            st.error("❌ Upload échoué")
            st.write(upload_result)
        else:
            doc_id = upload_result["doc_id"]

            st.info("PDF uploadé ✅")

            # Step 2: Ask
            result = ask_pdf(doc_id)

            st.subheader("📦 Réponse IA")
            st.json(result)

            # Essai extraction KPI
            try:
                answer = result.get("answer", "")

                # petit parsing simple
                df = pd.DataFrame({
                    "KPI": ["Résultat brut"],
                    "Valeur": [answer]
                })

                st.subheader("📊 KPI")
                st.dataframe(df)

            except:
                st.warning("⚠️ Impossible de parser")
