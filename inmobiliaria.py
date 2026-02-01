import streamlit as st
from st_files_connection import FilesConnection

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- 2. ESTILOS (BOTONES CON TUS COLORES) ---
st.markdown("""
    <style>
    .btn-side { padding: 12px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; }
    .ig { background-color: #E4405F; }
    .tk { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN DIRECTA ---
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception:
    conn = None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Secciones:", ["🏠 Galería", "📂 Cargar"])
    st.markdown("---")
    st.markdown('<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side tk" href="https://www.tiktok.com/@cortes.inmobiliaria">TikTok</a>', unsafe_allow_html=True)

# --- 5. LÓGICA ---
if menu == "📂 Cargar":
    st.title("📂 Panel de Carga")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        with st.form("form_final", clear_on_submit=True):
            titulo = st.text_input("Nombre de la Propiedad")
            precio = st.text_input("Precio USD")
            fotos = st.file_uploader("Fotos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and titulo and fotos:
                    with st.spinner("Subiendo..."):
                        for f in fotos:
                            # Ruta corregida para tu carpeta DB_Cortes_Inmo
                            path = f"gdrive://DB_Cortes_Inmo/{titulo}/{f.name}"
                            with conn.open(path, "wb") as fp:
                                fp.write(f.getbuffer())
                        st.success(f"✅ ¡{titulo} publicado con éxito!")
                else:
                    st.error("Error: Revisá que pusiste título, fotos y los Secrets.")
else:
    st.title("🏠 Galería")
    st.info("Sincronizando catálogo con Google Drive...")

