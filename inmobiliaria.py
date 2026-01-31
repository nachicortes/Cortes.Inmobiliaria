import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="centered")

# Conexión nativa de Streamlit a Google Drive
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception:
    st.error("Error configurando la conexión. Revisá los Secrets.")

# --- INTERFAZ ---
st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", width=200)

tab1, tab2 = st.tabs(["🖼️ Catálogo", "🔐 Cargar"])

with tab1:
    st.title("Propiedades")
    st.info("Aquí aparecerán tus archivos subidos.")

with tab2:
    clave = st.text_input("Contraseña:", type="password")
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("subida_directa"):
            nombre_prop = st.text_input("Nombre de la propiedad")
            archivos = st.file_uploader("Fotos/Video", accept_multiple_files=True)
            if st.form_submit_button("🚀 SUBIR AHORA"):
                if archivos and nombre_prop:
                    for arc in archivos:
                        # Ruta en tu Drive: DB_Cortes_Inmo / NombrePropiedad / nombre_archivo
                        ruta_destino = f"gdrive://DB_Cortes_Inmo/{nombre_prop}/{arc.name}"
                        try:
                            with conn.open(ruta_destino, "wb") as f:
                                f.write(arc.getbuffer())
                            st.success(f"✅ Subido: {arc.name}")
                        except Exception as e:
                            st.error(f"❌ Error al subir {arc.name}: {e}")
