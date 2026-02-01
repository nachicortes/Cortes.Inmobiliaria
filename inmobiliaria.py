import streamlit as st
import os
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Portfolio Cortes Inmo", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000000; color: white; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
DB_FILE = "db_inmuebles.csv"

# Función para limpiar/crear la base de datos si hay errores
def reset_db():
    df_empty = pd.DataFrame(columns=["Titulo", "Precio", "Archivos"])
    df_empty.to_csv(DB_FILE, index=False)

if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
    reset_db()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Gestión:", ["📂 Cargar al Portfolio", "🖼️ Ver Mis Propiedades"])
    st.markdown("---")
    st.markdown('<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA MULTIMEDIA ---
if menu == "📂 Cargar al Portfolio":
    st.title("📂 Administrar Mis Propiedades")
    with st.form("form_personal", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        # ACTIVADO: Carga de múltiples fotos y videos
        f = st.file_uploader("Subir Fotos y Videos", type=['jpg', 'png', 'jpeg', 'mp4', 'mov'], accept_multiple_files=True)
        
        if st.form_submit_button("✅ GUARDAR EN PORTFOLIO"):
            if t and p and f:
                cant = len(f)
                # Guardamos la cantidad de archivos para el registro
                nuevo = pd.DataFrame([[t, p, f"{cant} archivos"]], columns=["Titulo", "Precio", "Archivos"])
                nuevo.to_csv(DB_FILE, mode='a', header=False, index=False)
                st.success(f"¡{t} guardado con {cant} archivos con éxito!")
            else:
                st.warning("Completá Título, Precio y subí al menos un archivo.")

# --- VISTA DE PORTFOLIO (CORREGIDA) ---
else:
    st.title("🖼️ Mi Portfolio")
    try:
        # Leemos forzando los nombres de columna para evitar el KeyError
        df = pd.read_csv(DB_FILE, names=["Titulo", "Precio", "Archivos"], header=0)
        if not df.empty:
            for i, row in df.iterrows():
                with st.expander(f"🏠 {row['Titulo']} - USD {row['Precio']}"):
                    st.write(f"**Contenido cargado:** {row['Archivos']}")
        else:
            st.info("No hay propiedades cargadas.")
    except Exception:
        st.error("Error en el formato de la base de datos.")
        if st.button("Reiniciar Base de Datos"):
            reset_db()
            st.rerun()
