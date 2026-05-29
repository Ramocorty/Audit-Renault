import os
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(layout="wide")

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Sites Renault
SITES = ["Aubevoye", "Lardy", "Guyancourt", "VSF", "Boulogne"]

OBJETS = [
    "Humain", "Table", "Chaise", "PC",
    "Parking", "Barrière", "Lampe",
    "Chantier", "Véhicule", "Autre"
]

# =========================================================
# STYLE (dark Renault-like)
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#1e1e2f,#2c2f48);
    color: white;
}
h1,h2,h3 {color:white}
.card {
    background:#2c2f48;
    padding:15px;
    border-radius:15px;
    box-shadow:0 8px 20px rgba(0,0,0,0.2);
}
button {
    border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# FONCTIONS
# =========================================================

def init_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "date","site","type","conformite",
            "gravite","objets","commentaire"
        ])
        df.to_csv(DATA_FILE, index=False)

def save_data(row):
    df = pd.read_csv(DATA_FILE)
    df.loc[len(df)] = row
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

init_data()

# =========================================================
# NAVIGATION SIMPLE
# =========================================================
col1,col2,col3,col4 = st.columns(4)

if col1.button("🏠 Accueil"):
    st.session_state.page="home"
if col2.button("📷 Audit"):
    st.session_state.page="audit"
if col3.button("📊 KPI"):
    st.session_state.page="kpi"
if col4.button("🗺️ Carte"):
    st.session_state.page="map"

if "page" not in st.session_state:
    st.session_state.page="home"

# =========================================================
# ACCUEIL
# =========================================================
if st.session_state.page=="home":
    st.title("🚀 Audit Renault MVP")

    st.markdown("### Actions rapides")

    c1,c2 = st.columns(2)
    with c1:
        if st.button("📷 Faire un audit"):
            st.session_state.page="audit"
    with c2:
        if st.button("📊 Voir KPI"):
            st.session_state.page="kpi"

# =========================================================
# AUDIT
# =========================================================
elif st.session_state.page=="audit":

    st.title("📷 Audit terrain")

    site = st.selectbox("Site", SITES)
    type_espace = st.selectbox("Type", ["Parking","Salle","Chantier","Site"])

    conformite = st.radio("Conformité",["Conforme","Non conforme"])
    gravite = st.selectbox("Gravité",["Mineure","Majeure","Critique"])

    objets = st.multiselect("Objets observés", OBJETS)

    # Photo
    photo = st.camera_input("Prendre photo")
    upload = st.file_uploader("Ou importer image")

    commentaire = st.text_area("Commentaire")

    if st.button("✅ Enregistrer"):
        row = [
            datetime.now(),
            site,
            type_espace,
            conformite,
            gravite,
            ",".join(objets),
            commentaire
        ]
        save_data(row)
        st.success("Audit enregistré ✅")

# =========================================================
# KPI
# =========================================================
elif st.session_state.page=="kpi":

    st.title("📊 KPI")

    df = load_data()

    if len(df)==0:
        st.warning("Pas encore de données")
    else:

        total = len(df)
        conformes = len(df[df["conformite"]=="Conforme"])
        nonconf = len(df[df["conformite"]=="Non conforme"])

        pct = round((conformes/total)*100,1)

        c1,c2,c3 = st.columns(3)

        c1.metric("Audits", total)
        c2.metric("% conformité", f"{pct}%")
        c3.metric("Non conformes", nonconf)

        st.markdown("### Par site")
        fig = px.histogram(df, x="site", color="conformite")
        st.plotly_chart(fig)

        st.markdown("### Par type")
        fig = px.histogram(df, x="type")
        st.plotly_chart(fig)

# =========================================================
# CARTE
# =========================================================
elif st.session_state.page=="map":

    st.title("🗺️ Sites Renault")

    df_sites = pd.DataFrame([
        {"lat":49.17,"lon":1.33},
        {"lat":48.52,"lon":2.26},
        {"lat":48.76,"lon":2.08}
    ])

    st.map(df_sites)
