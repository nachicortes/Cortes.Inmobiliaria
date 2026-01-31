import streamlit as st
from st_files_connection import FilesConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria", layout="centered")

# 1. Iniciamos la conexión (Aquí estaba el error de nombre)
try:
    conn = st.connection("gdrive", type=FilesConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- INTERFAZ ---
st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", width=200)

tab1, tab2 = st.tabs(["🖼️ Catálogo", "🔐 Cargar"])

with tab1:
    st.title("Propiedades")
    st.info("Subí tu primera propiedad para verla aquí.")

with tab2:
    clave = st.text_input("Contraseña:", type="password")
    if clave == "cortes2026":
        st.success("Acceso concedido.")
        with st.form("subida_final", clear_on_submit=True):
            nombre_prop = st.text_input("Nombre de la propiedad (ej: Casa Valle Escondido)")
            archivos = st.file_uploader("Fotos/Video", accept_multiple_files=True)
            boton = st.form_submit_button("🚀 SUBIR AHORA")
            
            if boton:
                if archivos and nombre_prop:
                    for arc in archivos:
                        # Ruta: gdrive://NombreDeTuCarpetaEnDrive/NombrePropiedad/Archivo
                        ruta = f"gdrive://DB_Cortes_Inmo/{nombre_prop}/{arc.name}"
                        try:
                            # Usamos 'conn' que ahora sí está definido arriba
                            with conn.open(ruta, "wb") as f:
                                f.write(arc.getbuffer())
                            st.success(f"✅ ¡{arc.name} subido con éxito!")
                        except Exception as e:
                            st.error(f"Fallo al subir {arc.name}: {e}")
                else:
                    st.warning("Por favor, poné un nombre y elegí al menos una foto.")




