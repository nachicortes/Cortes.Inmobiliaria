import streamlit as st
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DRIVE ---
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S"

def obtener_drive():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except Exception as e:
        return None

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🖼️ Ver Propiedades", "🔐 Acceso Dueño"])

# --- LÓGICA DE PÁGINAS ---
drive = obtener_drive()

if menu == "🖼️ Ver Propiedades":
    st.title("🏡 Catálogo de Propiedades")
    if drive:
        try:
            query = f"'{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            carpetas = drive.ListFile({'q': query}).GetList()
            if not carpetas:
                st.info("No hay propiedades cargadas aún.")
            for c in carpetas:
                with st.expander(f"📍 {c['title']}"):
                    st.write("Cargando archivos...")
                    # Botón de consulta directo
                    st.link_button("Consultar por WhatsApp", f"https://wa.me/5493513083986?text=Me interesa: {c['title']}")
        except:
            st.error("Error al leer el catálogo. Refrescá la página.")
    else:
        st.error("No se pudo conectar con Google Drive.")

elif menu == "🔐 Acceso Dueño":
    st.title("Panel de Carga")
    clave = st.text_input("Clave:", type="password")
    
    if clave == "cortes2026":
        st.success("¡Hola Ignacio!")
        with st.form("carga", clear_on_submit=True):
            t = st.text_input("Título Propiedad")
            p = st.number_input("Precio USD", min_value=0)
            archivos = st.file_uploader("Fotos/Videos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if drive and t and archivos:
                    try:
                        with st.spinner("Subiendo... por favor no cierres la pestaña"):
                            folder = drive.CreateFile({'title': f"{t} - USD {p}", 'parents': [{'id': ID_CARPETA_RAIZ}], 'mimeType': 'application/vnd.google-apps.folder'})
                            folder.Upload()
                            for arc in archivos:
                                f_drive = drive.CreateFile({'title': arc.name, 'parents': [{'id': folder['id']}]})
                                f_drive.SetContentString(arc.read()) # Método alternativo más estable para la nube
                                f_drive.Upload()
                            st.success("¡Publicado con éxito!")
                    except Exception as e:
                        st.error(f"Error al subir: {e}. Intentá con menos archivos a la vez.")
                else:
                    st.warning("Faltan datos o falló la conexión.")
