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

# --- 2. DISEÑO CON BARRA LATERAL ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

# Barra Lateral con Logo y Redes a Color
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    st.markdown("### 📞 Contacto Rápido")
    
    # Botones con colores originales en el sidebar
    st.markdown(f"""
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="https://wa.me/5493513083986" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold;">WhatsApp</div>
            </a>
            <a href="https://www.instagram.com/cortes.inmo/" target="_blank" style="text-decoration: none;">
                <div style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2397 75%, #bc1888 100%); color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold;">Instagram</div>
            </a>
            <a href="https://www.tiktok.com/@cortes.inmobiliaria" target="_blank" style="text-decoration: none;">
                <div style="background-color: #000000; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #ee1d52;">TikTok</div>
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 3. PANEL DE CARGA ---
st.title("🏠 Panel de Gestión de Propiedades")

with st.form("registro_drive", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        titulo = st.text_input("Nombre de la Propiedad", placeholder="Ej: Departamento 2 dorm. Nueva Cba")
        precio = st.number_input("Precio (USD)", min_value=0, step=500)
    with col_b:
        tipo = st.selectbox("Categoría", ["Casa", "Departamento", "Lote", "Local", "Campo"])
        descripcion = st.text_area("Descripción y Notas", height=68)

    col_v, col_f = st.columns(2)
    with col_v:
        video = st.file_uploader("Video (MP4/MOV)", type=["mp4", "mov"])
    with col_f:
        fotos = st.file_uploader("Fotos (JPG/PNG/HEIC)", type=["jpg", "png", "jpeg", "heic"], accept_multiple_files=True)
    
    submit = st.form_submit_button("🚀 GUARDAR EN GOOGLE DRIVE", use_container_width=True)
    
    if submit:
        if titulo and (video or fotos):
            with st.spinner("Subiendo archivos..."):
                folder_meta = {
                    'title': f"{titulo} - USD {precio}",
                    'parents': [{'id': ID_CARPETA_RAIZ}],
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                carpeta = drive.CreateFile(folder_meta)
                carpeta.Upload()
