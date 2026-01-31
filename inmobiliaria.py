import streamlit as st
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXIÓN A GOOGLE DRIVE ---
scope = ['https://www.googleapis.com/auth/drive']
creds_dict = st.secrets["gcp_service_account"] 
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" 

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")
st.title("🏠 Cortes Inmobiliaria - Panel de Carga")

# --- 2. FORMULARIO DE CARGA COMPLETO ---
with st.form("registro_drive", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Nombre de la Propiedad")
        precio = st.number_input("Precio (USD)", min_value=0, step=500)
    with col2:
        tipo = st.selectbox("Tipo", ["Casa", "Departamento", "Lote", "Local", "Campo"])
        descripcion = st.text_area("Descripción/Notas")

    video = st.file_uploader("Seleccioná el Video", type=["mp4", "mov"])
    fotos = st.file_uploader("Seleccioná las Fotos", type=["jpg", "png", "jpeg", "heic"], accept_multiple_files=True)
    
    boton = st.form_submit_button("🚀 SUBIR PROPIEDAD A DRIVE")
    
    if boton:
        if titulo and (video or fotos):
            with st.spinner("Guardando archivos y datos en Drive..."):
                # Crear carpeta de la propiedad
                folder_name = f"{titulo} - USD {precio}"
                carpeta_prop = drive.CreateFile({
                    'title': folder_name,
                    'parents': [{'id': ID_CARPETA_RAIZ}],
                    'mimeType': 'application/vnd.google-apps.folder'
                })
                carpeta_prop.Upload()
                
                # Subir Video
                if video:
                    f_v = drive.CreateFile({'title': f"video_{titulo}.mov", 'parents': [{'id': carpeta_prop['id']}]})
                    with open(video.name, "wb") as f: f.write(video.getbuffer())
                    f_v.SetContentFile(video.name)
                    f_v.Upload()
                    os.remove(video.name)

                # Subir Fotos
                if fotos:
                    for i, foto in enumerate(fotos):
                        f_f = drive.CreateFile({'title': f"foto_{i}.jpg", 'parents': [{'id': carpeta_prop['id']}]})
                        with open(foto.name, "wb") as f: f.write(foto.getbuffer())
                        f_f.SetContentFile(foto.name)
                        f_f.Upload()
                        os.remove(foto.name)
                
                st.success(f"✅ ¡'{titulo}' guardado con éxito! Ya podés verlo en tu Drive.")
        else:
            st.warning("Falta el título o los archivos.")
