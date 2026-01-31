import streamlit as st
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DRIVE ---
scope = ['https://www.googleapis.com/auth/drive']
creds_dict = st.secrets["gcp_service_account"] 
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" 

# --- 2. DISEÑO DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

# Logo Centrado
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)

# Título y Redes con Colores Originales
st.markdown("<h1 style='text-align: center;'>Panel de Gestión</h1>", unsafe_allow_html=True)

# Botones de Redes Sociales Centrados y con sus Colores
st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 30px;">
        <a href="https://wa.me/5493513083986" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold;">
                WhatsApp
            </div>
        </a>
        <a href="https://www.instagram.com/cortes.inmo/" target="_blank" style="text-decoration: none;">
            <div style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2397 75%, #bc1888 100%); color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold;">
                Instagram
            </div>
        </a>
        <a href="https://www.tiktok.com/@cortes.inmobiliaria" target="_blank" style="text-decoration: none;">
            <div style="background-color: #000000; color: white; padding: 10px 20px; border-radius: 10px; font-weight: bold; border: 2px solid #ee1d52;">
                TikTok
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

# --- 3. PANEL DE CARGA ---
with st.expander("➕ Cargar Nueva Propiedad", expanded=True):
    with st.form("registro_drive", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Nombre de la Propiedad")
            precio = st.number_input("Precio (USD)", min_value=0, step=500)
        with c2:
            tipo = st.selectbox("Tipo", ["Casa", "Departamento", "Lote", "Local", "Campo"])
            descripcion = st.text_area("Descripción/Notas")

        video = st.file_uploader("Seleccioná el Video (MP4/MOV)", type=["mp4", "mov"])
        fotos = st.file_uploader("Seleccioná las Fotos", type=["jpg", "png", "jpeg", "heic"], accept_multiple_files=True)
        
        boton = st.form_submit_button("🚀 SUBIR PROPIEDAD A DRIVE")
        
        if boton:
            if titulo and (video or fotos):
                with st.spinner("Subiendo archivos a tu Drive..."):
                    # Crear carpeta
                    folder_name = f"{titulo} - USD {precio}"
                    carpeta_prop = drive.CreateFile({
                        'title': folder_name,
                        'parents': [{'id': ID_CARPETA_RAIZ}],
                        'mimeType': 'application/vnd.google-apps.folder'
                    })
                    carpeta_prop.Upload()
                    
                    # Subir archivos (Video y Fotos)
                    if video:
                        f_v = drive.CreateFile({'title': f"video_{titulo}.mov", 'parents': [{'id': carpeta_prop['id']}]})
                        with open(video.name, "wb") as f: f.write(video.getbuffer())
                        f_v.SetContentFile(video.name)
                        f_v.Upload()
                        os.remove(video.name)

                    if fotos:
                        for i, foto in enumerate(fotos):
                            f_f = drive.CreateFile({'title': f"foto_{i}.jpg", 'parents': [{'id': carpeta_prop['id']}]})
                            with open(foto.name, "wb") as f: f.write(foto.getbuffer())
                            f_f.SetContentFile(foto.name)
                            f_f.Upload()
                            os.remove(foto.name)
                    
                    st.success(f"✅ ¡'{titulo}' guardado con éxito en Drive!")
            else:
                st.warning("Completá el título y cargá al menos un archivo.")
