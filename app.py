import streamlit as st
onner le code `app.py` en étant encore plus explicite sur ce qui est le code et ce qui ne l'est pas.

---

**Voici le contenu exact que vous devriez copier-coller dans votre fichier `app.py` :**

```python
import streamlit as st
onner le code `app.py` en étant encore plus explicite sur ce qui est le code et ce qui ne l'est pas.

---

**Voici le contenu exact que vous devriez copier-coller dans votre fichier `app.py` :**

```python
import streamlit as st
onner le code `app.py` en étant encore plus explicite sur ce qui est le code et ce qui ne l'est pas.

---

**Voici le contenu exact que vous devriez copier-coller dans votre fichier `app.py` :**

```python
import streamlit as st
onner le code `app.py` en étant encore plus explicite sur ce qui est le code et ce qui ne l'est pas.

---

**Voici le contenu exact que vous devriez copier-coller dans votre fichier `app.py` :**

```python
import streamlit as st
import pandas as pd # On peut l'utiliser si le formulaire est un CSV/Excel

st.set_page_config(page_title="Audit Chantier Renault", layout="centered")

st.title("Application d'Audit sur Site Renault")
st.subheader("Uploader un formulaire d'audit")import pandas as pd # On peut l'utiliser si le formulaire est un CSV/Excel

st.set_page_config(page_title="Audit Chantier Renault", layout="centered")

st.title("Application d'Audit sur Site Renault")
st.subheader("Uploader un formulaire d'audit")import pandas as pd # On peut l'utiliser si le formulaire est un CSV/Excel

st.set_page_config(page_title="Audit Chantier Renault", layout="centered")

st.title("Application d'Audit sur Site Renault")
st.subheader("Uploader un formulaire d'audit")import pandas as pd # On peut l'utiliser si le formulaire est un CSV/Excel

st.set_page_config(page_title="Audit Chantier Renault", layout="centered")

st.title("Application d'Audit sur Site Renault")
st.subheader("Uploader un formulaire d'audit")

st.write("""
Bienvenue dans l'outil d'audit des chantiers Renault.
Veuillez uploader votre formulaire d'audit (par exemple, un PDF, une image ou un fichier Excel).
""")

uploaded_file = st.file_uploader("Choisissez un fichier de formulaire", type

st.write("""
Bienvenue dans l'outil d'audit des chantiers Renault.
Veuillez uploader votre formulaire d'audit (par exemple, un PDF, une image ou un fichier Excel).
""")

uploaded_file = st.file_uploader("Choisissez un fichier de formulaire", type

st.write("""
Bienvenue dans l'outil d'audit des chantiers Renault.
Veuillez uploader votre formulaire d'audit (par exemple, un PDF, une image ou un fichier Excel).
""")

uploaded_file = st.file_uploader("Choisissez un fichier de formulaire", type

st.write("""
Bienvenue dans l'outil d'audit des chantiers Renault.
Veuillez uploader votre formulaire d'audit (par exemple, un PDF, une image ou un fichier Excel).
""")

uploaded_file = st.file_uploader("Choisissez un fichier de formulaire", type

st.write("""
Bienvenue dans l'outil d'audit des chantiers Renault.
Veuillez uploader votre formulaire d'audit (par exemple, un PDF, une image ou un fichier Excel).
""")

uploaded_file = st.file_uploader("Choisissez un fichier de formulaire", type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])

if uploaded_file is not None:
    st.success(f"Fichier '{uploaded_file.name}' a été téléchargé avec succès !")

    # Optionnel : Afficher des informations sur le fichier ou son=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])

if uploaded_file is not None:
    st.success(f"Fichier '{uploaded_file.name}' a été téléchargé avec succès !")

    # Optionnel : Afficher des informations sur le fichier ou son=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])

if uploaded_file is not None:
    st.success(f"Fichier '{uploaded_file.name}' a été téléchargé avec succès !")

    # Optionnel : Afficher des informations sur le fichier ou son=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"])

if uploaded_file is not None:
    st.success(f"Fichier '{uploaded_file.name}' a été téléchargé avec succès !")

    # Optionnel : Afficher des informations sur le fichier ou son contenu
    # Si c'est une image
    if uploaded_file.type.startswith('image'):
        st.image(uploaded_file, caption="Formulaire téléchargé", use_column_width=True)
    # Si c'est un PDF (Streamlit ne l'affiche pas directement contenu
    # Si c'est une image
    if uploaded_file.type.startswith('image'):
        st.image(uploaded_file, caption="Formulaire téléchargé", use_column_width=True)
    # Si c'est un PDF (Streamlit ne l'affiche pas directement contenu
    # Si c'est une image
    if uploaded_file.type.startswith('image'):
        st.image(uploaded_file, caption="Formulaire téléchargé", use_column_width=True)
    # Si c'est un PDF (Streamlit ne l'affiche pas directement contenu
    # Si c'est une image
    if uploaded_file.type.startswith('image'):
        st.image(uploaded_file, caption="Formulaire téléchargé", use_column_width=True)
    # Si c'est un PDF (Streamlit ne l'affiche pas directement contenu
    # Si c'est une image
    if uploaded_file.type.startswith('image'):
        st.image(uploaded_file, caption="Formulaire téléchargé", use_column_width=True)
    # Si c'est un PDF (Streamlit ne l'affiche pas directement, mais on peut le mentionner)
    elif uploaded_file.type == 'application/pdf':
        st.write("Le fichier PDF a été téléchargé. Vous pouvez maintenant le traiter.")
    # Si c'est un CSV ou Excel (exemple de lecture)
    elif uploaded_file.type, mais on peut le mentionner)
    elif uploaded_file.type == 'application/pdf':
        st.write("Le fichier PDF a été téléchargé. Vous pouvez maintenant le traiter.")
    # Si c'est un CSV ou Excel (exemple de lecture)
    elif uploaded_file.type, mais on peut le mentionner)
    elif uploaded_file.type == 'application/pdf':
        st.write("Le fichier PDF a été téléchargé. Vous pouvez maintenant le traiter.")
    # Si c'est un CSV ou Excel (exemple de lecture)
    elif uploaded_file.type, mais on peut le mentionner)
    elif uploaded_file.type == 'application/pdf':
        st.write("Le fichier PDF a été téléchargé. Vous pouvez maintenant le traiter.")
    # Si c'est un CSV ou Excel (exemple de lecture)
    elif uploaded_file.type, mais on peut le mentionner)
    elif uploaded_file.type == 'application/pdf':
        st.write("Le fichier PDF a été téléchargé. Vous pouvez maintenant le traiter.")
    # Si c'est un CSV ou Excel (exemple de lecture)
    elif uploaded_file.type == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors == 'text/csv':
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier CSV :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Aperçu du fichier de la lecture du fichier CSV : {e}")
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Aperçu du fichier de la lecture du fichier CSV : {e}")
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Aperçu du fichier de la lecture du fichier CSV : {e}")
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Aperçu du fichier de la lecture du fichier CSV : {e}")
    elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Aperçu du fichier Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé Excel :")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
    else:
        st.write(f"Fichier de type '{uploaded_file.type}' téléchargé.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info.")

    # Ici, vous pourriez ajouter la logique pour traiter le formulaire
    # Par exemple, l'envoyer à un service d'OCR si c'est une image,
    # ou l'analyser si c'est un fichier structuré.

st.markdown("---")
st.info("Cette application est un prototype. Des fonctionnalités supplémentaires seront ajoutées.")
