import streamlit as st
import requests
import pandas as pd

API_KEY = "TA_CLE_API_ICI"

def analyse_pdf_with_ai(file):
    url = "https://api.pdf.ai/v1/extract"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {
        "file": file
    }

    data = {
        "prompt": "Retourne un JSON avec nombre_ok, nombre_nok, score"
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    try:
        return response.json()
    except:
        return {
            "error": "Réponse non JSON",
            "status_code": response.status_code,
            "text": response.text
        }

st.title("Audit Renault IA")

file = st.file_uploader("Upload PDF", type=["pdf"])

if file:
    if st.button("Analyser"):
        result = analyse_pdf_with_ai(file)

        if "error" in result:
            st.error(result)
        else:
            st.json(result)

            data = result.get("data", result)

            df = pd.DataFrame({
                "KPI": ["OK", "NOK", "Score"],
                "Valeur": [
                    data.get("nombre_ok", 0),
                    data.get("nombre_nok", 0),
                    data.get("score", 0)
                ]
            })

            st.dataframe(df)
            st.bar_chart(df.set_index("KPI"))
