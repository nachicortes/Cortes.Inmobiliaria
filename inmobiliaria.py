import streamlit as st
import os
import time
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DRIVE ---
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S"

@st.cache_resource
def iniciar_conexion():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except:
        return None

drive = iniciar_conexion()
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    menu = st.radio("Secciones:", ["🖼️ Catálogo", "🔐 Cargar Propiedad"])

if menu == "🖼️ Catálogo":
    st.title("🏡 Nuestras Propiedades")
    if drive:
        try:
            query = f"'{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            carpetas = drive.ListFile({'q': query}).GetList()
            if not carpetas: st.info("No hay propiedades publicadas.")
            for c in carpetas:
                with st.expander(f"📍 {c['title']}"):
                    st.link_button("Consultar por WhatsApp", f"https://wa.me/5493513083986?text=Me interesa: {c['title']}")
        except:
            st.error("Error al cargar. Refrescá con F5.")

elif menu == "🔐 Cargar Propiedad":
    st.title("Panel de Carga")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("carga_mejorada", clear_on_submit=False): # No se limpia hasta que termine
            titulo = st.text_input("Nombre de la Propiedad y Precio")
            archivos = st.file_uploader("Subir Fotos y Video (Máx 200MB)", accept_multiple_files=True)
            enviar = st.form_submit_button("🚀 PUBLICAR")
            
            if enviar:
                if drive and titulo and archivos:
                    # Contenedor de progreso para que el usuario vea qué pasa
                    status = st.empty()
                    progreso = st.progress(0)
                    
                    try:
                        # 1. Crear Carpeta primero
                        status.info("📁 Creando carpeta en Drive...")
                        folder = drive.CreateFile({'title': titulo, 'parents': [{'id': ID_CARPETA_RAIZ}], 'mimeType': 'application/vnd.google-apps.folder'})
                        folder.Upload()
                        
                        # 2. Subir archivos uno por uno con pausa para no saturar
                        for i, arc in enumerate(archivos):
                            status.info(f"📤 Subiendo: {arc.name} (Archivo {i+1} de {len(archivos)})")
                            f_drive = drive.CreateFile({'title': arc.name, 'parents': [{'id': folder['id']}]})
                            
                            # Guardar temporalmente para asegurar la subida del video
                            with open(arc.name, "wb") as f:
                                f.write(arc.getbuffer())
                            
                            f_drive.SetContentFile(arc.name)
                            f_drive.Upload()
                            os.remove(arc.name) # Borrar temporal
                            
                            progreso.progress((i + 1) / len(archivos))
                            time.sleep(1) # Pausa de seguridad
                            
                        status.success(f"✅ ¡{titulo} publicado con éxito!")
                    except Exception as e:
                        status.error(f"❌ Error: El video es muy pesado o se perdió la conexión. Intentá subirlo solo.")
                else:
                    st.warning("Faltan datos o conexión.")
