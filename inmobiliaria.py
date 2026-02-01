import streamlit as st
from st_files_connection import FilesConnection

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- 2. CONEXIÓN ---
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception:
    conn = None

# --- 3. BARRA LATERAL (CON TUS COLORES) ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🖼️ Catálogo", "📂 Cargar Propiedad"])
    st.markdown("---")
    
    st.markdown("### Contacto")
    # Estilo para forzar colores originales
    st.markdown("""
        <style>
        .wa { background-color: #25D366 !important; color: white !important; padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; font-weight: bold; }
        .ig { background-color: #E4405F !important; color: white !important; padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; font-weight: bold; }
        .tk { background-color: #000000 !important; color: white !important; padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; font-weight: bold; }
        </style>
        <a class="wa" href="https://wa.me/5493513083986">WhatsApp</a>
        <a class="ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>
        <a class="tk" href="https://www.tiktok.com/@cortes.inmobiliaria">TikTok</a>
    """, unsafe_allow_html=True)

# --- 4. PANEL DE CARGA ---
if menu == "📂 Cargar Propiedad":
    st.title("📂 Cargar Nueva Propiedad")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        with st.form("carga_final", clear_on_submit=True):
            t = st.text_input("Título de la Propiedad")
            p = st.text_input("Precio USD")
            f = st.file_uploader("Subir Fotos/Videos", accept_multiple_files=True)
            pdf = st.file_uploader("Ficha PDF", type="pdf")
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and t and f:
                    with st.spinner("Subiendo archivos..."):
                        for archivo in f:
                            ruta = f"gdrive://DB_Cortes_Inmo/{t}/{archivo.name}"
                            with conn.open(ruta, "wb") as file:
                                file.write(archivo.getbuffer())
                        st.success(f"✅ ¡{t} publicado con éxito!")
                else:
                    st.error("Error: Revisá que pusiste título y fotos, y que los Secrets estén bien.")

else:
    st.title("🏠 Catálogo")
    st.info("Sincronizando con Google Drive...")
