import streamlit as st
from st_files_connection import FilesConnection

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- 2. CONEXIÓN A DRIVE ---
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    conn = None

# --- 3. DISEÑO Y BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🖼️ Galería de Propiedades", "🔐 Panel de Carga"])
    
    st.markdown("---")
    st.subheader("Contacto")
    st.markdown("[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white)](https://wa.me/5493513083986)")
    st.markdown("[![Instagram](https://img.shields.io/badge/Instagram-E4405F?logo=instagram&logoColor=white)](https://www.instagram.com/cortes.inmo/)")
    st.markdown("[![TikTok](https://img.shields.io/badge/TikTok-000000?logo=tiktok&logoColor=white)](https://www.tiktok.com/@cortes.inmobiliaria?_r=1&_t=ZS-93Wzt9Gbfd6)")

# --- 4. LÓGICA DE LAS SECCIONES ---
if menu == "🖼️ Galería de Propiedades":
    st.title("🏡 Nuestras Propiedades")
    if conn:
        try:
            # Listamos las carpetas dentro de DB_Cortes_Inmo
            archivos = conn.fs.ls("gdrive://DB_Cortes_Inmo")
            if not archivos:
                st.info("Todavía no hay propiedades cargadas.")
            for arc in archivos:
                nombre = arc.split('/')[-1]
                if nombre not in [".DS_Store", "db_inmuebles.csv"]:
                    with st.expander(f"📍 {nombre}"):
                        st.write("Detalles de la propiedad próximamente...")
                        st.link_button("Consultar por WhatsApp", f"https://wa.me/5493513083986?text=Me interesa: {nombre}")
        except:
            st.warning("Sincronizando con Drive...")

else:
    st.title("🔐 Panel de Administración")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        st.success("¡Hola Ignacio!")
        with st.form("carga_inmo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                t = st.text_input("Título (Ej: Casa 3 dorm. Valle Escondido)")
                p = st.text_input("Precio USD")
            with col2:
                u = st.text_input("Ubicación")
                pdf = st.file_uploader("Ficha PDF", type="pdf")
            
            fotos = st.file_uploader("Fotos y Videos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and t and fotos:
                    with st.spinner("Subiendo archivos a Drive..."):
                        for foto in fotos:
                            ruta = f"gdrive://DB_Cortes_Inmo/{t}/{foto.name}"
                            with conn.open(ruta, "wb") as f:
                                f.write(foto.getbuffer())
                    st.success(f"✅ ¡{t} publicado con éxito!")
                else:
                    st.warning("Completá el título y elegí al menos una foto.")
