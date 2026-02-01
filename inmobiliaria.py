import streamlit as st
import os
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Cortes Inmobiliaria - Gestión", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #000000; color: white; }
    .btn-side { padding: 10px; border-radius: 8px; text-align: center; display: block; margin-bottom: 10px; text-decoration: none; color: white !important; font-weight: bold; }
    .wa { background-color: #25D366; } .ig { background-color: #E4405F; }
    </style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE BASE DE DATOS ---
DB_FILE = "db_inmuebles.csv"

def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=["Fecha", "Titulo", "Precio", "Descripcion"])
    try:
        # Forzamos la lectura de las columnas exactas para evitar el KeyError 'Titulo'
        return pd.read_csv(DB_FILE, usecols=["Fecha", "Titulo", "Precio", "Descripcion"])
    except:
        return pd.DataFrame(columns=["Fecha", "Titulo", "Precio", "Descripcion"])

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/nachicortes/cortes.inmobiliaria/main/logo.png", use_container_width=True)
    st.markdown("---")
    menu = st.radio("Ir a:", ["📂 Cargar Propiedad", "🖼️ Ver Portfolio"])
    st.markdown("---")
    st.markdown('<a class="btn-side wa" href="https://wa.me/5493513083986">WhatsApp</a>', unsafe_allow_html=True)
    st.markdown('<a class="btn-side ig" href="https://www.instagram.com/cortes.inmo/">Instagram</a>', unsafe_allow_html=True)

# --- PANEL DE CARGA ---
if menu == "📂 Cargar Propiedad":
    st.title("📂 Nueva Publicación")
    with st.form("form_v3", clear_on_submit=True):
        t = st.text_input("Nombre de la Propiedad")
        p = st.text_input("Precio USD")
        d = st.text_area("Descripción detallada")
        f = st.file_uploader("Fotos y Videos", type=['jpg','png','jpeg','mp4','mov'], accept_multiple_files=True)
        
        if st.form_submit_button("🚀 PUBLICAR EN PORTFOLIO"):
            if t and p and f:
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                # Guardamos solo el texto en el CSV para evitar errores de base de datos
                nuevo = pd.DataFrame([[fecha, t, p, d]], columns=["Fecha", "Titulo", "Precio", "Descripcion"])
                nuevo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                
                st.success(f"¡{t} guardada! Mirá la previsualización:")
                # Guardamos los archivos en la sesión para que se vean en el portfolio
                if 'temp_media' not in st.session_state: st.session_state['temp_media'] = {}
                st.session_state['temp_media'][t] = f
                
                # Mostrar en el momento
                cols = st.columns(2)
                for idx, file in enumerate(f):
                    with cols[idx % 2]:
                        if file.type.startswith('image'): st.image(file, use_container_width=True)
                        else: st.video(file)
            else:
                st.error("Faltan datos o archivos.")

# --- VISTA DE PORTFOLIO ---
else:
    st.title("🖼️ Mi Portfolio")
    df = load_data()
    
    if df.empty:
        st.info("No hay propiedades cargadas.")
    else:
        for i, row in df.iloc[::-1].iterrows():
            with st.expander(f"🏠 {row['Titulo']} - USD {row['Precio']}"):
                st.write(f"**Publicado:** {row['Fecha']}")
                st.write(f"**Descripción:** {row['Descripcion']}")
                
                # Intentar mostrar multimedia si está en la sesión actual
                if 'temp_media' in st.session_state and row['Titulo'] in st.session_state['temp_media']:
                    archivos = st.session_state['temp_media'][row['Titulo']]
                    cols = st.columns(3)
                    for idx, file in enumerate(archivos):
                        with cols[idx % 3]:
                            if file.type.startswith('image'): st.image(file)
                            else: st.video(file)
                else:
                    st.warning("⚠️ Las fotos se ven solo recién cargadas. Para guardarlas permanentes necesitamos conectarnos a una carpeta de Drive o GitHub.")
