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

# --- 2. DISEÑO DE PÁGINA COMPACTO ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

# Logo Centrado y más CHICO (ancho 150px en lugar de automático)
col_l1, col_l2, col_l3 = st.columns([2, 1, 2])
with col_l2:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", width=150)

# Botones de Redes Sociales en una sola línea y más pequeños
st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: -10px; margin-bottom: 20px;">
        <a href="https://wa.me/5493513083986" target="_blank" style="text-decoration: none; font-size: 12px;">
            <div style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold;">WhatsApp</div>
        </a>
        <a href="https://www.instagram.com/cortes.inmo/" target="_blank" style="text-decoration: none; font-size: 12px;">
            <div style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2397 75%, #bc1888 100%); color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold;">Instagram</div>
        </a>
        <a href="https://www.tiktok.com/@cortes.inmobiliaria" target="_blank" style="text-decoration: none; font-size: 12px;">
            <div style="background-color: #000000; color: white; padding: 5px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #ee1d52;">TikTok</div>
        </a>
    </div>
""", unsafe_allow_html=True)

# --- 3. PANEL DE CARGA ---
# Usamos un título más chico para ganar espacio
st.markdown("<h4 style='text-align: center; margin-top: -10px;'>Panel de Carga</h4>", unsafe_allow_html=True)

with st.form("registro_drive", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        titulo = st.text_input("Propiedad", placeholder="Ej: Depto Nueva Córdoba")
        precio = st.number_input("Precio (USD)", min_value=0, step=500)
    with c2:
        tipo = st.selectbox("Tipo", ["Casa", "Departamento", "Lote", "Local", "Campo"])
        descripcion = st.text_input("Breve descripción") # Cambiado a text_input para que sea más petizo

    col_v, col_f = st.columns(2)
    with col_v:
        video = st.file_uploader("Video", type=["mp4", "mov"])
    with col_f:
        fotos = st.file_uploader("Fotos", type=["jpg", "png", "jpeg", "heic"], accept_multiple_files=True)
    
    boton = st.form_submit_button("🚀 SUBIR A DRIVE", use_container_width=True)
    
    if boton:
        if titulo and (video or fotos):
            with st.spinner("Sub
