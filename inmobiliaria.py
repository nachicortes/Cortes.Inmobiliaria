import streamlit as st
from st_files_connection import FilesConnection

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- 2. ESTILOS (TUS COLORES REALES) ---
st.markdown("""
    <style>
    .btn-c { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; }
    .ig { background-color: #E4405F; }
    .tk { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN ---
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception:
    conn = None

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🏠 Galería", "📂 Panel de Carga"])
    st.markdown("---")
    st.markdown(f'<a class="btn-c wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-c ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-c tk" href="https://www.tiktok.com/@cortes.inmobiliaria">TikTok</a>', unsafe_allow_html=True)

# --- 5. LÓGICA ---
if menu == "📂 Panel de Carga":
    st.title("📂 Cargar Propiedad")
    clave = st.text_input("Contraseña:", type="password")
    if clave == "cortes2026":
        with st.form("carga", clear_on_submit=True):
            t = st.text_input("Nombre de la propiedad")
            p = st.text_input("Precio USD")
            f = st.file_uploader("Fotos", accept_multiple_files=True)
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and t and f:
                    with st.spinner("Subiendo..."):
                        for ar in f:
                            with conn.open(f"gdrive://DB_Cortes_Inmo/{t}/{ar.name}", "wb") as fp:
                                fp.write(ar.getbuffer())
                        st.success(f"✅ ¡{t} publicado con éxito!")
                else:
                    st.error("Error: Revisá la conexión o faltan datos.")
else:
    st.title("🏠 Galería")
    st.info("Sincronizando con Drive...")
