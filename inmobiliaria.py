import streamlit as st
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONEXIÓN A GOOGLE DRIVE ---
# Usamos el nombre que pusiste en Secrets
scope = ['https://www.googleapis.com/auth/drive']
creds_dict = st.secrets["gcp_service_account"] 
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

# --- 2. TU ID DE CARPETA (YA CONFIGURADO) ---
# Este es el código que sacamos de tu URL de Drive
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" 

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

st.title("🏠 Cortes Inmobiliaria - Panel de Carga")

# --- 3. FORMULARIO DE CARGA ---
with st.form("registro_drive", clear_on_submit=True):
    titulo = st.text_input("Nombre de la Propiedad (ej: Casa en Valle Escondido)")
    video = st.file_uploader("Seleccioná el Video (MP4)", type=["mp4"])
    
    boton = st.form_submit_button("Subir Propiedad a Drive")
    
    if boton:
        if titulo and video:
            with st.spinner("Subiendo video a Google Drive..."):
                # Crear archivo en Drive
                archivo_drive = drive.CreateFile({
                    'title': f"{titulo}.mp4",
                    'parents': [{'id': ID_CARPETA_RAIZ}]
                })
                
                # Guardar temporalmente para subirlo
                with open(video.name, "wb") as f:
                    f.write(video.getbuffer())
                
                archivo_drive.SetContentFile(video.name)
                archivo_drive.Upload()
                
                # Borrar archivo temporal de la nube de Streamlit
                os.remove(video.name)
                
                st.success(f"✅ ¡Video de '{titulo}' subido con éxito a tu Drive!")
        else:
            st.warning("Por favor, poné un título y seleccioná un video.")

st.divider()
st.info("Recordá que podés ver tus videos directamente en tu carpeta 'DB_Cortes_Inmo' de Google Drive.")
