import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(layout="wide")

DATA_FILE = "audits.csv"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================================================
# STYLE DARK + MOBILE
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#1c1e26,#2d3142);
    color:white;
}

h1,h2,h3,h4,h5,p,span {
    color:white!important;
}

.card {
    background: rgba(255,255,255,0.08);
    border-radius:20px;
    padding:15px;
    margin-bottom:10px;
}

button {
    border-radius:12px!important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO RENAULT
# =========================================================
st.image("nouveau_logo_renault.webp", width=90)

# =========================================================
# NAVIGATION SIMPLE (MOBILE)
# =========================================================
page = st.radio(
    "",
    ["🏠 Accueil","📷 Audit","📄 Import","📊 KPI","🗺️ Carte"],
    horizontal=True
)

# =========================================================
# SITES
# =========================================================
SITES = ["Aubevoye","Lardy","Guyancourt","VSF","Boulogne"]

# =========================================================
# DATA
# =========================================================
if not os.path.exists(DATA_FILE):
    pd.DataFrame().to_csv(DATA_FILE)

df = pd.read_csv(DATA_FILE)

# =========================================================
# FONCTIONS
# =========================================================

def save_media(file):
    if file is None:
        return ""
    name = str(uuid.uuid4()) + "_" + file.name
    path = os.path.join(UPLOAD_DIR, name)
    with open(path,"wb") as f:
        f.write(file.getbuffer())
    return name

def add_audit(data):
    global df
    new_df = pd.DataFrame([data])
    df = pd.concat([df,new_df],ignore_index=True)
    df.to_csv(DATA_FILE,index=False)

def compute_kpi(df):
    if df.empty:
        return 0,0,0,0
    total = len(df)
    conformes = (df["conformite"]=="Conforme").sum()
    non_conformes = (df["conformite"]=="Non conforme").sum()
    pct = int((conformes/total)*100) if total>0 else 0
    return total, conformes, non_conformes, pct

# =========================================================
# ACCUEIL
# =========================================================
if page=="🏠 Accueil":

    st.title("Audit Renault Mobile")

    total, conformes, non_conformes, pct = compute_kpi(df)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Audits",total)
    c2.metric("% Conformité",str(pct)+"%")
    c3.metric("Conformes",conformes)
    c4.metric("Non conformes",non_conformes)

    st.write("Application audit terrain + KPI")

# =========================================================
# AUDIT PHOTO
# =========================================================
elif page=="📷 Audit":

    st.subheader("Audit terrain")

    site = st.selectbox("Site",SITES)
    type_espace = st.selectbox("Type espace",["chantier","parking","salle","bureau","zone"])

    col1,col2 = st.columns(2)

    with col1:
        conformite = st.radio("Conformité",["Conforme","Non conforme"])
        gravite = st.selectbox("Gravité",["Faible","Moyenne","Critique"])

    with col2:
        categorie = st.selectbox("Catégorie",["Sécurité","Propreté","Technique"])
        auditeur = st.text_input("Auditeur")

    # PHOTO
    photo = st.camera_input("Prendre une photo")
    upload = st.file_uploader("ou uploader une image",type=["jpg","png"])

    # SIMULATION DETECTION
    objets = st.multiselect("Objets détectés",
        ["Humain","Table","Chaise","PC","Parking","Barrière","Lampe","Chantier","Véhicule"])

    commentaire = st.text_area("Commentaire")

    if st.button("Enregistrer"):

        media = save_media(photo if photo else upload)

        add_audit({
            "date":datetime.now(),
            "site":site,
            "type_espace":type_espace,
            "conformite":conformite,
            "gravite":gravite,
            "categorie":categorie,
            "auditeur":auditeur,
            "objets":",".join(objets),
            "media":media,
            "commentaire":commentaire
        })

        st.success("Audit enregistré")

# =========================================================
# IMPORT PDF / EXCEL
# =========================================================
elif page=="📄 Import":

    st.subheader("Import formulaire")

    file = st.file_uploader("Importer PDF / Excel / CSV")

    if file:

        st.write("Aperçu fichier")

        if file.name.endswith(".csv"):
            df_import = pd.read_csv(file)
        else:
            df_import = pd.read_excel(file)

        st.dataframe(df_import)

        if st.button("Importer"):

            df_final = pd.concat([df,df_import],ignore_index=True)
            df_final.to_csv(DATA_FILE,index=False)

            st.success("Import réussi")

# =========================================================
# KPI
# =========================================================
elif page=="📊 KPI":

    st.subheader("Dashboard")

    if df.empty:
        st.warning("Pas de données")
    else:

        total, conformes, non_conformes, pct = compute_kpi(df)

        st.metric("% conformité",pct)

        fig = px.histogram(df, x="site", color="conformite")
        st.plotly_chart(fig,use_container_width=True)

        st.dataframe(df)

# =========================================================
# MAP
# =========================================================
elif page=="🗺️ Carte":

    st.subheader("Carte sites")

    map_data = pd.DataFrame({
        "lat":[49.17,48.52,48.76,48.82,48.83],
        "lon":[1.33,2.26,2.08,1.90,2.24]
    })

    st.map(map_data)
