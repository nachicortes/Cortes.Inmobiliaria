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

# TU ID DE CARPETA
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" 

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

st.title("🏠 Cortes Inmobiliaria - Panel de Carga")

# --- 2. FORMULARIO DE CARGA ---
with st.form("registro_drive", clear_on_submit=True):
    titulo = st.text_input("Nombre de la Propiedad (ej: Departamento Nueva Córdoba)")
    
    # Campo para el Video (acepta iPhone y Android)
    video = st.file_uploader("Seleccioná el Video", type=["mp4", "mov"])
    
    # Campo para las Fotos (permite elegir varias)
    fotos = st.file_uploader("Seleccioná las Fotos", type=["jpg", "png", "jpeg", "heic"], accept_multiple_files=True)
    
    boton = st.form_submit_button("Subir Todo a Drive")
    
    if boton:
        if titulo and (video or fotos):
            with st.spinner("Subiendo archivos a Google Drive..."):
                # 1. Crear una carpeta específica para esta propiedad
                carpeta_prop = drive.CreateFile({
                    'title': titulo,
                    'parents': [{'id': ID_CARPETA_RAIZ}],
                    'mimeType': 'application/vnd.google-apps.folder'
                })
                carpeta_prop.Upload()
                
                # 2. Subir el Video
                if video:
                    ext_v = video.name.split('.')[-1]
                    f_v = drive.CreateFile({'title': f"video_{titulo}.{ext_v}", 'parents': [{'id': carpeta_prop['id']}]})
                    with open(video.name, "wb") as f:
                        f.write(video.getbuffer())
                    f_v.SetContentFile(video.name)
                    f_v.Upload()
                    os.remove(video.name)

                # 3. Subir las Fotos
                if fotos:
                    for i, foto in enumerate(fotos):
                        ext_f = foto.name.split('.')[-1]
                        f_f = drive.CreateFile({'title': f"foto_{i}_{titulo}.{ext_f}", 'parents': [{'id': carpeta_prop['id']}]})
                        with open(foto.name, "wb") as f:
                            f.write(foto.getbuffer())
                        f_f.SetContentFile(foto.name)
                        f_f.Upload()
                        os.remove(foto.name)
                
                st.success(f"✅ ¡Todo subido con éxito a la carpeta '{titulo}' en tu Drive!")
        else:
            st.warning("Por favor, poné un título y al menos una foto o video.")
