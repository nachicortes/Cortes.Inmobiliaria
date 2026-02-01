import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- CONEXIÓN BLINDADA ---
@st.cache_resource
def get_connection():
    try:
        return st.connection("gdrive", type=FilesConnection)
    except Exception:
        return None

conn = get_connection()

# --- DISEÑO ORIGINAL (COLORES Y REDES) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🖼️ Galería", "🔐 Panel de Carga"])
    st.markdown("---")
    st.subheader("Contacto")
    st.markdown("[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white)](https://wa.me/5493513083986)")
    st.markdown("[![Instagram](https://img.shields.io/badge/Instagram-E4405F?logo=instagram&logoColor=white)](https://www.instagram.com/cortes.inmo/)")
    st.markdown("[![TikTok](https://img.shields.io/badge/TikTok-000000?logo=tiktok&logoColor=white)](https://www.tiktok.com/@cortes.inmobiliaria)")

if menu == "🖼️ Galería":
    st.title("🏠 Nuestras Propiedades")
    if conn:
        st.info("Conexión con Drive establecida. Cargando catálogo...")
    else:
        st.warning("Aguardando conexión con la base de datos...")

else:
    st.title("🔐 Cargar Nueva Propiedad")
    clave = st.text_input("Contraseña:", type="password")
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("carga", clear_on_submit=True):
            t = st.text_input("Título (Ej: Casa Valle Escondido)")
            p = st.text_input("Precio USD")
            desc = st.text_area("Descripción")
            fotos = st.file_uploader("Fotos/Videos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and t and fotos:
                    for foto in fotos:
                        # Usamos la carpeta que compartiste ayer
                        ruta = f"gdrive://DB_Cortes_Inmo/{t}/{foto.name}"
                        try:
                            with conn.open(ruta, "wb") as f:
                                f.write(foto.getbuffer())
                            st.success(f"✅ Subido: {foto.name}")
                        except Exception as e:
                            st.error(f"Error al subir: {e}")
                else:
                    st.error("Faltan datos o la conexión falló.")
