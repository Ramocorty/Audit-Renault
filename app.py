import streamlit as st

st.set_page_config(page_title="Audit Renault MVP", layout="centered")

st.title("📱 Audit Bâtiment")

st.write("Application MVP pour signaler un incident")

batiment = st.text_input("Bâtiment")
salle = st.text_input("Salle")
description = st.text_area("Description du problème")

if st.button("Envoyer"):
    st.success("Incident enregistré ✅")
