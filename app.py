import streamlit as st
import requests
import pandas as pd

API_URL = "https://api.apify.com/v2/acts/parseforge~pdf-to-json-parser/run-sync-get-dataset-items"

API_TOKEN = "TA_CLE_APIFY"

def analyse_pdf(file):
    files = {
        "file": file
    }

    params = {
        "token": API_TOKEN
    }

    response = requests.post(API_URL, params=params, files=files)

    if response.status_code != 200:
        return {"error": response.text}

    return response.json()


st.title("🤖 Audit Renault IA (Stable)")

file = st.file_uploader("Upload PDF", type=["pdf"])

if file:
    if st.button("Analyser"):

        result = analyse_pdf(file)

        if "error" in result:
            st.error(result)
        else:
            st.subheader("📦 Donnée brute")
            st.write(result)

            df = pd.DataFrame(result)

            st.subheader("📊 Données structurées")
            st.dataframe(df)
