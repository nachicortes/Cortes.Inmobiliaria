import streamlit as st
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURACIÓN DRIVE (REFORZADA) ---
@st.cache_resource
def iniciar_drive():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

drive = iniciar_drive()
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S" 

st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide", page_icon="🏠")

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    # El cliente cae acá por defecto
    menu = st.radio("Secciones:", ["🖼️ Ver Propiedades", "🔐 Acceso Dueño"])
    st.markdown("---")
    st.markdown("### 📞 Contacto")
    st.write("📱 [WhatsApp](https://wa.me/5493513083986)")
    st.write("📸 [Instagram](https://www.instagram.com/cortes.inmo/)")

# --- 3. LÓGICA DE PÁGINAS ---

if menu == "🖼️ Ver Propiedades":
    st.title("🏡 Nuestras Propiedades Disponibles")
    
    if drive:
        try:
            # Buscamos las carpetas de propiedades
            query = f"'{ID_CARPETA_RAIZ}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            lista_propiedades = drive.ListFile({'q': query}).GetList()

            if not lista_propiedades:
                st.info("Próximamente subiremos nuevas oportunidades.")
            else:
                for prop in lista_propiedades:
                    with st.expander(f"📍 {prop['title']}", expanded=False):
                        # Buscamos fotos dentro de la carpeta
                        fotos = drive.ListFile({'q': f"'{prop['id']}' in parents and trashed = false"}).GetList()
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.subheader("Información")
                            st.write(f"Detalles de la ubicación y precio en el título.")
                            st.link_button("Consultar por WhatsApp", f"https://wa.me/5493513083986?text=Hola! Me interesa: {prop['title']}")
                        
                        with col2:
                            for f in fotos:
                                if "foto" in f['title'].lower():
                                    st.image(f['thumbnailLink'], use_container_width=True)
        except Exception:
            st.warning("🔄 Refrescá la página (F5) para cargar el catálogo.")

elif menu == "🔐 Acceso Dueño":
    st.title("Panel Administrativo")
    clave = st.text_input("Contraseña de acceso:", type="password")
    
    if clave == "cortes2026": # Tu clave secreta
        st.success("¡Bienvenido, Ignacio!")
        
        with st.form("nueva_carga", clear_on_submit=True):
            t = st.text_input("Título (Ej: Casa 3 dorm. Valle Escondido)")
            p = st.number_input("Precio USD", min_value=0)
            archivos = st.file_uploader("Subir Fotos/Video", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR AHORA"):
                if t and archivos:
                    with st.spinner("Subiendo a Drive..."):
                        # Creamos carpeta
                        folder = drive.CreateFile({'title': f"{t} - USD {p}", 'parents': [{'id': ID_CARPETA_RAIZ}], 'mimeType': 'application/vnd.google-apps.folder'})
                        folder.Upload()
                        # Subimos archivos
                        for arc in archivos:
                            f_drive = drive.CreateFile({'title': arc.name, 'parents': [{'id': folder['id']}]})
                            with open(arc.name, "wb") as local_f: local_f.write(arc.getbuffer())
                            f_drive.SetContentFile(arc.name)
                            f_drive.Upload()
                            os.remove(arc.name)
                        st.success("¡Propiedad publicada!")
    elif clave != "":
        st.error("Clave incorrecta")
