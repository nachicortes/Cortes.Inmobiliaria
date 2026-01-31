import streamlit as st
import os
import time
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DRIVE (ESTABLE) ---
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S"

@st.cache_resource
def obtener_drive():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except:
        return None

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")
drive = obtener_drive()

# --- INTERFAZ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🖼️ Ver Propiedades", "🔐 Acceso Dueño"])

if menu == "🖼️ Ver Propiedades":
    st.title("🏡 Catálogo")
    if drive:
        try:
            query = f"'{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            carpetas = drive.ListFile({'q': query}).GetList()
            if not carpetas: st.info("No hay propiedades.")
            for c in carpetas:
                with st.expander(f"📍 {c['title']}"):
                    st.link_button("Consultar WhatsApp", f"https://wa.me/5493513083986?text=Me interesa: {c['title']}")
        except:
            st.warning("La conexión está lenta. Refrescá con F5.")
    else:
        st.error("Error de conexión con el servidor de datos.")

elif menu == "🔐 Acceso Dueño":
    st.title("Panel de Carga")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        st.success("¡Hola Ignacio!")
        with st.form("carga", clear_on_submit=True):
            t = st.text_input("Título Propiedad")
            p = st.number_input("Precio USD", min_value=0)
            archivos = st.file_uploader("Fotos/Videos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if drive and t and archivos:
                    try:
                        with st.spinner("Publicando... por favor esperá"):
                            # Crear carpeta con reintento
                            folder = drive.CreateFile({'title': f"{t} - USD {p}", 'parents': [{'id': ID_CARPETA_RAIZ}], 'mimeType': 'application/vnd.google-apps.folder'})
                            folder.Upload()
                            
                            for arc in archivos:
                                f_drive = drive.CreateFile({'title': arc.name, 'parents': [{'id': folder['id']}]})
                                # Usamos upload directo para evitar errores de servidor
                                f_drive.SetContentFile(os.path.join(os.getcwd(), arc.name))
                                with open(arc.name, "wb") as f:
                                    f.write(arc.getbuffer())
                                f_drive.Upload()
                                os.remove(arc.name)
                                time.sleep(1) # Pausa técnica para no saturar el servidor
                            st.success("¡Propiedad publicada con éxito!")
                    except Exception as e:
                        st.error(f"El servidor está ocupado. Intentá de nuevo con menos fotos.")
                else:
                    st.warning("Completá todos los campos.")
