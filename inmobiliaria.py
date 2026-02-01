import streamlit as st
from st_files_connection import FilesConnection

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- 2. CONEXIÓN (Aquí se define 'conn') ---
conn = st.connection("gdrive", type=FilesConnection)

# --- 3. BARRA LATERAL (Tus Redes y Logo) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🖼️ Galería de Propiedades", "🔐 Panel de Carga"])
    st.markdown("---")
    st.subheader("Contacto")
    st.markdown("[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white)](https://wa.me/5493513083986)")
    st.markdown("[![Instagram](https://img.shields.io/badge/Instagram-E4405F?logo=instagram&logoColor=white)](https://www.instagram.com/cortes.inmo/)")
    st.markdown("[![TikTok](https://img.shields.io/badge/TikTok-000000?logo=tiktok&logoColor=white)](https://www.tiktok.com/@cortes.inmobiliaria)")

# --- 4. SECCIONES ---
if menu == "🖼️ Galería de Propiedades":
    st.title("🏠 Nuestras Propiedades")
    st.info("Sincronizando con Google Drive...")
    # Mañana activamos la visualización automática aquí

else:
    st.title("🔐 Panel de Administración")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        st.success("¡Bienvenido, Ignacio!")
        with st.form("carga_completa", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                titulo = st.text_input("Título de la Propiedad")
                precio = st.text_input("Precio USD")
                ubicacion = st.text_input("Ubicación")
            with col2:
                descripcion = st.text_area("Descripción")
                pdf = st.file_uploader("Subir PDF", type="pdf")
            
            archivos = st.file_uploader("Subir Fotos/Videos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR AHORA"):
                if titulo and archivos:
                    with st.spinner("Subiendo a Drive..."):
                        for arc in archivos:
                            # Ruta: carpeta compartida / título / nombre de archivo
                            ruta = f"gdrive://DB_Cortes_Inmo/{titulo}/{arc.name}"
                            try:
                                with conn.open(ruta, "wb") as f:
                                    f.write(arc.getbuffer())
                                st.success(f"✅ Subido: {arc.name}")
                            except Exception as e:
                                st.error(f"Error en {arc.name}: {e}")
                else:
                    st.warning("Faltan datos obligatorios.")
