import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- ESTILOS PERSONALIZADOS (TUS COLORES) ---
st.markdown("""
    <style>
    .btn-contact {
        padding: 10px; border-radius: 8px; text-align: center;
        display: block; margin-bottom: 10px; text-decoration: none;
        color: white !important; font-weight: bold;
    }
    .wa { background-color: #25D366; } /* Verde WhatsApp */
    .ig { background-color: #E4405F; } /* Rosa Instagram */
    .tk { background-color: #000000; } /* Negro TikTok */
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DRIVE ---
# Esta es la forma correcta de llamar a la conexión según tus Secrets
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception:
    conn = None

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🏠 Galería", "📂 Panel de Carga"])
    st.markdown("---")
    st.markdown(f'<a class="btn-contact wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-contact ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-contact tk" href="https://www.tiktok.com/@cortes.inmobiliaria">TikTok</a>', unsafe_allow_html=True)

# --- LÓGICA DE PANTALLAS ---
if menu == "📂 Panel de Carga":
    st.title("📂 Cargar Propiedad")
    clave = st.text_input("Contraseña:", type="password")
    
    if clave == "cortes2026":
        with st.form("form_carga", clear_on_submit=True):
            titulo = st.text_input("Nombre de la propiedad")
            precio = st.text_input("Precio USD")
            fotos = st.file_uploader("Subir Fotos", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and titulo and fotos:
                    with st.spinner("Subiendo a Google Drive..."):
                        for f in fotos:
                            # Creamos la carpeta con el nombre de la propiedad
                            ruta = f"gdrive://DB_Cortes_Inmo/{titulo}/{f.name}"
                            with conn.open(ruta, "wb") as fp:
                                fp.write(f.getbuffer())
                        st.success(f"✅ ¡{titulo} se publicó con éxito!")
                else:
                    st.error("Error: La conexión con Drive falló. Verificá los Secrets.")
    elif clave:
        st.error("Contraseña incorrecta.")

else:
    st.title("🏠 Galería de Propiedades")
    st.info("Sincronizando con Google Drive...")
