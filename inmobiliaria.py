import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DRIVE ---
ID_CARPETA_RAIZ = "17Yy2_XN-x_LpQ_f_56pW7y_L_N0_S"

@st.cache_resource
def conectar_drive():
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"] 
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gauth = GoogleAuth()
        gauth.credentials = creds
        return GoogleDrive(gauth)
    except:
        return None

st.set_page_config(page_title="Cortes Inmobiliaria", layout="centered")
drive = conectar_drive()

# --- INTERFAZ ---
st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", width=200)

menu = st.tabs(["🖼️ Catálogo", "🔐 Cargar"])

with menu[0]:
    st.title("Propiedades")
    if drive:
        try:
            items = drive.ListFile({'q': f"'{ID_CARPETA_RAIZ}' in parents and trashed = false"}).GetList()
            for item in items:
                st.write(f"✅ {item['title']}")
        except:
            st.error("Error al leer Drive.")

with menu[1]:
    clave = st.text_input("Contraseña:", type="password")
    if clave == "cortes2026":
        with st.form("subida"):
            nombre = st.text_input("Nombre de la Foto/Propiedad")
            archivos = st.file_uploader("Elegir archivos", accept_multiple_files=True)
            if st.form_submit_button("🚀 SUBIR AHORA"):
                if drive and archivos:
                    for arc in archivos:
                        try:
                            # Subida directa desde memoria
                            f = drive.CreateFile({'title': f"{nombre}_{arc.name}", 'parents': [{'id': ID_CARPETA_RAIZ}]})
                            f.content = arc
                            f.Upload()
                            st.success(f"Subido: {arc.name}")
                        except Exception as e:
                            st.error(f"Error en {arc.name}: {e}")
