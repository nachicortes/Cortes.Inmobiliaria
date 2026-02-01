import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="wide")

# --- ESTILOS PERSONALIZADOS (TUS COLORES DE AYER) ---
st.markdown("""
    <style>
    /* Estilo para los botones de contacto */
    .btn-contact {
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        display: block;
        margin-bottom: 12px;
        text-decoration: none;
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }
    .wa { background-color: #25D366; } /* Verde WhatsApp */
    .ig { background-color: #E4405F; } /* Rosa Instagram */
    .tk { background-color: #000000; } /* Negro TikTok */
    
    /* Ajuste de botones generales de Streamlit */
    div.stButton > button {
        background-color: #000000;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DRIVE ---
try:
    # Intentamos conectar usando los secrets configurados
    conn = st.connection("gdrive", type=FilesConnection)
except Exception as e:
    conn = None

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["🏠 Galería de Propiedades", "📂 Panel de Carga"])
    st.markdown("---")
    
    st.markdown("### Contacto")
    st.markdown(f'<a class="btn-contact wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-contact ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)
    st.markdown(f'<a class="btn-contact tk" href="https://www.tiktok.com/@cortes.inmobiliaria">TikTok</a>', unsafe_allow_html=True)

# --- LÓGICA DE PANTALLAS ---
if menu == "📂 Panel de Carga":
    st.title("📂 Cargar Nueva Propiedad")
    clave = st.text_input("Contraseña de seguridad:", type="password")
    
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("form_carga", clear_on_submit=True):
            titulo = st.text_input("Nombre de la propiedad (ej: Casa Valle Escondido)")
            precio = st.text_input("Precio USD")
            fotos = st.file_uploader("Fotos/Video", accept_multiple_files=True)
            
            if st.form_submit_button("🚀 PUBLICAR"):
                if conn and titulo and fotos:
                    with st.spinner("Subiendo archivos a Google Drive..."):
                        for f in fotos:
                            ruta = f"gdrive://DB_Cortes_Inmo/{titulo}/{f.name}"
                            with conn.open(ruta, "wb") as fp:
                                fp.write(f.getbuffer())
                        st.success(f"✅ ¡{titulo} se publicó con éxito!")
                else:
                    st.error("Error: Revisá la conexión de Drive o que hayas completado Título y Fotos.")
    elif clave:
        st.error("Contraseña incorrecta.")

else:
    st.title("🏠 Nuestras Propiedades")
    st.info("Sincronizando con Google Drive...")
