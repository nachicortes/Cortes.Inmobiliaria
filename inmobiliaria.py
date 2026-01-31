import streamlit as st
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

ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" # Tu carpeta DB_Cortes_Inmo

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

# --- 2. BARRA LATERAL (LOGO Y NAVEGACIÓN) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🖼️ Galería de Propiedades", "⚙️ Panel de Carga (Privado)"])
    st.markdown("---")
    st.markdown("### 📞 Contacto")
    st.write("📱 [WhatsApp](https://wa.me/5493513083986)") #
    st.write("📸 [Instagram](https://www.instagram.com/cortes.inmo/)") #

# --- 3. LÓGICA DE PÁGINAS ---

if menu == "🖼️ Galería de Propiedades":
    st.title("🏡 Nuestras Propiedades")
    
    # Listar carpetas de Drive (Cada carpeta es una propiedad)
    lista_carpetas = drive.ListFile({
        'q': f"'{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    }).GetList()

    if not lista_carpetas:
        st.info("Aún no hay propiedades publicadas.")
    else:
        for carpeta in lista_carpetas:
            with st.expander(f"📍 {carpeta['title']}", expanded=False):
                col_info, col_media = st.columns([1, 2])
                
                # Buscar archivos dentro de la carpeta de la propiedad
                archivos = drive.ListFile({'q': f"'{carpeta['id']}' in parents and trashed = false"}).GetList()
                
                with col_info:
                    st.write("### Detalles")
                    st.write(f"**Nombre:** {carpeta['title']}")
                    st.button("Consultar por esta propiedad", key=carpeta['id'])
                
                with col_media:
                    # Mostrar fotos y videos encontrados
                    for archivo in archivos:
                        if "foto" in archivo['title'].lower():
                            st.image(archivo['thumbnailLink'], caption="Foto de la propiedad", use_container_width=True)
                        elif "video" in archivo['title'].lower():
                            st.video(archivo['webContentLink'])

elif menu == "⚙️ Panel de Carga (Privado)":
    st.title("🔐 Acceso Administrativo")
    # Una clave simple para que no cualquiera cargue cosas
    password = st.text_input("Ingresá la clave para cargar:", type="password")
    
    if password == "cortes2026": # Podés cambiar esta clave
        st.success("Acceso concedido")
        # Aquí va tu formulario de carga anterior
        with st.form("carga_nueva", clear_on_submit=True):
            titulo = st.text_input("Nombre de la Propiedad")
            precio = st.number_input("Precio (USD)", min_value=0)
            video = st.file_uploader("Subir Video", type=["mp4", "mov"])
            fotos = st.file_uploader("Subir Fotos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                # Lógica de subida a Drive (la que ya tenías funcionando)
                st.info("Subiendo archivos...")
                # ... (resto del código de subida)
    else:
        st.warning("Por favor, ingresá la clave para gestionar las propiedades.")
