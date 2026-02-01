import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- CONEXIÓN ---
@st.cache_resource
def get_conn():
    try:
        return st.connection("gdrive", type=FilesConnection)
    except:
        return None

conn = get_conn()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🖼️ Galería", "🔐 Panel de Carga"])
    
    st.markdown("---")
    st.subheader("Contacto")
    # Botones con colores originales forzados
    st.markdown(f'''
        <a href="https://wa.me/5493513083986" style="text-decoration:none;">
            <div style="background-color:#25D366;color:white;padding:10px;border-radius:5px;text-align:center;margin-bottom:10px;font-weight:bold;">WhatsApp</div>
        </a>
        <a href="https://www.instagram.com/cortes.inmo/" style="text-decoration:none;">
            <div style="background-color:#E4405F;color:white;padding:10px;border-radius:5px;text-align:center;margin-bottom:10px;font-weight:bold;">Instagram</div>
        </a>
        <a href="https://www.tiktok.com/@cortes.inmobiliaria" style="text-decoration:none;">
            <div style="background-color:#000000;color:white;padding:10px;border-radius:5px;text-align:center;margin-bottom:10px;font-weight:bold;">TikTok</div>
        </a>
    ''', unsafe_allow_html=True)

# --- SECCIONES ---
if menu == "🖼️ Galería":
    st.title("🏠 Nuestras Propiedades")
    st.info("Sincronizando con la base de datos...")

else:
    st.title("🔐 Cargar Propiedad")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("formulario_carga", clear_on_submit=True):
            titulo = st.text_input("Título de la Propiedad (Obligatorio)")
            precio = st.text_input("Precio USD")
            descripcion = st.text_area("Descripción")
            archivos = st.file_uploader("Fotos/Videos", accept_multiple_files=True)
            
            submit = st.form_submit_button("🚀 PUBLICAR")
            
            if submit:
                if not titulo or not archivos:
                    st.error("⚠️ Error: Debes poner un título y elegir al menos una foto.")
                elif conn is None:
                    st.error("❌ Error de conexión con Drive. Revisá los Secrets.")
                else:
                    with st.spinner("Subiendo a Google Drive..."):
                        for arc in archivos:
                            ruta = f"gdrive://DB_Cortes_Inmo/{titulo}/{arc.name}"
                            try:
                                with conn.open(ruta, "wb") as f:
                                    f.write(arc.getbuffer())
                                st.success(f"✅ ¡{arc.name} subido!")
                            except Exception as e:
                                st.error(f"Fallo en {arc.name}: {e}")
